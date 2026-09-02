"""Roll back an installed agent to a previous version kept in ~/.personal-workflow/backups.

Part of PersonalWorkflow tools (manifest-driven lifecycle). See tools/docs/lifecycle.md.

Usage:
    python tools/scripts/rollback_agent.py <agent-name> [--version 0.1.0] [--client X] [--dest Y]

Exit code 0 = rolled back for all target clients.
"""

import argparse
import io
import json
import shutil
import sys
from pathlib import Path

from client_paths import client_paths

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


def backups_root() -> Path:
    return Path.home() / ".personal-workflow" / "backups"


def load_manifest(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_manifest(path: Path, manifest: dict) -> None:
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def manifest_path_for(dst: Path) -> Path:
    if dst.is_dir():
        return dst / MANIFEST_NAME
    return dst.with_suffix(".manifest.json")


def find_installed(name: str, clients=None, dest_override: Path | None = None) -> list[tuple[str, Path]]:
    found = []
    if dest_override is not None:
        dir_candidate = dest_override / name
        file_candidate = dest_override / (name + ".md")
        if (dir_candidate / MANIFEST_NAME).exists():
            found.append(("custom", dir_candidate))
        elif file_candidate.with_suffix(".manifest.json").exists():
            found.append(("custom", file_candidate))
        return found
    for client in clients or ("claude", "opencode", "codex", "deepseek"):
        base = client_paths(client)["agents_dir"]
        dir_candidate = base / name
        file_candidate = base / (name + ".md")
        if (dir_candidate / MANIFEST_NAME).exists():
            found.append((client, dir_candidate))
        elif file_candidate.with_suffix(".manifest.json").exists():
            found.append((client, file_candidate))
    return found


def main() -> int:
    configure_utf8_output()
    parser = argparse.ArgumentParser(description="Roll back an installed agent to a previous backup")
    parser.add_argument("name", help="Installed agent name")
    parser.add_argument("--version", default=None, help="Target backup version (default: latest available)")
    parser.add_argument("--client", default=None, help="Only roll back for this client (default: all detected)")
    parser.add_argument("--dest", default=None, help="Override install dir (must match install --dest if used)")
    args = parser.parse_args()

    base = backups_root() / args.name
    if not base.is_dir():
        print(f"❌ No backups for '{args.name}' under {base}")
        return 1

    versions = sorted(p.name for p in base.iterdir() if p.is_dir())
    if not versions:
        print(f"❌ No backup versions found under {base}")
        return 1

    target = args.version if args.version else versions[-1]
    backup_dir = base / target
    if not backup_dir.is_dir():
        print(f"❌ No backup version '{target}'. Available: {', '.join(versions)}")
        return 1

    clients = [args.client] if args.client else ("claude", "opencode", "codex", "deepseek")
    dest_override = Path(args.dest) if args.dest else None
    targets = find_installed(args.name, clients=clients, dest_override=dest_override)
    if not targets:
        print(f"❌ No manifest-marked install of '{args.name}' found. Install it first, then roll back.")
        return 1

    for client, dst in targets:
        if dst.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(backup_dir, dst)
            manifest_path = dst / MANIFEST_NAME
        else:
            if dst.exists():
                dst.unlink()
            shutil.copy2(backup_dir / dst.name, dst)
            manifest_path = dst.with_suffix(".manifest.json")
            # restore sidecar manifest from backup if present
            if (backup_dir / MANIFEST_NAME).exists():
                save_manifest(manifest_path, load_manifest(backup_dir / MANIFEST_NAME))
        manifest = load_manifest(manifest_path)
        manifest["version"] = target
        save_manifest(manifest_path, manifest)
        print(f"↩️  [{client}] rolled back {args.name} -> v{target}")
    print("🎉 Rollback done. Restart the client to load the restored version.")
    return 0


if __name__ == "__main__":
    sys.exit(main())