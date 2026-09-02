"""Build a searchable SQLite index of the agentic-awesome-skills upstream catalog.

Part of the skill-creator skill. See references/skill-index.md.

Data source: upstream's own skills_index.json (official metadata, fast & authoritative),
plus a local directory scan to enrich structure info (body lines, subdirs, file count).

Usage:
    python skill-creator/scripts/build_index.py           # download tarball + rebuild
    python skill-creator/scripts/build_index.py --keep    # keep downloaded tarball
    python skill-creator/scripts/build_index.py --no-dl   # use repo root (local checkout)

Exit code 0 = success.
"""

import argparse
import io
import json
import os
import re
import sqlite3
import sys
import tarfile
import tempfile
import urllib.request
from datetime import datetime
from pathlib import Path

UPSTREAM_URL = "https://github.com/sickn33/agentic-awesome-skills"
TARBALL_URL = UPSTREAM_URL + "/archive/refs/heads/main.tar.gz"
SCRIPT_DIR = Path(__file__).resolve().parent
INDEX_DIR = SCRIPT_DIR.parent / "indexes"
DB_PATH = INDEX_DIR / "upstream.db"
INDEX_VERSION = 2


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
            setattr(
                sys,
                stream_name,
                io.TextIOWrapper(buffer, encoding="utf-8", errors="backslashreplace"),
            )


def download_tarball(dest: Path) -> Path:
    print(f"⬇️  Downloading upstream tarball: {TARBALL_URL}")
    tmp = dest / "upstream.tgz"
    urllib.request.urlretrieve(TARBALL_URL, tmp)
    size_mb = tmp.stat().st_size / (1024 * 1024)
    print(f"✅ Downloaded {size_mb:.1f} MB -> {tmp}")
    return tmp


def unpack_tarball(tar_path: Path, dest: Path) -> Path:
    print(f"📦 Unpacking tarball -> {dest}")
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(dest, filter="data")
    tops = [p for p in dest.iterdir() if p.is_dir()]
    return tops[0] if tops else dest


def load_official_index(repo_root: Path) -> list[dict]:
    """Read upstream's own skills_index.json (fallback: scan SKILL.md files)."""
    f = repo_root / "skills_index.json"
    if f.exists():
        data = json.loads(f.read_text(encoding="utf-8"))
        print(f"🗂️  Using official skills_index.json ({len(data)} entries)")
        return data
    print("ℹ️  skills_index.json not found — will fall back to directory scan")
    return []


def enrich_structure(repo_root: Path, entry: dict) -> dict:
    """Scan the skill dir to add structure info (body lines, subdirs, file count, flags)."""
    rel = entry.get("path", "").removesuffix("/")
    skill_dir = repo_root / rel
    result = {
        "has_script": 0,
        "has_references": 0,
        "has_examples": 0,
        "has_templates": 0,
        "body_lines": 0,
        "file_count": 0,
        "subdirs": "",
    }
    if not skill_dir.is_dir():
        return result
    try:
        content = (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="replace")
        result["body_lines"] = content.count("\n") + 1
    except (OSError, FileNotFoundError):
        result["body_lines"] = 0
    subdirs = [d for d in os.listdir(skill_dir) if (skill_dir / d).is_dir() and not d.startswith(".")]
    result["subdirs"] = ",".join(subdirs)
    result["has_script"] = int("scripts" in subdirs)
    result["has_references"] = int("references" in subdirs)
    result["has_examples"] = int("examples" in subdirs)
    result["has_templates"] = int("templates" in subdirs)
    result["file_count"] = sum(
        1 for _, _, fs in os.walk(skill_dir) for f in fs if not f.startswith(".")
    )
    return result


