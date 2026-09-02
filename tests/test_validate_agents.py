"""Tests for validate_agents.py."""

def test_valid_agent_passes(temp_agent):
    from conftest import run_script

    r = run_script(
        "agent-creator/scripts/validate_agents.py",
        "--strict",
        "--dir",
        str(temp_agent),
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "All agents passed" in r.stdout


def test_missing_boundary_fails_strict(temp_agent):
    from conftest import run_script

    content = (temp_agent / "AGENT.md").read_text(encoding="utf-8")
    content = content.replace("## 职责范围", "## 职责（无边界）")
    (temp_agent / "AGENT.md").write_text(content, encoding="utf-8")

    r = run_script(
        "agent-creator/scripts/validate_agents.py",
        "--strict",
        "--dir",
        str(temp_agent),
    )
    assert r.returncode == 1
    assert "职责范围" in r.stdout or "boundary" in r.stdout


def test_tools_declaration_required(temp_agent):
    from conftest import run_script

    content = (temp_agent / "AGENT.md").read_text(encoding="utf-8")
    content = content.replace("tools: [read, grep, bash]\n", "")
    content = content.replace("permission:\n  edit: deny\n", "")
    # remove the body section too, so no permission declaration remains anywhere
    content = content.replace("## 工具与权限\n\n- 允许：read grep bash\n- 禁止：edit\n\n", "")
    (temp_agent / "AGENT.md").write_text(content, encoding="utf-8")

    r = run_script(
        "agent-creator/scripts/validate_agents.py",
        "--strict",
        "--dir",
        str(temp_agent),
    )
    assert r.returncode == 1
    assert "tools/permission" in r.stdout