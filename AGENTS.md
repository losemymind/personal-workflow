# PersonalWorkflow AGENTS 引导

本文件是所有 LLM 客户端（claude / opencode / codex / deepseek-harness）接入 PersonalWorkflow 的**分发入口**。将其加入客户端配置（如 opencode 的 `opencode.json` 的 `instructions`，或项目根直接放置）后，代理即可按本文件引导使用本仓库的技能与代理。

## 本仓库是什么

PersonalWorkflow 是个人工作流的工具库，提供三部分能力：

| 部分 | 位置 | 职责 |
|---|---|---|
| 技能创建器 | `skill-creator/` | 创建/改进/验证/对比技能，维护上游索引 |
| 代理创建器 | `agent-creator/` | 创建/改进/验证代理 |
| 技能库 | `skills/` | 已验证可安装的技能（回馈目标；含自动生成的能力目录 `CATALOG.md`） |
| 代理库 | `agents/` | 已验证可安装的代理（含自动生成的能力目录 `CATALOG.md`） |
| 基础工具 | `tools/scripts/` | 四端安装器 + 能力目录生成器 + 生命周期管理（install/update/uninstall/rollback） |

## 入口选择（先定领域）

| 任务类型 | 进入入口 | 说明 |
|---|---|---|
| **按需安装**已有技能/代理（用现成能力） | 读 `skills/CATALOG.md` / `agents/CATALOG.md` | 让 LLM 读能力目录匹配需求 → 命中即给 install 命令，确认后执行 |
| 创建/改进/**技能** | `skill-creator/AGENTS.md` | 技能领域入口（先查本地→再查上游→创建→验证→安装） |
| 创建/改进/**代理** | `agent-creator/AGENTS.md` | 代理领域入口（先查本地→身份先于指令→创建→验证→安装） |
| 安装/生命周期（通用） | `tools/docs/lifecycle.md` | 安装/升级/卸载/回滚命令 |
| 其他/不确定 | 继续读本文件 | 总编排兜底 |

**技能 vs 代理取舍**：可描述的步骤化流程 → 技能；需要常驻角色/权限/协作 → 代理。

**能力目录说明**：`skills/CATALOG.md` 与 `agents/CATALOG.md` 由 `tools/scripts/build_catalog.py` 从各 `SKILL.md`/`AGENT.md` frontmatter 自动生成，是「本地已验证能力」的机器可读清单；新增/删除能力后重跑 `python tools/scripts/build_catalog.py`（CI 用 `--check` 防漂移）。它是 LLM 按需检索本地能力的唯一入口，**不代表上游库**（上游只在技能创建对比流程使用）。

## 标准工作流

当用户需要"一个做 X 的技能/代理"时，先按上方「入口选择」定位领域，再按该入口的领域工作流执行（**引导型：不自动执行安装**，每步向用户确认后再做）。总览如下：

### 1. 查本地已验证库（先查后建）

```bash
# 读能力目录，看本地是否已有合适能力（而非直接查上游/新建）
# 技能：skills/CATALOG.md ；代理：agents/CATALOG.md
```

- **本地有合适能力且只是想用** → 让 LLM 匹配目录条目，给 install 命令，确认后安装（进第 5 步）。本仓库现有：`pr-summarizer`（skills）、`code-reviewer`（agents）。
- 本地无合适能力 → 继续。

### 2. 检索上游（仅技能创建，无本地候选时）

```bash
python skill-creator/scripts/search_index.py "<需求关键词>" [--category X] [--risk Y] [--limit 10]
```

- 有匹配候选 → 记录候选，继续第 3 步对比
- 无匹配 → 直接跳到第 4 步创建

### 3. 对比择优（有候选时）

```bash
python skill-creator/scripts/compare_skills.py <本地候选或新建> <上游候选目录>
```

- 上游更优 → 建议采纳上游（记录到 `skill-creator/evolutions/`）
- 自建更优 → 用自建版本

### 4. 创建（无合适技能/代理时）

```bash
# 创建技能（交互式脚手架 + 验证）
python skill-creator/scripts/create_skill.py
python skill-creator/scripts/validate_skills.py --strict --dir skills/<name>

# 创建代理（交互式脚手架 + 验证）
python agent-creator/scripts/create_agent.py
python agent-creator/scripts/validate_agents.py --strict --dir agents/<name>
```

### 5. 验证测试

按 `skill-creator/SKILL.md` 的阶段 5-7 执行：自动验证 → 真实任务测试 → 触发优化（代理按 `agent-creator/SKILL.md` 阶段 5-6）。

### 6. 安装到客户端

```bash
# 指定客户端安装
python tools/scripts/install_skill.py --client <claude|opencode|codex|deepseek> <技能目录>

# 自动探测已安装客户端
python tools/scripts/install_skill.py <技能目录>

# 代理安装（同构）
python tools/scripts/install_agent.py --client <claude|opencode|codex|deepseek> <代理目录>
```

### 7. 回馈仓库

稳定使用后：更新元数据（source/date_added/version/tags）→ 放入 `skills/<name>/`（或 `agents/<name>/`）→ 运行 `python tools/scripts/build_catalog.py` 刷新能力目录 → 提交（含 `evolutions/` 对比记录）。

## 生命周期操作（维护）

```bash
# 技能
python tools/scripts/update_skill.py <技能名> --source <新版目录>   # 升级（自动备份旧版）
python tools/scripts/uninstall_skill.py <技能名>                    # 卸载（仅限本仓库装的）
python tools/scripts/rollback_skill.py <技能名>                     # 回滚上一版本

# 代理（同构）
python tools/scripts/update_agent.py <代理名> --source <新版目录或.md>
python tools/scripts/uninstall_agent.py <代理名>
python tools/scripts/rollback_agent.py <代理名>
```

## 目录导览

- `skill-creator/SKILL.md` — 技能创建方法论（10 阶段工作流，阶段 0 先本地后上游）
- `skill-creator/references/` — 规范参考（template/anatomy/quality-bar/index/comparison）
- `skill-creator/examples/` — 6 个上游学习样本
- `skill-creator/evolutions/` — 对比择优学习记录（反馈闭环）
- `agent-creator/SKILL.md` — 代理创建方法论（身份先于指令、最小权限、协作协议）
- `agent-creator/references/` — 代理规范参考（template/anatomy/quality-bar）
- `skills/CATALOG.md` / `agents/CATALOG.md` — 已验证能力目录（自动生成）
- `tools/scripts/build_catalog.py` — 能力目录生成器
- `tools/docs/lifecycle.md` — 生命周期操作详解
- `docs/ON-DEMAND-INSTALL.md` — 按需安装与能力目录方案

## 客户端接入方式

| 客户端 | 接入位置 |
|---|---|
| opencode | `opencode.json` 的 `instructions: ["../PersonalWorkflow/AGENTS.md"]`（相对路径按实际为准） |
| claude | 项目根 `CLAUDE.md` 中 `@import ../PersonalWorkflow/AGENTS.md`，或直接复制内容 |
| codex | `AGENTS.md` 放项目根（codex 原生读取） |
| deepseek-harness | 按其文档配置 instructions 引用 |

## 原则

- **先查后建**：永远先检索上游再创建，避免重复造轮子
- **验证优先**：未经 `validate_skills.py` 验证的技能不安装
- **引导不自动**：本文件只指引路径，不代替用户执行安装/提交等副作用操作
- **回馈闭环**：每次"上游更优"的对比都是学习机会（`evolutions/`）