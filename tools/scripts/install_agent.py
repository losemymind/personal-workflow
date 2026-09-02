"""Install an agent from the PersonalWorkflow repo (agents/ or any source dir) to an LLM client.

Part of PersonalWorkflow tools (manifest-driven lifecycle). See tools/docs/lifecycle.md.

Usage:
    python tools/scripts/install_agent.py [--client <claude|opencode|codex|deepseek>] <agent-dir> [--dest <override>]
    python tools/scripts/install_agent.py <agent-dir>        # auto-detect installed clients

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
    copy_agent,
    detect_client_dirs,
    installed_clients,
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


def agent_version(src: Path) -> str:
    """Read the `version` field from AGENT.md frontmatter (source file or dir)."""
    file = (src / "AGENT.md") if src.is_dir() else src
    if file.exists():
        import re

        content = file.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^version:\s*[\"']?([0-9]+(?:\.[0-9]+){0,2})[\"']?", content, re.MULTILINE)
        if m:
            return m.group(1)
    return "0.1.0"


def manifest_for_agent(agent_dir: Path, name: str) -> dict:
    return {
        "name": name,
        "version": agent_version(agent_dir),
        "source": str(agent_dir),
        "installed_at": datetime.now().isoformat(timespec="seconds"),
    }


def install_one(client: str, src: Path, dest_override: Path | None = None) -> Path:
    paths = client_install_dir(client, "agent", dest_override)
    paths.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        dst = paths / src.name
        if dst.exists():
            raise FileExistsError(f"{dst} already exists. Uninstall first, or use an explicit --dest.")
        copy_agent(src, dst)
        manifest = manifest_for_agent(src, src.name)
        save_manifest(dst / MANIFEST_NAME, manifest)
    else:
        dst = paths / src.name
        if dst.exists():
            raise FileExistsError(f"{dst} already exists. Uninstall first.")
        copy_agent(src, dst)
        manifest = manifest_for_agent(src, src.stem)
        # single-file agents use a sidecar manifest next to the file
        save_manifest(dst.with_suffix(".manifest.json"), manifest)
    print(f"✅ [{client}] installed agent {src.name} -> {dst}")
    return dst


def main() -> int:
    configure_utf8_output()
    parser = argparse.ArgumentParser(description="Install an agent to LLM clients")
    parser.add_argument("source", help="Agent file (*.md) or agent directory to install")
    parser.add_argument("--client", choices=CLIENTS + ("auto",), default="auto", help="Target client (default: auto-detect)")
    parser.add_argument("--dest", default=None, help="Override destination base dir")
    parser.add_argument("--dry-run", action="store_true", help="Only resolve and print targets")
    args = parser.parse_args()

    src = Path(args.source)
    if not src.exists():
        print(f"❌ Source not found: {src}")
        return 1
    is_valid = src.is_dir() and (src / "AGENT.md").exists() or (src.is_file() and src.name.endswith(".md"))
    if not is_valid:
        print("❌ Not an agent definition: expected AGENT.md in a dir, or a *.md file")
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
            p = client_install_dir(c, "agent", dest_override)
            print(f"🔎 [{c}] would install to: {p}")
        return 0

    installed = []
    for c in clients:
        installed.append(install_one(c, src, dest_override))
    if installed:
        print(f"🎉 Installed agent '{src.name}' to {len(installed)} client(s). Restart the client to load it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())