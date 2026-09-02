"""Update an installed skill from the PersonalWorkflow repo (preserve old version backup)."""

import argparse
import io
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from client_paths import client_paths, read_version

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


def find_installed(name: str, clients=None, dest_override: Path | None = None) -> list[tuple[str, Path]]:
    """Locate every client install of a skill (manifest-marked ones only)."""
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
    parser = argparse.ArgumentParser(description="Update an installed skill (backup old version first)")
    parser.add_argument("name", help="Installed skill name")
    parser.add_argument("--source", required=True, help="New version source dir (skills/<name> or built dir)")
    parser.add_argument("--client", default=None, help="Only update for this client (default: all detected)")
    parser.add_argument("--dest", default=None, help="Override install dir (must match install --dest if used)")
    args = parser.parse_args()

    src = Path(args.source)
    if not (src / "SKILL.md").exists():
        print(f"❌ Source is not a skill dir: {src}")
        return 1
    new_version = read_version(src)
    print(f"🔍 New version: {new_version} (source {src})")

    if args.client:
        clients = [args.client]
    else:
        clients = ("claude", "opencode", "codex", "deepseek")
    dest_override = Path(args.dest) if args.dest else None
    targets = find_installed(args.name, clients=clients, dest_override=dest_override)
    if not targets:
        print(f"❌ No manifest-marked install of '{args.name}' found. Nothing to update.")
        return 1

    for client, dst in targets:
        manifest = load_manifest(dst / MANIFEST_NAME)
        old_version = manifest.get("version", "unknown")
        backup_dir = backups_root() / args.name / old_version
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        # copytree requires the destination to NOT exist (dirs_exist_ok=False),
        # so do not mkdir here; copytree creates parents itself.
        shutil.copytree(dst, backup_dir)
        print(f"💾 Backed up {dst} (v{old_version}) -> {backup_dir}")

        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        manifest["version"] = new_version
        manifest["source"] = str(src)
        manifest["updated_at"] = datetime.now().isoformat(timespec="seconds")
        save_manifest(dst / MANIFEST_NAME, manifest)
        print(f"✅ [{client}] updated {args.name} -> v{new_version}")
    print("🎉 Update done. Restart the client to load the new version.")
    return 0


if __name__ == "__main__":
    sys.exit(main())