r"""Client path matrix for supported LLM clients (claude / opencode / codex / deepseek-harness).

Single source of truth for install locations, shared by install/update/uninstall/rollback
scripts and referenced from tools/docs/lifecycle.md.

Path resolution rules:
  - User-level dirs resolve from HOME (%USERPROFILE% on Windows, ~ elsewhere).
  - Config root is ~/.config on every platform (honoring XDG_CONFIG_HOME when set).
    On Windows that is %USERPROFILE%\.config, NOT %APPDATA%: opencode loads skills
    from %USERPROFILE%\.config\opencode\skills and ignores %APPDATA%\opencode.
  - Install scopes: 'global' (user-level) and 'workspace' (project-level, at the git
    worktree root). Clients scan project skill dirs upward from cwd to the repo root,
    so workspace installs must target the root itself.
  - Codex skills live in ~/.agents/skills (USER scope) and <repo>/.agents/skills (REPO
    scope) per official docs; ~/.codex/skills is Codex's SYSTEM domain, do not write there.
  - DeepSeek Harness paths are version-dependent; we expose best-effort guesses and
    always allow an explicit override via --dest / DEEPSEEK_HARNESS_ROOT env var.
"""

import os
import shutil
import sys
from pathlib import Path

CLIENTS = ("claude", "opencode", "codex", "deepseek")
SCOPES = ("global", "workspace")

# ---------------------------------------------------------------------------
# Base directories
# ---------------------------------------------------------------------------


def home_dir() -> Path:
    if sys.platform == "win32":
        return Path(os.environ.get("USERPROFILE", Path.home()))
    return Path.home()


def config_dir() -> Path:
    """Per-client user-level config root (~/.config on every platform).

    opencode resolves its config (and skills/agent dirs) from ~/.config/opencode
    even on Windows, so do NOT map to %APPDATA%. XDG_CONFIG_HOME overrides when set.
    """
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg)
    return home_dir() / ".config"


# ---------------------------------------------------------------------------
# Paths per client
# ---------------------------------------------------------------------------


def client_paths(client: str) -> dict:
    """Return {skills_dir, agents_dir, note} for a client (user-level default)."""
    h = home_dir()
    c = config_dir()
    client = client.lower()
    if client == "claude":
        return {
            "skills_dir": h / ".claude" / "skills",
            "agents_dir": h / ".claude" / "agents",
            "config_files": [h / ".claude" / "settings.json"],
            "note": "User-level: ~/.claude/skills/<name>/; project-level: .claude/skills/",
        }
    if client == "opencode":
        return {
            "skills_dir": c / "opencode" / "skills",
            "agents_dir": c / "opencode" / "agent",
            "config_files": [c / "opencode" / "opencode.json"],
            "note": "User-level: ~/.config/opencode/skills/<name>/; project-level: .opencode/skills/ or skills.paths in opencode.json",
        }
    if client == "codex":
        return {
            "skills_dir": h / ".agents" / "skills",
            "agents_dir": h / ".codex" / "agents",
            "config_files": [h / ".codex" / "config.toml"],
            "note": "Codex USER scope: ~/.agents/skills/<name>/ (official docs). "
            "~/.codex/skills is Codex's SYSTEM domain (bundled skills), never install there. "
            "Subagent dir has no official convention (best-effort).",
        }
    if client == "deepseek":
        # Version-dependent; best-effort + env override.
        override = os.environ.get("DEEPSEEK_HARNESS_ROOT")
        base = Path(override) if override else (c / "deepseek-harness")
        return {
            "skills_dir": base / "skills",
            "agents_dir": base / "agents",
            "config_files": [base / "config.json", base / "harness.json"],
            "note": "DeepSeek Harness paths vary by version; DEEPSEEK_HARNESS_ROOT can override. Verify against official docs.",
        }
    raise ValueError(f"Unknown client: {client}. Valid: {', '.join(CLIENTS)}")


def client_install_dir(client: str, kind: str, base_dir: Path | None = None) -> Path:
    """Resolve the install directory for a client+kind (+ optional override)."""
    paths = client_paths(client)
    key = "skills_dir" if kind == "skill" else "agents_dir"
    if base_dir is not None:
        return Path(base_dir)
    return paths[key]


