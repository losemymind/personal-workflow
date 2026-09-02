# agents/ — 已验证代理（Agent）能力目录

> 本文件由 `python tools/scripts/build_catalog.py` 自动生成，**禁止手改**。事实源 = 各 `SKILL.md` / `AGENT.md` 的 frontmatter。
> 新增/删除能力后重跑 `python tools/scripts/build_catalog.py`；CI 以 `--check` 防止目录与目录不同步。
> 检索：让 LLM 读本文件匹配需求 → 命中即给出 `install` 命令，人类确认后执行。


## code-reviewer

| mode | subagent |
| version | 0.1.0 |
| tags | [code-review, quality, agent] |
| install | `python tools/scripts/install_agent.py agents/code-reviewer` |

**用途**：常驻代码审查代理：对 PR/diff 做多轴质量审查（正确性/可维护性/性能/安全），分级输出问题清单与修改建议。当用户要求「审查代码」「review 我的改动」「合并前把关」时被调用。只读角色，无编辑权限。

