# PersonalWorkflow

个人工作流工具库：**检索上游 → 创建 → 对比择优 → 验证 → 安装 → 回馈** 的完整闭环，支持 claude / opencode / codex / deepseek-harness 四个 LLM 客户端。

## 是什么

PersonalWorkflow 是个人工作流（技能/代理）的分发与回馈中心：

| 部分 | 位置 | 职责 |
|---|---|---|
| 分发入口 | `AGENTS.md` | 引导 LLM 客户端按标准流程使用本仓库 |
| 技能创建器 | `skill-creator/` | 创建/改进/验证/对比技能（含上游索引检索） |
| 技能库 | `skills/` | 已验证可安装的技能（回馈目标位置） |
| 代理库 | `agents/` | 已验证可安装的代理 |
| 基础工具 | `tools/scripts/` | 四端安装器与生命周期管理（install/update/uninstall/rollback） |

## 安装到你的项目

1. 确保本仓库在本地（或克隆到任意位置）
2. 把 `AGENTS.md` 接入你的 LLM 客户端（见下）
3. 重启客户端，按引导使用

| 客户端 | 接入位置 |
|---|---|
| opencode | `opencode.json` 的 `instructions: ["../PersonalWorkflow/AGENTS.md"]` |
| claude | 项目根 `CLAUDE.md` 中 `@import ../PersonalWorkflow/AGENTS.md` |
| codex | `AGENTS.md` 放项目根（codex 原生读取） |
| deepseek-harness | 按其文档配置 instructions 引用 |

## 快速开始

```bash
# 检索上游是否已有可用技能（先查后建）
python skill-creator/scripts/search_index.py "你的需求关键词"

# 创建新技能（交互式脚手架）
python skill-creator/scripts/create_skill.py --name my-skill --category productivity --risk safe

# 验证技能
python skill-creator/scripts/validate_skills.py --strict --dir skills/my-skill

# 安装到客户端（自动探测已安装客户端）
python tools/scripts/install_skill.py skills/my-skill

# 生命周期管理
python tools/scripts/update_skill.py my-skill --source skills/my-skill
python tools/scripts/uninstall_skill.py my-skill
python tools/scripts/rollback_skill.py my-skill
```

## 核心原则

- **先查后建**：先检索上游索引（2100+ 技能）再创建，避免重复造轮子
- **验证优先**：未经 `validate_skills.py` 验证的技能不安装
- **引导不自动**：`AGENTS.md` 只指引路径，不代替用户执行安装/提交
- **回馈闭环**：稳定的技能/代理回馈到 `skills/` `agents/`，对比学习记录在 `skill-creator/evolutions/`

详细开发计划见 `docs/DEVELOPMENT-PLAN.md`。