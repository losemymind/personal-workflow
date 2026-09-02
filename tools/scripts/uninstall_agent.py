"""Uninstall an agent installed by PersonalWorkflow (manifest-marked only)."""

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
    """Locate every client install of an agent (manifest-marked ones only).

    Agents may be installed as a directory (AGENT.md inside) or as a single
    .md file (manifest sits next to it, named <name>.manifest.json).
    """
    found = []
    if dest_override is not None:
        # mirror single-file naming convention from install_agent.py
        dir_candidate = dest_override / name
        file_candidate = dest_override / (name + ".md")
        if (dir_candidate / MANIFEST_NAME).exists():
            found.append(("custom", dir_candidate))
        elif (dest_override / (name + ".manifest.json")).exists():
            found.append(("custom", file_candidate))
        return found
    for client in clients or ("claude", "opencode", "codex", "deepseek"):
        paths = client_paths(client)
        base = paths["agents_dir"]
        dir_candidate = base / name
        file_candidate = base / (name + ".md")
        if (dir_candidate / MANIFEST_NAME).exists():
            found.append((client, dir_candidate))
        elif (base / (name + ".manifest.json")).exists():
            found.append((client, file_candidate))
    return found


def main() -> int:
    configure_utf8_output()
    parser = argparse.ArgumentParser(description="Uninstall an agent installed by PersonalWorkflow")
    parser.add_argument("name", help="Installed agent name")
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
        if dst.is_dir():
            shutil.rmtree(dst, ignore_errors=True)
            manifest_path = dst / MANIFEST_NAME
        else:
            dst.unlink(missing_ok=True)
            # remove the sidecar manifest if present
            sidecar = dst.parent / (dst.stem + ".manifest.json")
            sidecar.unlink(missing_ok=True)
            manifest_path = sidecar
        print(f"🗑️  [{client}] uninstalled: {dst}")
    print("ℹ️  Backup copies under ~/.personal-workflow/backups are kept (use rollback_agent.py to restore).")
    return 0


if __name__ == "__main__":
    sys.exit(main())