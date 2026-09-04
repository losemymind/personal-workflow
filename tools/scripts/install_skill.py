"""Install a skill from the PersonalWorkflow repo (skills/ or any source dir) to an LLM client.

Part of PersonalWorkflow tools (manifest-driven lifecycle). See tools/docs/lifecycle.md.

Usage:
    python tools/scripts/install_skill.py [--client <claude|opencode|codex|deepseek>] <skills-dir> [--dest <override>]
    python tools/scripts/install_skill.py <skills-dir>        # auto-detect installed clients
    python tools/scripts/install_skill.py <skills-dir> --scope workspace   # project-level (git root)
    python tools/scripts/install_skill.py <skills-dir> --client opencode --into skills        # --into: skills|agents

Scope: 'global' installs to the user-level dir (all projects); 'workspace' installs to the
current git worktree root (project-level). When --scope is omitted (and no --dest override),
the installer asks interactively. See skill-creator/INSTALL.md for the full runbook.

Exit code 0 = installed for all target clients.
"""

import argparse
import io
import json
import sys
from datetime import datetime
from pathlib import Path

from client_paths import (
    CLIENTS,
    SCOPES,
    client_scope_install_dir,
    copy_skill_dir,
    detect_client_dirs,
    find_project_root,
    installed_clients,
    read_version,
)

MANIFEST_NAME = ".personal-workflow-manifest.json"


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


def load_manifest(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_manifest(path: Path, manifest: dict) -> None:
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def write_manifest_entry(skills_dir: Path, name: str, source: Path | None = None) -> None:
    """Append/update the manifest entry for one installed skill (manifest lives inside each installed dir).

    `source` records where the skill was installed FROM (the true source dir);
    when omitted it falls back to the install location itself.
    """
    entry = {
        "name": name,
        "version": read_version(skills_dir),
        "source": str(source if source is not None else skills_dir),
        "installed_at": datetime.now().isoformat(timespec="seconds"),
    }
    manifest_path = skills_dir / MANIFEST_NAME
    manifest = load_manifest(manifest_path)
    manifest.update({"pw_installed": True, **entry})
    save_manifest(manifest_path, manifest)


def install_one(
    client: str,
    src: Path,
    scope: str,
    project_root: Path | None = None,
    dest_override: Path | None = None,
) -> Path:
    paths = client_scope_install_dir(client, "skill", scope, project_root, dest_override)
    paths.mkdir(parents=True, exist_ok=True)
    dst = paths / src.name
    if dst.exists():
        raise FileExistsError(
            f"{dst} already exists. Use update_skill.py to upgrade, or uninstall first."
        )
    copy_skill_dir(src, dst)
    write_manifest_entry(dst, src.name, source=src)
    label = "dest" if dest_override else scope
    print(f"✅ [{client}|{label}] installed {src.name} -> {dst}")
    return dst


def prompt_scope() -> str:
    """Interactive scope choice (INSTALL.md step 0). Non-interactive stdin -> error."""
    print("请选择安装作用域：")
    print("  [1] global    — 全局（用户级，所有项目可用）")
    print("  [2] workspace — 目标工作区（项目级，装到当前 git 仓库根）")
    try:
        choice = input("输入 1 或 2 [默认 1]: ").lstrip("\ufeff").strip().lower()
    except EOFError:
        print("❌ 非交互环境无法询问，请显式指定 --scope global|workspace（或 --dest）。")
        sys.exit(1)
    if choice in ("", "1", "global", "g"):
        return "global"
    if choice in ("2", "workspace", "w", "project"):
        return "workspace"
    print(f"❌ 无法识别的选择: {choice!r}（应为 1/2 或 global/workspace）")
    sys.exit(1)


def main() -> int:
    configure_utf8_output()
    parser = argparse.ArgumentParser(description="Install a skill to LLM clients")
    parser.add_argument("source", help="Skill directory to install (must contain SKILL.md)")
    parser.add_argument("--client", choices=CLIENTS + ("auto",), default="auto", help="Target client (default: auto-detect)")
    parser.add_argument("--scope", choices=SCOPES, default=None, help="Install scope: global (user-level) or workspace (git root). Asked interactively when omitted.")
    parser.add_argument("--dest", default=None, help="Override destination base dir (takes precedence over --scope)")
    parser.add_argument("--dry-run", action="store_true", help="Only resolve and print targets")
    args = parser.parse_args()

    src = Path(args.source)
    if not (src / "SKILL.md").exists():
        print(f"❌ Not a skill directory (no SKILL.md): {src}")
        return 1

    if args.client == "auto":
        clients = installed_clients()
        if not clients:
            print("⚠️  No installed clients detected. Pass --client claude|opencode|codex|deepseek")
            return 1
    else:
        clients = [args.client]

    dest_override = Path(args.dest) if args.dest else None
    scope = args.scope
    if scope is None and dest_override is None:
        scope = prompt_scope()

    project_root = None
    if scope == "workspace" and dest_override is None:
        project_root = find_project_root()
        if project_root is None:
            print("❌ workspace 作用域需要处于 git 仓库内（向上未找到 .git）。")
            print("   请切换到目标仓库内运行，或改用 --scope global / --dest <目录>。")
            return 1
        print(f"📁 workspace 目标项目根: {project_root}")

    if args.dry_run:
        for c in clients:
            p = client_scope_install_dir(c, "skill", scope or "global", project_root, dest_override)
            print(f"🔎 [{c}|{('dest' if dest_override else scope or 'global')}] would install to: {p / src.name}")
        return 0

    installed = []
    for c in clients:
        installed.append(install_one(c, src, scope or "global", project_root, dest_override))
    if installed:
        print(f"🎉 Installed '{src.name}' to {len(installed)} client(s). Restart the client to load it.")
        print("📖 安装后验证与调用范式见: skill-creator/INSTALL.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())