def find_project_root(start: Path | None = None) -> Path | None:
    """Walk up from start (default cwd) to the git worktree root (.git marker).

    Returns None when no git root exists above start. claude/opencode/codex scan
    project-level skill dirs upward from cwd to the repo root, so workspace-scope
    installs must target the root itself — a subdir would be missed by the scan.
    """
    current = (start or Path.cwd()).resolve()
    while True:
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def client_scope_paths(client: str, scope: str, project_root: Path | None = None) -> dict:
    """Return {skills_dir, agents_dir, note} for a client and install scope.

    scope='global'    -> user-level dirs (identical to client_paths()).
    scope='workspace' -> project-level dirs under project_root (required).
    """
    scope = scope.lower()
    if scope not in SCOPES:
        raise ValueError(f"Unknown scope: {scope}. Valid: {', '.join(SCOPES)}")
    if scope == "global":
        return client_paths(client)
    if project_root is None:
        raise ValueError("workspace scope requires project_root (the git worktree root)")
    root = Path(project_root)
    client = client.lower()
    if client == "claude":
        return {
            "skills_dir": root / ".claude" / "skills",
            "agents_dir": root / ".claude" / "agents",
            "note": "Project-level: <project>/.claude/skills/<name>/",
        }
    if client == "opencode":
        return {
            "skills_dir": root / ".opencode" / "skills",
            "agents_dir": root / ".opencode" / "agent",
            "note": "Project-level: <project>/.opencode/skills/<name>/ (or skills.paths in opencode.json)",
        }
    if client == "codex":
        return {
            "skills_dir": root / ".agents" / "skills",
            "agents_dir": root / ".codex" / "agents",
            "note": "Project-level: <repo>/.agents/skills/<name>/ (Codex REPO scope)",
        }
    if client == "deepseek":
        return {
            "skills_dir": root / ".deepseek" / "skills",
            "agents_dir": root / ".deepseek" / "agents",
            "note": "Project-level is best-effort; DeepSeek Harness has no official convention.",
        }
    raise ValueError(f"Unknown client: {client}. Valid: {', '.join(CLIENTS)}")


def client_scope_install_dir(
    client: str,
    kind: str,
    scope: str,
    project_root: Path | None = None,
    base_dir: Path | None = None,
) -> Path:
    """Resolve the install dir for client+kind+scope (+ optional --dest override)."""
    if base_dir is not None:
        return Path(base_dir)
    paths = client_scope_paths(client, scope, project_root)
    return paths["skills_dir"] if kind == "skill" else paths["agents_dir"]


# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------


def detect_client_dirs(client: str) -> list[Path]:
    """Return existing install dirs (user-level first, then project-level)."""
    paths = client_paths(client)
    dirs = [paths["skills_dir"], paths["agents_dir"]]
    project = Path.cwd()
    project_dirs = {
        "claude": [project / ".claude" / "skills", project / ".claude" / "agents"],
        "opencode": [project / ".opencode" / "skills", project / ".opencode" / "agent"],
        "codex": [project / ".agents" / "skills", project / ".codex" / "agents"],
        "deepseek": [project / ".deepseek" / "skills", project / ".deepseek" / "agents"],
    }
    dirs.extend(project_dirs.get(client.lower(), []))
    return [d for d in dirs if d.is_dir()]


def installed_clients() -> list[str]:
    """Detect which clients appear installed (any of their dirs/files exist)."""
    h = home_dir()
    base_dirs = {"claude": h / ".claude", "codex": h / ".codex"}
    found = []
    for client in CLIENTS:
        paths = client_paths(client)
        exists = any(
            p.exists()
            for p in [
                paths["skills_dir"],
                paths["agents_dir"],
                *paths["config_files"],
            ]
        )
        if not exists:
            base = base_dirs.get(client)
            exists = base is not None and base.is_dir()
        if exists:
            found.append(client)
        elif client == "deepseek" and os.environ.get("DEEPSEEK_HARNESS_ROOT"):
            found.append(client)
    return found if found else []


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

# Cache/bytecode noise that must not ship into client install dirs.
COPY_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")


def copy_skill_dir(src: Path, dst: Path) -> None:
    """Copy a skill directory (SKILL.md + optional subdirs) to dst, replacing it."""
    if not (src / "SKILL.md").exists():
        raise FileNotFoundError(f"{src} is not a skill directory (no SKILL.md)")
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=COPY_IGNORE)


def copy_agent(src: Path, dst: Path) -> None:
    """Copy an agent definition (single AGENT.md or a directory) to dst."""
    if src.is_dir() and (src / "AGENT.md").exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=COPY_IGNORE)
    elif src.is_file() and src.name.endswith(".md"):
        if dst.exists():
            dst.unlink()
        shutil.copy2(src, dst)
        if dst.suffix == "" or not dst.suffix:
            dst.rename(dst.with_suffix(".md"))
    else:
        raise FileNotFoundError(f"{src} is not an agent definition (AGENT.md or *.md)")


def read_version(skill_dir: Path, default: str = "0.1.0") -> str:
    """Read the `version` field from a skill's frontmatter (or its dir if absent)."""
    skill_file = skill_dir / "SKILL.md" if skill_dir.is_dir() else skill_dir
    if skill_dir.is_dir() and skill_file.exists():
        content = skill_file.read_text(encoding="utf-8", errors="replace")
        import re

        m = re.search(r"^version:\s*[\"']?([0-9]+(?:\.[0-9]+){0,2})[\"']?", content, re.MULTILINE)
        if m:
            return m.group(1)
    return default