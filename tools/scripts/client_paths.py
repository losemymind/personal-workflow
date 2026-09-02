"""Client path matrix for supported LLM clients (claude / opencode / codex / deepseek-harness).

Single source of truth for install locations, shared by install/update/uninstall/rollback
scripts and referenced from tools/docs/lifecycle.md.

Path resolution rules:
  - User-level dirs resolve from HOME (%USERPROFILE% on Windows, ~ elsewhere).
  - Project-level dirs resolve from the current working directory (cwd).
  - DeepSeek Harness paths are version-dependent; we expose best-effort guesses and
    always allow an explicit override via --dest / DEEPSEEK_HARNESS_ROOT env var.
"""

import os
import shutil
import sys
from pathlib import Path

CLIENTS = ("claude", "opencode", "codex", "deepseek")

# ---------------------------------------------------------------------------
# Base directories
# ---------------------------------------------------------------------------


def home_dir() -> Path:
    if sys.platform == "win32":
        return Path(os.environ.get("USERPROFILE", Path.home()))
    return Path.home()


def config_dir() -> Path:
    """Per-client user-level config root."""
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", home_dir() / ".config"))
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
            "skills_dir": h / ".codex" / "skills",
            "agents_dir": h / ".codex" / "agents",
            "config_files": [h / ".codex" / "config.toml"],
            "note": "Codex: ~/.codex/skills/<name>/; requires experimental skills feature",
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
        "codex": [project / ".codex" / "skills", project / ".codex" / "agents"],
        "deepseek": [project / ".deepseek" / "skills", project / ".deepseek" / "agents"],
    }
    dirs.extend(project_dirs.get(client.lower(), []))
    return [d for d in dirs if d.is_dir()]


def installed_clients() -> list[str]:
    """Detect which clients appear installed (any of their dirs/files exist)."""
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
        if exists:
            found.append(client)
        elif client == "deepseek" and os.environ.get("DEEPSEEK_HARNESS_ROOT"):
            found.append(client)
    return found if found else []


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------


def copy_skill_dir(src: Path, dst: Path) -> None:
    """Copy a skill directory (SKILL.md + optional subdirs) to dst, replacing it."""
    if not (src / "SKILL.md").exists():
        raise FileNotFoundError(f"{src} is not a skill directory (no SKILL.md)")
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def copy_agent(src: Path, dst: Path) -> None:
    """Copy an agent definition (single AGENT.md or a directory) to dst."""
    if src.is_dir() and (src / "AGENT.md").exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
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