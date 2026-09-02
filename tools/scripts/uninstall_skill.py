"""Uninstall a skill installed by PersonalWorkflow (manifest-marked only)."""

import argparse
import io
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


def find_installed(name: str, clients=None, dest_override: Path | None = None) -> list[tuple[str, Path]]:
    found = []
    if dest_override is not None:
        dst = dest_override / name
        if (dst / MANIFEST_NAME).exists():
            found.append(("custom", dst))
        return found
    for client in clients or ("claude", "opencode", "codex", "deepseek"):
        paths = client_paths(client)
        for kind in ("skills_dir", "agents_dir"):
            base = paths[kind]
            dst = base / name
            if (dst / MANIFEST_NAME).exists():
                found.append((client, dst))
    return found


def main() -> int:
    configure_utf8_output()
    parser = argparse.ArgumentParser(description="Uninstall a skill installed by PersonalWorkflow")
    parser.add_argument("name", help="Installed skill name")
    parser.add_argument("--client", default=None, help="Only uninstall for this client (default: all detected)")
    parser.add_argument("--dest", default=None, help="Override install dir (must match install --dest if used)")
    parser.add_argument("--keep-backup", action="store_true", help="Keep the backup copy (default: keep)")
    args = parser.parse_args()

    if args.client:
        clients = [args.client]
    else:
        clients = ("claude", "opencode", "codex", "deepseek")
    dest_override = Path(args.dest) if args.dest else None
    targets = find_installed(args.name, clients=clients, dest_override=dest_override)
    if not targets:
        print(f"❌ No manifest-marked install of '{args.name}' found (nothing to uninstall).")
        return 1

    for client, dst in targets:
        shutil.rmtree(dst, ignore_errors=True)
        print(f"🗑️  [{client}] uninstalled: {dst}")
    print("ℹ️  Backup copies under ~/.personal-workflow/backups are kept (use rollback_skill.py to restore).")
    return 0


if __name__ == "__main__":
    sys.exit(main())