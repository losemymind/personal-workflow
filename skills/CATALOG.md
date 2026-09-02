# skills/ — 已验证技能（Skill）能力目录

> 本文件由 `python tools/scripts/build_catalog.py` 自动生成，**禁止手改**。事实源 = 各 `SKILL.md` / `AGENT.md` 的 frontmatter。
> 新增/删除能力后重跑 `python tools/scripts/build_catalog.py`；CI 以 `--check` 防止目录与目录不同步。
> 检索：让 LLM 读本文件匹配需求 → 命中即给出 `install` 命令，人类确认后执行。


## pr-summarizer

| category | git |
| risk | safe |
| version | 0.1.0 |
| source | self |
| date_added | 2026-09-02 |
| tags | [git, pr, summary, review] |
| install | `python tools/scripts/install_skill.py skills/pr-summarizer` |

**用途**：将 git diff 转为结构化 PR 总结：一句话摘要、变更分类表、审查清单、风险标注与语义化标题建议。当用户要求总结变更、撰写 PR 描述、review 前梳理 diff、或说「总结我的改动」「写 PR 描述」「PR 摘要」时使用。

**触发器**：用户要求「总结我的改动」「写 PR 描述」「PR 摘要」「review 前梳理 diff」

