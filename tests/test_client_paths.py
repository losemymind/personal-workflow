"""Tests for tools/scripts/client_paths.py (path matrix + install helpers)."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools" / "scripts"))

from client_paths import (  # noqa: E402
    CLIENTS,
    client_paths,
    installed_clients,
    read_version,
)


def test_all_clients_covered():
    assert set(CLIENTS) == {"claude", "opencode", "codex", "deepseek"}


def test_each_client_has_skills_and_agents_dirs(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    monkeypatch.delenv("DEEPSEEK_HARNESS_ROOT", raising=False)
    for c in CLIENTS:
        p = client_paths(c)
        assert p["skills_dir"].name in ("skills", "skills")
        assert p["agents_dir"].name in ("agent", "agents")
        assert "note" in p


def test_read_version_parses_frontmatter(tmp_path):
    d = tmp_path / "s"
    d.mkdir()
    (d / "SKILL.md").write_text(
        '---\nname: x\ndescription: "d"\nversion: "1.2.3"\n---\n# x\n',
        encoding="utf-8",
    )
    assert read_version(d) == "1.2.3"


def test_read_version_default_when_absent(tmp_path):
    d = tmp_path / "s"
    d.mkdir()
    (d / "SKILL.md").write_text(
        '---\nname: x\ndescription: "d"\n---\n# x\n',
        encoding="utf-8",
    )
    assert read_version(d) == "0.1.0"