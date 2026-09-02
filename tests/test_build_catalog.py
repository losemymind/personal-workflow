"""Tests for build_catalog.py: catalog generation, staleness detection, agent catalog exclusion."""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_CATALOG = REPO_ROOT / "tools" / "scripts" / "build_catalog.py"

# Sample frontmatters exercising parser edge cases (nested map, flow arrays, CJK desc).
SKILL_FM = """---
name: test-skill
description: "测试技能：做 X。当用户说「做 X」时使用。"
category: testing
risk: safe
source: self
version: "0.1.0"
date_added: "2026-09-02"
tags: [test, skill]
---

# test-skill

## 何时使用此技能

- 用户要求做 X 时使用
- 其他场景

## 示例

输入 → 输出
"""

# AGENT.md has NO category/source/date_added; nested permission map + flow arrays.
AGENT_FM = """---
name: test-agent
description: "测试代理：审查 Y。当用户要求审查时调用。"
mode: subagent
tools: [read, grep]
permission:
  edit: deny
version: "0.1.0"
tools_clients: [claude, opencode]
tags: [review, quality]
---

# test-agent

## 职责范围

**必须做：**
- 审查 Y

**拒绝做：**
- 不改代码

## 工具与权限

- 允许：read grep

## 协作协议

- 升级路径：交还用户

## 完成标准

- [ ] 输出

## 限制与边界

- 无
"""


def _write_fixture(lib: Path, name: str, entry_file: str, content: str) -> None:
    d = lib / name
    d.mkdir(parents=True, exist_ok=True)
    (d / entry_file).write_text(content, encoding="utf-8")


def run_script(*args: str, root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BUILD_CATALOG), "--root", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=root,
    )


@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    """A throwaway repo-like layout: skills/ + agents/ each with one entry."""
    skills = tmp_path / "skills"
    agents = tmp_path / "agents"
    skills.mkdir()
    agents.mkdir()
    _write_fixture(skills, "test-skill", "SKILL.md", SKILL_FM)
    _write_fixture(agents, "test-agent", "AGENT.md", AGENT_FM)
    return tmp_path


def test_generate_writes_both_catalogs(fake_repo):
    r = run_script(root=fake_repo)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "wrote skills\\CATALOG.md" in r.stdout.replace("/", "\\")
    assert (fake_repo / "skills" / "CATALOG.md").exists()
    assert (fake_repo / "agents" / "CATALOG.md").exists()


def test_check_pass_when_fresh(fake_repo):
    run_script(root=fake_repo)
    r = run_script("--check", root=fake_repo)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "up to date" in r.stdout


def test_check_fails_when_stale(fake_repo):
    run_script(root=fake_repo)
    # Add a new skill dir without regenerating -> catalog is stale.
    _write_fixture(fake_repo / "skills", "another-skill", "SKILL.md", SKILL_FM)
    r = run_script("--check", root=fake_repo)
    assert r.returncode == 1
    assert "stale" in r.stdout


def test_skill_entry_uses_skill_schema(fake_repo):
    run_script(root=fake_repo)
    text = (fake_repo / "skills" / "CATALOG.md").read_text(encoding="utf-8")
    assert "## test-skill" in text
    assert "| category | testing |" in text
    assert "| risk | safe |" in text
    assert "| source | self |" in text
    assert "install_skill.py skills/test-skill" in text
    assert "测试技能" in text


def test_agent_entry_omits_skill_only_fields(fake_repo):
    run_script(root=fake_repo)
    text = (fake_repo / "agents" / "CATALOG.md").read_text(encoding="utf-8")
    assert "## test-agent" in text
    assert "| mode | subagent |" in text
    assert "install_agent.py agents/test-agent" in text
    # skill-only schema fields must NOT appear for agents
    assert "| category |" not in text
    assert "| risk |" not in text
    assert "| source |" not in text
    assert "| date_added |" not in text


def test_generate_is_idempotent(fake_repo):
    run_script(root=fake_repo)
    before = (fake_repo / "skills" / "CATALOG.md").read_text(encoding="utf-8")
    run_script(root=fake_repo)
    after = (fake_repo / "skills" / "CATALOG.md").read_text(encoding="utf-8")
    assert before == after


def test_validate_agents_ignores_catalog_md(tmp_path):
    """validate_agents.py must not treat agents/CATALOG.md as an agent definition."""
    from conftest import run_script

    # Synthetic agents/ dir: one real agent + CATALOG.md + README.md.
    agents = tmp_path / "agents"
    agents.mkdir()
    _write_fixture(agents, "test-agent", "AGENT.md", AGENT_FM)
    (agents / "CATALOG.md").write_text("# catalog\n", encoding="utf-8")
    (agents / "README.md").write_text("# readme\n", encoding="utf-8")

    r = run_script("agent-creator/scripts/validate_agents.py", "--strict", "--dir", str(agents))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "Checked 1 agents." in r.stdout
