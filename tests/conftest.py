"""Shared pytest fixtures: temp skill/agent dirs and validation helpers."""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

SKILL_FIXTURE = """---
name: {name}
description: "{desc}"
category: testing
risk: safe
source: self
version: "0.1.0"
date_added: "2026-09-02"
---

# {name}

## 概述

{desc}

## 何时使用此技能

- 测试时使用

## 工作原理

1. 执行

## 示例

```text
输入 → 输出
```

## 最佳实践

- ✅ 这样做

## 限制和注意事项

- 无
"""

AGENT_FIXTURE = """---
name: {name}
description: "{desc}"
mode: subagent
tools: [read, grep, bash]
permission:
  edit: deny
version: "0.1.0"
---

# {name}

## 角色定位

{desc}

## 职责范围

**必须做：**
- 审查

**拒绝做：**
- 不修改代码

## 工作方式

只读

## 工具与权限

- 允许：read grep bash
- 禁止：edit

## 协作协议

- **何时被调用**：用户请求
- **汇报格式**：清单
- **升级路径**：权限不足时交还用户

## 完成标准

- [ ] 输出清单

## 限制与边界

- 不运行测试
"""


def run_script(script: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run one of the repo's CLI scripts and capture output."""
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / script), *args],
        capture_output=True,
        text=True,
        cwd=cwd or REPO_ROOT,
    )


@pytest.fixture
def temp_skill(tmp_path: Path) -> Path:
    d = tmp_path / "test-skill"
    d.mkdir()
    (d / "SKILL.md").write_text(
        SKILL_FIXTURE.format(name="test-skill", desc="测试技能"), encoding="utf-8"
    )
    return d


@pytest.fixture
def temp_agent(tmp_path: Path) -> Path:
    d = tmp_path / "test-agent"
    d.mkdir()
    (d / "AGENT.md").write_text(
        AGENT_FIXTURE.format(name="test-agent", desc="测试代理"), encoding="utf-8"
    )
    return d