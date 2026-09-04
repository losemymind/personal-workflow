"""Tests for tools/scripts/client_paths.py (path matrix + install helpers)."""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools" / "scripts"))

from client_paths import (  # noqa: E402
    CLIENTS,
    client_paths,
    client_scope_paths,
    config_dir,
    copy_skill_dir,
    find_project_root,
    installed_clients,
    read_version,
)


def test_all_clients_covered():
    assert set(CLIENTS) == {"claude", "opencode", "codex", "deepseek"}


def test_each_client_has_skills_and_agents_dirs(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    monkeypatch.delenv("DEEPSEEK_HARNESS_ROOT", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    for c in CLIENTS:
        p = client_paths(c)
        assert p["skills_dir"].name in ("skills", "skills")
        assert p["agents_dir"].name in ("agent", "agents")
        assert "note" in p


def test_opencode_config_root_ignores_appdata_on_windows(tmp_path, monkeypatch):
    """opencode loads skills from ~/.config/opencode even on Windows.

    Regression: installs to %APPDATA%\\opencode are silently ignored by the
    client (observed: pr-summarizer/code-reviewer never loaded from APPDATA).
    """
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setattr("client_paths.home_dir", lambda: tmp_path)
    p = client_paths("opencode")
    assert p["skills_dir"] == tmp_path / ".config" / "opencode" / "skills"
    assert p["agents_dir"] == tmp_path / ".config" / "opencode" / "agent"
    assert "appdata" not in str(p["skills_dir"])


def test_config_dir_respects_xdg_config_home(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    assert config_dir() == tmp_path / "xdg"


def test_copy_skill_dir_excludes_cache_noise(tmp_path):
    src = tmp_path / "src"
    (src / "scripts" / "__pycache__").mkdir(parents=True)
    (src / "scripts" / "__pycache__" / "mod.cpython-312.pyc").write_text("x", encoding="utf-8")
    (src / "scripts" / "keep.py").write_text("print(1)", encoding="utf-8")
    (src / "SKILL.md").write_text("---\nname: src\ndescription: d\n---\n# x\n", encoding="utf-8")
    dst = tmp_path / "dst"
    copy_skill_dir(src, dst)
    assert (dst / "SKILL.md").exists()
    assert (dst / "scripts" / "keep.py").exists()
    assert not (dst / "scripts" / "__pycache__").exists()


def test_codex_global_skills_targets_agents_dir(tmp_path, monkeypatch):
    """Codex USER scope is ~/.agents/skills; ~/.codex/skills is Codex's SYSTEM domain."""
    monkeypatch.setattr("client_paths.home_dir", lambda: tmp_path)
    p = client_paths("codex")
    assert p["skills_dir"] == tmp_path / ".agents" / "skills"
    assert ".codex" not in str(p["skills_dir"])


def test_workspace_scope_lands_at_project_root(tmp_path):
    claude = client_scope_paths("claude", "workspace", tmp_path)
    opencode = client_scope_paths("opencode", "workspace", tmp_path)
    codex = client_scope_paths("codex", "workspace", tmp_path)
    assert claude["skills_dir"] == tmp_path / ".claude" / "skills"
    assert opencode["skills_dir"] == tmp_path / ".opencode" / "skills"
    assert codex["skills_dir"] == tmp_path / ".agents" / "skills"


def test_workspace_scope_requires_project_root():
    with pytest.raises(ValueError):
        client_scope_paths("claude", "workspace")


def test_global_scope_equals_user_level(tmp_path, monkeypatch):
    monkeypatch.setattr("client_paths.home_dir", lambda: tmp_path)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    for c in CLIENTS:
        assert client_scope_paths(c, "global")["skills_dir"] == client_paths(c)["skills_dir"]


def test_find_project_root_walks_to_git(tmp_path):
    (tmp_path / ".git").mkdir()
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    assert find_project_root(nested) == tmp_path.resolve()


def test_install_workspace_scope_dry_run(tmp_path):
    """install_skill.py --scope workspace targets <git-root>/.<client>/skills."""
    (tmp_path / ".git").mkdir()
    (tmp_path / "SKILL.md").write_text(
        '---\nname: demo\ndescription: "d"\n---\n# demo\n', encoding="utf-8"
    )
    script = REPO_ROOT / "tools" / "scripts" / "install_skill.py"
    r = subprocess.run(
        [sys.executable, str(script), str(tmp_path), "--client", "claude",
         "--scope", "workspace", "--dry-run"],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    expected = tmp_path / ".claude" / "skills" / tmp_path.name
    assert str(expected) in r.stdout


def test_install_workspace_scope_outside_git_fails(tmp_path):
    """No git root above cwd -> workspace scope must abort, not install into a subdir."""
    (tmp_path / "SKILL.md").write_text(
        '---\nname: demo\ndescription: "d"\n---\n# demo\n', encoding="utf-8"
    )
    script = REPO_ROOT / "tools" / "scripts" / "install_skill.py"
    r = subprocess.run(
        [sys.executable, str(script), str(tmp_path), "--client", "claude",
         "--scope", "workspace"],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert r.returncode == 1, r.stdout + r.stderr
    assert "git" in (r.stdout + r.stderr)


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