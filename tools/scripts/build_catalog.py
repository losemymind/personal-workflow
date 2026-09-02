"""Generate a machine-readable capability catalog from skills//agents/ frontmatter.

Design: each SKILL.md / AGENT.md is the single source of truth; the generated
CATALOG.md files are derived artifacts that must never be edited by hand. AI
agents (claude/opencode/codex/deepseek) read these files to match a natural
language need to an installable local capability.

Usage:
    python tools/scripts/build_catalog.py                 # rewrite both CATALOG.md files
    python tools/scripts/build_catalog.py --check         # verify only (no writes)
    python tools/scripts/build_catalog.py --verbose       # log per-entry sources

Exit code 0 = ok. --check returns 1 if the on-disk catalog is stale.
"""

import argparse
import io
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
CATALOG_NAME = "CATALOG.md"

# Order matters: agents/README notes agents may be a single .md or a dir with AGENT.md.
# We only index the canonical form: a directory holding SKILL.md / AGENT.md.
KIND_FILES = {
    "skills": ("SKILL.md", "skill"),
    "agents": ("AGENT.md", "agent"),
}

DEFAULTS = {
    "category": "uncategorized",
    "risk": "unknown",
    "version": "-",
    "source": "-",
    "date_added": "-",
    "mode": "-",
    "install": "",
}

# Readme/catalog/resource files that are NOT capability entries.
EXCLUDED_NAMES = {"README.md", "CATALOG.md"}


def configure_utf8_output() -> None:
    if sys.platform != "win32":
        return
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
            continue
        except Exception:
            pass
        buffer = getattr(stream, "buffer", None)
        if buffer is not None:
            setattr(sys, stream_name, io.TextIOWrapper(buffer, encoding="utf-8", errors="backslashreplace"))


def parse_frontmatter(content: str) -> dict:
    """Minimal frontmatter parser: pulls the --- delimited YAML block into a dict.

    Line-based and dependency-free. Handles flat scalars, inline flow arrays
    ([a, b, c] kept verbatim as the string value) and ignores nested/indented
    structures (block mappings under a key) — the catalog only needs scalars.
    Returns {} if there is no well-formed frontmatter block.
    """
    m = re.match(r"^---\s*\n(.*?)\n?---(?:\s*\n|$)", content, re.DOTALL)
    if not m:
        return {}
    data: dict = {}
    for line in m.group(1).splitlines():
        # Skip blank/comment/indented (nested map elements / block list items).
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        if not key:
            continue
        val = val.strip()
        # Unwrap one level of quotes for scalars.
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        # Keep inline arrays verbatim (e.g. `[claude, opencode]`), drop empties.
        if val in ("", "null", "~"):
            val = ""
        data[key] = val
    return data


def first_when_to_use(content: str, head: list[str]) -> str:
    """Extract the first non-empty line after a 'when to use' heading (EN or 中文)."""
    for h in head:
        pat = re.compile(
            r"^##\s*" + re.escape(h) + r"\s*\n(.*?)(?=\n##\s|\Z)",
            re.DOTALL | re.MULTILINE,
        )
        m = pat.search(content)
        if not m:
            continue
        for line in m.group(1).splitlines():
            line = line.strip().lstrip("-• ")
            if line and not line.startswith(("```", "|")):
                return line[:160]
    return ""


def discover(root: Path, kind: str, entry_file: str, verbose: bool) -> list[dict]:
    """Scan a library dir (skills/ or agents/) and return per-entry data."""
    entries = []
    for sub in sorted(root.iterdir()):
        if not sub.is_dir() or sub.name.startswith(".") or sub.name in EXCLUDED_NAMES:
            continue
        fm_file = sub / entry_file
        if not fm_file.exists():
            if verbose:
                print(f"  · skip {sub.name}: no {entry_file}")
            continue
        content = fm_file.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(content)
        if not fm:
            if verbose:
                print(f"  · skip {sub.name}: no frontmatter in {entry_file}")
            continue
        install_target = f"{root.name}/{sub.name}" if root.name in ("skills", "agents") else f"{kind}/{sub.name}"
        entry = {
            "kind": kind,
            "name": fm.get("name") or sub.name,
            "dir": sub.name,
            "path": f"{root.name}/{sub.name}",
            "install": f"python tools/scripts/install_{'skill' if kind == 'skill' else 'agent'}.py {install_target}",
            "description": fm.get("description") or "",
            "tags": fm.get("tags") or "",
            "trigger": first_when_to_use(content, ["When to Use This Skill", "When to Use", "Use this skill when", "Use this skill when", "何时使用此技能", "何时使用", "When to activate this skill"])
            or "",
        }
        if kind == "skill":
            # Skill frontmatter schema: category/risk/source/date_added are real fields.
            entry["category"] = fm.get("category") or DEFAULTS["category"]
            entry["risk"] = fm.get("risk") or DEFAULTS["risk"]
            entry["version"] = fm.get("version") or DEFAULTS["version"]
            entry["source"] = fm.get("source") or DEFAULTS["source"]
            entry["date_added"] = fm.get("date_added") or DEFAULTS["date_added"]
        else:
            # Agent frontmatter schema: no category/source/date_added; mode + tags carry taxonomy.
            entry["mode"] = fm.get("mode") or DEFAULTS["mode"]
            entry["version"] = fm.get("version") or DEFAULTS["version"]
        entries.append(entry)
    return entries


