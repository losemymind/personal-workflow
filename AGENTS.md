# PersonalWorkflow AGENTS 引导

本文件是所有 LLM 客户端（claude / opencode / codex / deepseek-harness）接入 PersonalWorkflow 的**分发入口**。将其加入客户端配置（如 opencode 的 `opencode.json` 的 `instructions`，或项目根直接放置）后，代理即可按本文件引导使用本仓库的技能与代理。

## 本仓库是什么

PersonalWorkflow 是个人工作流的工具库，提供三部分能力：

| 部分 | 位置 | 职责 |
|---|---|---|
| 技能创建器 | `skill-creator/` | 创建/改进/验证/对比技能，维护上游索引 |
| 代理创建器 | `agent-creator/` | 创建/改进/验证代理，维护代理上游索引 |
| 技能库 | `skills/` | 已验证可安装的技能（回馈目标；含自动生成的能力目录 `CATALOG.md`） |
| 代理库 | `agents/` | 已验证可安装的代理（含自动生成的能力目录 `CATALOG.md`） |
| 基础工具 | `tools/scripts/` | 四端安装器 + 能力目录生成器 + 生命周期管理（install/update/uninstall/rollback） |

## 入口选择（先定领域）

| 任务类型 | 进入入口 | 说明 |
|---|---|---|
| **按需安装**已有技能/代理（用现成能力，不创建） | 读 `skills/CATALOG.md` / `agents/CATALOG.md` | 让 LLM 读能力目录匹配需求 → 命中即给 install 命令，确认后执行 |
| 创建/改进/**技能** | 本层流程（下方）；生成器 = `skill-creator`（独立技能，引导见 `skill-creator/AGENTS.md`，方法论 `skill-creator/SKILL.md`） | 本层查本地候选 A → 调生成器产出 B → 对比 A/B 取优 |
| 创建/改进/**代理** | 本层流程（下方）；生成器 = `agent-creator`（独立技能，引导见 `agent-creator/AGENTS.md`，方法论 `agent-creator/SKILL.md`） | 同技能，入口换 `agent-creator/` |
| 安装/生命周期（通用） | `tools/docs/lifecycle.md` | 安装/升级/卸载/回滚命令 |
| 其他/不确定 | 继续读本文件 | 总编排兜底 |

**技能 vs 代理取舍**：可描述的步骤化流程 → 技能；需要常驻角色/权限/协作 → 代理。

**能力目录说明**：`skills/CATALOG.md` 与 `agents/CATALOG.md` 由 `tools/scripts/build_catalog.py` 从各 `SKILL.md`/`AGENT.md` frontmatter 自动生成，是「本地已验证能力」的机器可读清单；新增/删除能力后重跑 `python tools/scripts/build_catalog.py`（CI 用 `--check` 防漂移）。它是 LLM 按需检索本地能力的唯一入口，**不代表上游库**（上游只在技能创建对比流程使用）。

## 标准工作流

需求先按「入口选择」定域。**是否调用 skill-creator / agent-creator（生成器）由本层（根 AGENTS）判定**：

- 用户只是**用现成能力**（不创建）→ 走「按需安装」：读对应 `CATALOG.md`，命中即给 install 命令，确认后安装，**不调用生成器**。
- 用户要**创建/改进能力** → 走「创建」路径（下方），**无论本地是否已有，都调用生成器生成**，再与本地现有对比**谁优用谁**。

> skill-creator/agent-creator 是**可独立安装的技能**（不与本仓库耦合，自身含完整工作流，见各自 AGENTS.md）。本仓库只把它们当作生产器调用：查本地 → 调生成 → 对比取优在**本层完成**，不写入生成器内部。

### 入库准入规则（硬性约束）

任何能力进入 `skills/` 或 `agents/` 库，必须同时满足以下四条（违反视为不合规，需整改）：

1. **代理必经 agent-creator**：放入本库 `agents/` 的代理，**无论参考自本地其他文件还是远程仓库**，入库前都必须经过 `agent-creator`（创建/改进 → 验证 → 对比择优），并在 `docs/AGENTS-AUDIT.md` 登记。
2. **技能必经 skill-creator**：放入本库 `skills/` 的技能，**无论参考自本地其他文件还是远程仓库**，入库前都必须经过 `skill-creator`（创建/改进 → 检索上游对比 → 验证），并在 `docs/SKILLS-AUDIT.md` 登记。
3. **外部来源必标注数据来源**：本仓库 `agents/` 与 `skills/` 中的能力**若参考了外部仓库**，必须在对应审计文件（`docs/AGENTS-AUDIT.md` / `docs/SKILLS-AUDIT.md`）中标注数据来源（外部仓库地址 / 上游索引来源 / 上游条目）。
4. **分类目录必入**：创建/改进的代理与技能入库时，按其**功能**放入对应分类文件夹——代理放入 `agents/<顶层分类>/<name>/`（如 `ue-game-studio/`、`academic/`、`code-quality/`），技能按功能分类放入 `skills/<分类>/<name>/`；分类文件夹不存在时**先创建**。**任何能力均不得堆在 `agents/` / `skills/` 根目录**——通用能力同样按功能归入分类文件夹（无现成分类则新建，如 `code-quality/`），不存在「留顶层」例外。

> 审计文件是数据来源与入库合规性的**唯一记录入口**：新增、迁移、改进或整改能力后，同步更新 `docs/AGENTS-AUDIT.md` / `docs/SKILLS-AUDIT.md`。

### 创建/改进技能或代理（总览）

以技能为例（代理同构，生成器换 `agent-creator`）：

1. **查本地现有候选**（先查后建）：读 `skills/CATALOG.md`，命中即记作「现有候选 A」（有则可用，无则空）。
2. **调用生成器产出 B**：把需求交给 skill-creator 执行其内部闭环（按需求创建 → 检索上游对比 → 产出「自建/上游」最优 B，上游更优则记录 `evolutions/` 优化生成器）。命令按 `skill-creator/AGENTS.md` / `SKILL.md` 执行。
3. **对比 A 与 B** → **谁优用谁**（最优按「分类目录必入」规则放入 `skills/<分类>/<name>/`，供验证/安装/回馈）。

## 提交前收尾与交接（硬性约束）

本仓库用 `docs/HANDOFF.md` 做会话交接：**每次 git 提交前必须先「收尾 + 交接」**，确保下一个会话只读 HANDOFF 即可接手。三步：

1. **收尾（防回归全跑）**：失败先修复再继续：
   ```bash
   python -m pytest tests/ -q
   python tools/scripts/check_docs_refs.py
   python skill-creator/scripts/validate_skills.py --strict --dir skills
   python skill-creator/scripts/validate_skills.py --strict --dir skill-creator
   python agent-creator/scripts/validate_agents.py --strict --dir agents
   python tools/scripts/build_catalog.py --check
   ```
   改动涉及能力时，同步审计文件（`docs/AGENTS-AUDIT.md` / `docs/SKILLS-AUDIT.md`）并重建 CATALOG（新增/删除能力后必跑 `python tools/scripts/build_catalog.py`）。
2. **交接（更新 `docs/HANDOFF.md`）**：把本次改动同步进交接文件——刷新基线（`git log --oneline -3`）、已交付/未完成状态表、审计计数、能力清单；若改动未触及能力或文档状态（如仅占位文件），可只刷新基线行、不重写全表。
3. **确认后提交**：1/2 就绪后才 commit；提交后向用户输出「新会话交接提示语」——用**可整段复制的代码块**给出，内容自包含：新基线提交号 + 本轮一句话摘要 + HANDOFF §6 的 7 步行动清单（与 `docs/HANDOFF.md` 开场提示保持一致，以提交后的新基线刷新），供用户直接粘贴到下一个会话。

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

- `skill-creator/SKILL.md` — 技能创建方法论（可独立安装；创建→检索上游→对比择优，上游更优反哺自身）
- `skill-creator/references/` — 规范参考（template/anatomy/quality-bar/index/comparison）
- `skill-creator/examples/` — 6 个上游学习样本
- `skill-creator/evolutions/` — 对比择优学习记录（反馈闭环）
- `skill-creator/indexes/upstream.db` — 技能双源上游索引（随技能分发）
- `agent-creator/SKILL.md` — 代理创建方法论（可独立安装；身份先于指令、最小权限、协作协议）
- `agent-creator/references/` — 代理规范参考（template/anatomy/quality-bar/index）
- `agent-creator/indexes/upstream.db` — 代理三源上游索引（随技能分发）
- `agent-creator/evolutions/` — 代理对比择优学习记录（反馈闭环）
- `skills/CATALOG.md` / `agents/CATALOG.md` — 已验证能力目录（自动生成）
- `tools/scripts/build_catalog.py` — 能力目录生成器
- `tools/docs/lifecycle.md` — 生命周期操作详解
- `docs/AGENTS-AUDIT.md` / `docs/SKILLS-AUDIT.md` — 代理/技能审计（数据来源 + 入库合规唯一记录入口）
- `docs/HANDOFF.md` — 会话交接文件（提交前收尾/交接的落地对象；新会话开场提示）
- `docs/ON-DEMAND-INSTALL.md` — 按需安装与能力目录方案

## 客户端接入方式

| 客户端 | 接入位置 |
|---|---|
| opencode | `opencode.json` 的 `instructions: ["../PersonalWorkflow/AGENTS.md"]`（相对路径按实际为准） |
| claude | 项目根 `CLAUDE.md` 中 `@import ../PersonalWorkflow/AGENTS.md`，或直接复制内容 |
| codex | `AGENTS.md` 放项目根（codex 原生读取） |
| deepseek-harness | 按其文档配置 instructions 引用 |

## 原则

- **先查后建**：创建前先查本地 `CATALOG.md` 取现有候选、再查上游对比，避免重复造轮子
- **生成必调 / 谁优用谁**：创建/改进需求无论本地有无，都调用对应生成器，生成结果与本地现有对比取最优
- **引导不自动**：本文件只指引路径，不代替用户执行安装/提交等副作用操作；是否调用生成器由本层判定
- **验证优先**：未经 `validate_skills.py` / `validate_agents.py` 验证的能力不安装
- **提交前收尾交接**：每次 git 提交前先跑防回归收尾 + 更新 `docs/HANDOFF.md` 交接新会话（见「提交前收尾与交接」节）
- **回馈闭环**：每次"上游更优"的对比都是学习机会（`evolutions/`）