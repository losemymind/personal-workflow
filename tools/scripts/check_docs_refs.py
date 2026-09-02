"""Case-sensitive path reference checker using git's index as authority.

Windows filesystem is case-insensitive, so git ls-files is the source of truth.
This script extracts backtick refs from .md files (repo-internal path style)
and verifies them against the git index case-sensitively.

Heuristics:
  - command examples are unwrapped to the first path-like token
    (e.g. `python tools/scripts/install_skill.py --client opencode <dir>` -> `tools/scripts/install_skill.py`)
  - directory-only refs (e.g. `tools/`) are accepted if any tracked file lives under them
  - refs with placeholders (<, >, *, ?, xxx, your-) are skipped
  - references inside fenced code blocks are skipped (illustrative examples)

Usage: python tools/scripts/check_docs_refs.py
"""

import os
import re
import subprocess
import sys
from pathlib import Path

def repo_root() -> Path:
    """Locate the git top level (robust regardless of this script's location)."""
    out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=Path(__file__).resolve().parent, text=True)
    return Path(out.strip())


REPO = repo_root()

KNOWN_DIRS = ("skill-creator", "agent-creator", "tools", "skills", "agents", "docs", "tests", "indexes")
PLACEHOLDER_MARKERS = ("<", ">", "*", "?", "…", "xxx", "your-", "TODO")


def git_files() -> set[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=REPO, text=True)
    return set(line.replace("/", "\\") for line in out.splitlines() if line)


def has_cjk(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def clean_fenced(content: str) -> str:
    return re.sub(r"```.*?```", "", content, flags=re.DOTALL)


def extract_path_token(cand: str) -> str:
    """Pull the repo-internal path token out of a possibly-command-line ref.

    `python tools/scripts/install_skill.py --client opencode <dir>` ->
    `tools/scripts/install_skill.py`
    """
    for token in cand.split():
        for d in KNOWN_DIRS:
            if token.startswith(d + "/") or token == d:
                return token
    return cand


def main() -> int:
    index = git_files()
    problems: list[tuple[Path, str]] = []

    for md in sorted(REPO.rglob("*.md")):
        rel = md.relative_to(REPO)
        if "examples" in rel.parts:
            continue
        content = clean_fenced(md.read_text(encoding="utf-8", errors="replace"))
        refs = set(re.findall(r"`([^`]+)`", content))
        for ref in sorted(refs):
            cand = ref.strip()
            if not cand or has_cjk(cand):
                continue
            if cand.startswith("~") or cand.startswith("$") or cand.startswith("{"):
                continue  # client-side path or env/config interpolation, not repo-internal
            if any(m in cand for m in PLACEHOLDER_MARKERS):
                continue
            token = extract_path_token(cand)
            if "." in token and "/" not in token:
                continue  # config key like `skills.paths`, not a repo path
            # token must START with a known repo dir (prefix match, not substring)
            if not any(token.startswith(d + "/") or token == d for d in KNOWN_DIRS):
                continue  # not repo-internal (client paths, field names, etc.)
            # evolutions/ records reference UPSTREAM repo paths (e.g. `skills/comprehensive-review-*`
            # inside sickn33's catalog). They are intentionally not local — do not flag them.
            if "evolutions" in rel.parts and token.startswith("skills/"):
                continue
            key = token.replace("/", "\\")
            # strip trailing separator so `tools/` -> `tools` (not `tools\`)
            bare = key.rstrip("\\")
            # resolve relative to the markdown file's own dir too (e.g. `indexes/upstream.db`
            # inside skill-creator/docs is `<repo>/skill-creator/indexes/upstream.db`)
            rel_md = md.parent.relative_to(REPO)
            local_probe = rel_md / Path(token.replace("/", os.sep))
            local_key = str(local_probe).replace("/", "\\")
            if bare in index or local_key in index:
                continue
            # directory-only ref (e.g. `tools/`): accept if any tracked file lives under it
            if any(f == bare or f.startswith(bare + "\\") for f in index):
                continue
            problems.append((rel, cand))

    if not problems:
        print("✅ 所有仓库内路径引用均与 git 索引精确匹配（大小写敏感）。")
        return 0
    print("❌ 与 git 索引不匹配的路径引用：\n")
    for rel, ref in problems:
        print(f"  {rel}\n    -> `{ref}`")
    return 1


if __name__ == "__main__":
    sys.exit(main())