"""Tests for validate_skills.py."""


def test_valid_skill_passes(temp_skill):
    from conftest import run_script

    r = run_script("skill-creator/scripts/validate_skills.py", "--strict", "--dir", str(temp_skill))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "All skills passed" in r.stdout


def test_missing_risk_fails_strict(temp_skill):
    from conftest import run_script

    content = (temp_skill / "SKILL.md").read_text(encoding="utf-8")
    content = content.replace("risk: safe\n", "")
    (temp_skill / "SKILL.md").write_text(content, encoding="utf-8")

    r = run_script("skill-creator/scripts/validate_skills.py", "--strict", "--dir", str(temp_skill))
    assert r.returncode == 1
    assert "Missing 'risk'" in r.stdout


def test_dangling_backtick_reference_fails(temp_skill):
    from conftest import run_script

    content = (temp_skill / "SKILL.md").read_text(encoding="utf-8")
    content += "\n参考 `references/missing.md` 获取细节。\n"
    (temp_skill / "SKILL.md").write_text(content, encoding="utf-8")

    r = run_script("skill-creator/scripts/validate_skills.py", "--strict", "--dir", str(temp_skill))
    assert r.returncode == 1
    assert "Backtick reference" in r.stdout


def test_backtick_ref_inside_fence_is_ignored(temp_skill):
    """Illustrative paths inside fenced code blocks must NOT fail validation."""
    from conftest import run_script

    content = (temp_skill / "SKILL.md").read_text(encoding="utf-8")
    content += "\n## 示例路径\n\n```\nsrc/auth.ts\ntests/auth.test.ts\n```\n"
    (temp_skill / "SKILL.md").write_text(content, encoding="utf-8")

    r = run_script("skill-creator/scripts/validate_skills.py", "--strict", "--dir", str(temp_skill))
    assert r.returncode == 0, r.stdout + r.stderr