def render_entry(e: dict) -> str:
    """Render a single catalog entry (heading anchor + table + prose)."""
    kind = e["kind"]
    if kind == "skill":
        rows = [
            ("category", e["category"]),
            ("risk", e["risk"]),
            ("version", e["version"]),
            ("source", e["source"]),
            ("date_added", e["date_added"]),
        ]
    else:
        rows = [("mode", e["mode"]), ("version", e["version"])]
    if e.get("tags"):
        rows.append(("tags", e["tags"]))
    rows.append(("install", f"`{e['install']}`"))

    table = "\n".join(f"| {k} | {v} |" for k, v in rows)
    head = f"## {e['name']}\n\n"
    body = f"{table}\n"
    if e["description"]:
        body += f"\n**用途**：{e['description']}\n"
    if e["trigger"]:
        body += f"\n**触发器**：{e['trigger']}\n"
    return head + body


def header(kind: str) -> str:
    repo = "skills" if kind == "skill" else "agents"
    label = "技能（Skill）" if kind == "skill" else "代理（Agent）"
    script = "python tools/scripts/build_catalog.py"
    return (
        f"# {repo}/ — 已验证{label}能力目录\n\n"
        f"> 本文件由 `{script}` 自动生成，**禁止手改**。事实源 = 各 `SKILL.md` / `AGENT.md` 的 frontmatter。\n"
        f"> 新增/删除能力后重跑 `{script}`；CI 以 `--check` 防止目录与目录不同步。\n"
        f"> 检索：让 LLM 读本文件匹配需求 → 命中即给出 `install` 命令，人类确认后执行。\n\n"
    )


def render_catalog(library: Path, kind: str, entry_file: str, verbose: bool) -> str:
    entries = discover(library, kind, entry_file, verbose)
    parts = [header(kind)]
    if not entries:
        parts.append("_（暂无能力）_\n")
    for e in entries:
        parts.append(render_entry(e))
    return "\n".join(parts) + "\n"


def main() -> int:
    configure_utf8_output()
    parser = argparse.ArgumentParser(description="Generate skills//agents// capability catalogs from frontmatter")
    parser.add_argument("--root", default=str(REPO_ROOT), help="Repo root to scan (default: derived from script location)")
    parser.add_argument("--check", action="store_true", help="Verify on-disk catalogs are up to date (no writes)")
    parser.add_argument("--verbose", action="store_true", help="Log per-entry data sources")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    changed = False
    for lib_name, (entry_file, kind) in KIND_FILES.items():
        library = root / lib_name
        catalog_path = library / CATALOG_NAME
        rendered = render_catalog(library, kind, entry_file, args.verbose)
        if args.check:
            if not catalog_path.exists():
                print(f"❌ [{lib_name}] missing {catalog_path.name}. Run build_catalog.py")
                changed = True
                continue
            if catalog_path.read_text(encoding="utf-8") != rendered:
                print(f"❌ [{lib_name}] catalog is stale. Run build_catalog.py")
                changed = True
            else:
                print(f"✅ [{lib_name}] catalog up to date")
        else:
            catalog_path.parent.mkdir(parents=True, exist_ok=True)
            catalog_path.write_text(rendered, encoding="utf-8")
            print(f"✅ [{lib_name}] wrote {catalog_path.relative_to(root)} ({len(discover(library, kind, entry_file, False))} entries)")

    return 1 if (args.check and changed) else 0


if __name__ == "__main__":
    sys.exit(main())
