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

    bases = set()
    for client, dst in targets:
        shutil.rmtree(dst, ignore_errors=True)
        bases.add(dst.parent)
        print(f"🗑️  [{client}] uninstalled: {dst}")
    for base in sorted(bases):
        try:
            base.rmdir()
            print(f"🧹 [{base}] removed empty dir left by uninstall")
        except OSError:
            pass
    print("ℹ️ 卸载不创建备份——需要时用 install_skill.py 重新安装（备份仅来自 update 升级，rollback 只能恢复那些版本）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())