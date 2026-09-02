"""Install a skill from the PersonalWorkflow repo (skills/ or any source dir) to an LLM client.

Part of PersonalWorkflow tools (manifest-driven lifecycle). See tools/docs/lifecycle.md.

Usage:
    python tools/scripts/install_skill.py [--client <claude|opencode|codex|deepseek>] <skills-dir> [--dest <override>]
    python tools/scripts/install_skill.py <skills-dir>        # auto-detect installed clients
    python tools/scripts/install_skill.py <skills-dir> --client opencode --into skills        # --into: skills|agents

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
    client_install_dir,
    copy_skill_dir,
    detect_client_dirs,
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


def write_manifest_entry(skills_dir: Path, name: str) -> None:
    """Append/update the manifest entry for one installed skill (manifest lives inside each installed dir)."""
    entry = {
        "name": name,
        "version": read_version(skills_dir),
        "source": str(skills_dir),
        "installed_at": datetime.now().isoformat(timespec="seconds"),
    }
    manifest_path = skills_dir / MANIFEST_NAME
    manifest = load_manifest(manifest_path)
    manifest.update({"pw_installed": True, **entry})
    save_manifest(manifest_path, manifest)


def install_one(client: str, src: Path, dest_override: Path | None = None) -> Path:
    paths = client_install_dir(client, "skill", dest_override)
    paths.mkdir(parents=True, exist_ok=True)
    dst = paths / src.name
    if dst.exists():
        raise FileExistsError(
            f"{dst} already exists. Use update_skill.py to upgrade, or uninstall first."
        )
    copy_skill_dir(src, dst)
    write_manifest_entry(dst, src.name)
    print(f"✅ [{client}] installed {src.name} -> {dst}")
    return dst


def main() -> int:
    configure_utf8_output()
    parser = argparse.ArgumentParser(description="Install a skill to LLM clients")
    parser.add_argument("source", help="Skill directory to install (must contain SKILL.md)")
    parser.add_argument("--client", choices=CLIENTS + ("auto",), default="auto", help="Target client (default: auto-detect)")
    parser.add_argument("--dest", default=None, help="Override destination base dir")
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
    if args.dry_run:
        for c in clients:
            p = client_install_dir(c, "skill", dest_override)
            print(f"🔎 [{c}] would install to: {p / src.name if not dest_override else p}")
        return 0

    installed = []
    for c in clients:
        installed.append(install_one(c, src, dest_override))
    if installed:
        print(f"🎉 Installed '{src.name}' to {len(installed)} client(s). Restart the client to load it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())