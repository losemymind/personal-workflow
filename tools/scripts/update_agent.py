"""Update an installed agent from the PersonalWorkflow repo (preserve old version backup).

Part of PersonalWorkflow tools (manifest-driven lifecycle). See tools/docs/lifecycle.md.

Usage:
    python tools/scripts/update_agent.py <agent-name> --source <new-agent-dir-or-file> [--client X] [--dest Y]

Exit code 0 = updated for all target clients.
"""

import argparse
import io
import json
import re
import shutil
import sys
from datetime import datetime
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


def agent_version(src: Path) -> str:
    """Read the `version` field from AGENT.md frontmatter (source file or dir)."""
    file = (src / "AGENT.md") if src.is_dir() else src
    if file.exists():
        content = file.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^version:\s*[\"']?([0-9]+(?:\.[0-9]+){0,2})[\"']?", content, re.MULTILINE)
        if m:
            return m.group(1)
    return "0.1.0"


def manifest_path_for(dst: Path) -> Path:
    """Manifest location: inside dir installs, sidecar for single-file installs."""
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
    parser = argparse.ArgumentParser(description="Update an installed agent (backup old version first)")
    parser.add_argument("name", help="Installed agent name")
    parser.add_argument("--source", required=True, help="New version source dir (agents/<name> or *.md file)")
    parser.add_argument("--client", default=None, help="Only update for this client (default: all detected)")
    parser.add_argument("--dest", default=None, help="Override install dir (must match install --dest if used)")
    args = parser.parse_args()

    src = Path(args.source)
    is_valid = (src.is_dir() and (src / "AGENT.md").exists()) or (src.is_file() and src.name.endswith(".md"))
    if not is_valid:
        print(f"❌ Source is not an agent definition: {src}")
        return 1
    new_version = agent_version(src)
    print(f"🔍 New version: {new_version} (source {src})")

    clients = [args.client] if args.client else ("claude", "opencode", "codex", "deepseek")
    dest_override = Path(args.dest) if args.dest else None
    targets = find_installed(args.name, clients=clients, dest_override=dest_override)
    if not targets:
        print(f"❌ No manifest-marked install of '{args.name}' found. Nothing to update.")
        return 1

    for client, dst in targets:
        manifest = load_manifest(manifest_path_for(dst))
        old_version = manifest.get("version", "unknown")
        backup_dir = backups_root() / args.name / old_version
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        if dst.is_dir():
            shutil.copytree(dst, backup_dir)
        else:
            backup_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, backup_dir / dst.name)
            src_manifest = dst.with_suffix(".manifest.json")
            if src_manifest.exists():
                shutil.copy2(src_manifest, backup_dir / MANIFEST_NAME)
        print(f"💾 Backed up {dst} (v{old_version}) -> {backup_dir}")

        if dst.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            manifest_path = dst / MANIFEST_NAME
        else:
            if dst.exists():
                dst.unlink()
            shutil.copy2(src, dst)
            manifest_path = dst.with_suffix(".manifest.json")
        manifest["version"] = new_version
        manifest["source"] = str(src)
        manifest["updated_at"] = datetime.now().isoformat(timespec="seconds")
        save_manifest(manifest_path, manifest)
        print(f"✅ [{client}] updated {args.name} -> v{new_version}")
    print("🎉 Update done. Restart the client to load the new version.")
    return 0


if __name__ == "__main__":
    sys.exit(main())