def build_db(entries: list[dict], repo_root: Path, db_path: Path) -> int:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE skills (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            description TEXT,
            category TEXT,
            risk TEXT,
            source TEXT,
            date_added TEXT,
            author TEXT,
            tags TEXT,
            tools TEXT,
            client_targets TEXT,
            has_script INTEGER DEFAULT 0,
            has_references INTEGER DEFAULT 0,
            has_examples INTEGER DEFAULT 0,
            has_templates INTEGER DEFAULT 0,
            body_lines INTEGER DEFAULT 0,
            file_count INTEGER DEFAULT 0,
            subdirs TEXT
        )
        """
    )
    cur.execute(
        "CREATE VIRTUAL TABLE skills_fts USING fts5(name, description, category, tags)"
    )
    count = 0
    for e in entries:
        tags = e.get("tags") or []
        plugin = e.get("plugin") or {}
        targets = plugin.get("targets") or {}
        tools = json.dumps(list(targets.keys()), ensure_ascii=False) if targets else None
        st = enrich_structure(repo_root, e)
        cur.execute(
            """
            INSERT INTO skills
            (name, path, description, category, risk, source, date_added, author,
             tags, tools, client_targets, has_script, has_references, has_examples,
             has_templates, body_lines, file_count, subdirs)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                e.get("name") or e.get("id"),
                e.get("path") or (e.get("id") and "skills/" + e["id"]),
                e.get("description"),
                e.get("category"),
                e.get("risk"),
                e.get("source"),
                e.get("date_added"),
                e.get("author"),
                json.dumps(tags, ensure_ascii=False) if tags else None,
                tools,
                json.dumps(targets, ensure_ascii=False) if targets else None,
                st["has_script"],
                st["has_references"],
                st["has_examples"],
                st["has_templates"],
                st["body_lines"],
                st["file_count"],
                st["subdirs"],
            ),
        )
        rowid = cur.lastrowid
        cur.execute(
            "INSERT INTO skills_fts(rowid, name, description, category, tags) VALUES (?,?,?,?,?)",
            (
                rowid,
                e.get("name") or e.get("id"),
                e.get("description") or "",
                e.get("category") or "",
                " ".join(tags) if tags else "",
            ),
        )
        count += 1
    cur.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    cur.execute("INSERT INTO meta VALUES ('version', ?)", (str(INDEX_VERSION),))
    cur.execute("INSERT INTO meta VALUES ('source_repo', ?)", (UPSTREAM_URL,))
    cur.execute("INSERT INTO meta VALUES ('built_at', ?)", (datetime.now().isoformat(timespec="seconds"),))
    cur.execute("INSERT INTO meta VALUES ('skill_count', ?)", (str(count),))
    cur.execute("INSERT INTO meta VALUES ('data_source', 'official skills_index.json + dir scan')")
    conn.commit()
    conn.close()
    return count


def main() -> int:
    configure_utf8_output()
    parser = argparse.ArgumentParser(description="Build upstream skills SQLite index")
    parser.add_argument("--keep", action="store_true", help="Keep the downloaded tarball")
    parser.add_argument("--no-dl", action="store_true", help="Use repo root (local checkout) instead of downloading")
    parser.add_argument("--from-extracted", default=None, help="Build from an already-extracted upstream checkout dir")
    args = parser.parse_args()

    tmp = Path(tempfile.gettempdir()) / "pw-upstream-index"
    tmp.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).resolve().parents[2]
    if args.from_extracted:
        repo_root = Path(args.from_extracted)
        print(f"🗂️  Using extracted checkout: {repo_root}")
        entries = load_official_index(repo_root)
        if not entries:
            print("❌ skills_index.json missing in that checkout; aborting.")
            return 1
    elif args.no_dl:
        print(f"🗂️  Using local checkout: {repo_root}")
        entries = load_official_index(repo_root)
        if not entries:
            print("❌ No skills_index.json found locally. Run without --no-dl to download.")
            return 1
    else:
        tar_path = download_tarball(tmp)
        try:
            top = unpack_tarball(tar_path, tmp / "unpack")
            entries = load_official_index(top)
            if not entries:
                print("❌ skills_index.json missing in tarball; aborting.")
                return 1
        except Exception as e:
            print(f"❌ Unpack failed: {e}")
            return 1
        repo_root = top

    print(f"🔍 Enriching structure for {len(entries)} skills (dir scan)...")
    count = build_db(entries, repo_root, DB_PATH)
    print(f"✅ Indexed {count} skills -> {DB_PATH}")

    if not args.from_extracted and not args.no_dl and not args.keep:
        for p in tmp.rglob("*"):
            if p.is_file():
                try:
                    p.unlink()
                except OSError:
                    pass
        for p in sorted(tmp.rglob("*"), key=lambda x: -len(x.parts)):
            if p.is_dir():
                try:
                    # tarball-unpacked dirs are often read-only on Windows
                    for child in p.rglob("*"):
                        if child.is_file():
                            try:
                                child.chmod(0o644)
                            except OSError:
                                pass
                    p.rmdir()
                except OSError:
                    pass
    return 0


if __name__ == "__main__":
    sys.exit(main())