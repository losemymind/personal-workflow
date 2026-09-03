# skills/ — 已验证技能（Skill）能力目录

> 本文件由 `python tools/scripts/build_catalog.py` 自动生成，**禁止手改**。事实源 = 各 `SKILL.md` / `AGENT.md` 的 frontmatter。
> 新增/删除能力后重跑 `python tools/scripts/build_catalog.py`；CI 以 `--check` 防止目录与目录不同步。
> 检索：让 LLM 读本文件匹配需求 → 命中即给出 `install` 命令，人类确认后执行。


## code-review-skill

| category | development |
| risk | safe |
| version | 0.1.0 |
| source | community |
| date_added | 2026-09-03 |
| tags | [code-review, pr, security, performance, architecture] |
| install | `python tools/scripts/install_skill.py skills/development/code-review-skill` |

**用途**：Provides comprehensive, expert-level code review guidance across 20+ languages and frameworks — React 19, Vue 3, Angular 17+, Svelte 5, Rust, TypeScript, Java 17/21, Java 8, PHP, Ruby/Rails, Python, Django/DRF, FastAPI, Go, C#/.NET 8, Kotlin/Android, Swift/SwiftUI, Dart/Flutter, NestJS, C/C++, Zig, CSS/Less/Sass, Qt, and more. Covers architecture review, performance review, security audit, code-quality anti-patterns, and common bugs across all ecosystems, with progressive-disclosure per-language guides. Use when: reviewing pull requests, conducting PR reviews, code review, reviewing code changes, establishing review standards, mentoring developers, architecture reviews, security audits, performance reviews, checking code quality, finding bugs, giving feedback on code — 或用户要求代码审查、review PR/代码改动、架构审查、安全审计、检查代码质量、找 Bug、给代码反馈时使用。

**触发器**：Reviewing pull requests and code changes

## pr-summarizer

| category | git |
| risk | safe |
| version | 0.1.0 |
| source | self |
| date_added | 2026-09-02 |
| tags | [git, pr, summary, review] |
| install | `python tools/scripts/install_skill.py skills/git/pr-summarizer` |

**用途**：将 git diff 转为结构化 PR 总结：一句话摘要、变更分类表、审查清单、风险标注与语义化标题建议。当用户要求总结变更、撰写 PR 描述、review 前梳理 diff、或说「总结我的改动」「写 PR 描述」「PR 摘要」时使用。

**触发器**：用户要求「总结我的改动」「写 PR 描述」「PR 摘要」「review 前梳理 diff」

