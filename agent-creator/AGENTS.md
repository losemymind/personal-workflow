# agent-creator AGENTS 引导（代理领域入口）

本文件是 **PersonalWorkflow 代理领域** 的入口（总编排见仓库根 `AGENTS.md`）。当任务涉及**创建/改进/验证/安装代理**时，从总编排进入本文件，按此引导执行；细节方法论在 `SKILL.md`，规范在 `references/`（渐进式披露：按需读取，不一次全部加载）。

## 何时进入本文件

- 根 AGENTS 判定用户要「创建/改进一个代理」→ 进入本文件的**生成流程**
- 用户要「按需安装/用现成的本地代理」→ 见下方「按需安装路径」（不生成）
- 需要为代理安装到 claude / opencode / codex / deepseek 客户端
- 用户提到触发词：「创建agent」「写个代理」「agent-creator」「把这个角色做成代理」

**技能 vs 代理取舍**：可描述的步骤化流程 → 技能（进入 `skill-creator/AGENTS.md`）；需要常驻角色/权限/协作 → 代理（本文件）。

## 领域工作流（引导型：每步向用户确认后再执行）

> **职责分层**：是否调用 agent-creator（生成器）由上层（根 AGENTS）判定；本领域文件的生成流程 = **查本地现有候选 → 必定调用 agent-creator 生成 → 与本地候选对比取最优**。agent-creator 是可独立安装的生产器，其自身闭环见 `SKILL.md`（按需求创建 → 检索上游对比 → 上游更优则优化自身）。

### 0. 按需安装路径（只想用现成的，不生成）

用户明确只要**现成的**（非创建需求）→ 读本地能力目录 `agents/CATALOG.md`，命中即给条目的 `install` 命令（如 `python tools/scripts/install_agent.py agents/code-reviewer`），**用户确认后**再执行，不调用生成器。

### 1. 查本地现有候选（先查后建）

用户要**创建/改进**「做 X 的代理」时，先读 `agents/CATALOG.md`（由 `tools/scripts/build_catalog.py` 从各 `AGENT.md` frontmatter 自动生成）判断本地是否已有合适代理：

- 命中 → 记作「现有候选 A」（有则可用作对比基座）
- 未命中 → 候选 A 为空

**无论 A 是否存在，都继续调用 agent-creator 生成**（不因本地已有而跳过）。

### 2. 调用 agent-creator 生成（必定执行）

**2a. 明确角色与边界（先问后建）**——确认身份的**身份与边界**（不必一次问完，逐条确认）：
- 角色一句话怎么说？被谁调用、何时调用？
- 必须做什么？**坚决拒绝做什么**？（边界是代理质量的核心）
- 需要哪些工具？哪些绝不该碰？（最小权限）
- 完成标准如何验收？何时停下交还人类？（升级路径）

有现成的角色描述、协作流程文档就贴出来当证据。

**2b. 检索上游候选**（供对比）：

```bash
python skill-creator/scripts/search_index.py "<需求关键词>" [--category X] [--limit 10]
```

（与 skill-creator 同一索引；代理/编排类技能候选可学习采纳）

**2c. 创建（脚手架）**：

```bash
python agent-creator/scripts/create_agent.py --name <代理名> --mode subagent [--tools read,grep,bash]
```

frontmatter 必须含 `version: "0.1.0"` 与最小权限声明。骨架生成后按 `SKILL.md` 阶段 4 完善（身份先于指令：角色定位 → 职责边界 → 协作协议）。

**2d. 与候选对比**：有上游候选时对比择优（自建更优用自建，上游更优则学习/采纳并记录 `evolutions/` 反哺 agent-creator）——得到生成结果 B。

### 3. 与本地现有候选对比取最优（A vs B）

将第 1 步的「现有候选 A」与生成的「最优 B」对比，谁优用谁：

- **B 更优（或 A 为空）** → 采用 B（放入 `agents/<name>/` 供后续验证/安装/回馈）
- **A 更优/持平** → 保留 A（可将 B 的亮点吸收进 A）

### 4. 自动验证

```bash
python agent-creator/scripts/validate_agents.py --strict --dir <代理目录>
```

检查项：frontmatter / `name` 一致 /「职责范围」含必须做+拒绝做 / 工具权限声明 / 协作协议含升级路径 / 引用不悬空。失败必须修复后再继续。

### 5. 真实场景测试

按 `SKILL.md` 阶段 6：构造 2-3 个该代理会被调用的真实场景，实际跑一次：验证身份表述、边界执行（拒绝该拒绝的）、权限遵守、汇报格式。根据结果迭代 AGENT.md。

### 6. 安装到客户端

```bash
python tools/scripts/install_agent.py [--client <claude|opencode|codex|deepseek>] <代理目录>
```

安装后重启客户端生效；生命周期（更新/卸载/回滚）见 `tools/docs/lifecycle.md`（与技能同构）。

### 7. 回馈仓库

代理稳定后：完善元数据（source/version/tags/tools_clients）→ 放入 `agents/<name>/` → 运行 `python tools/scripts/build_catalog.py` 刷新能力目录 → 提交（含测试记录）。

## 资源导览（按需读取）

| 资源 | 何时读取 |
|---|---|
| `SKILL.md` | 任务开始时：完整方法论（身份先于指令/最小权限/协作协议） |
| `references/agent-template.md` | 需要字段细节/四端兼容矩阵时 |
| `references/agent-anatomy.md` | 需要结构规范/技能代理取舍时 |
| `references/agent-quality-bar.md` | 需要质量标准/验证器检查项时 |
| `templates/AGENT.template.md` | 骨架模板（脚手架可自动生成） |
| `agents/CATALOG.md` | 按需安装/本地查找时（自动生成，见 `tools/scripts/build_catalog.py`） |

## 与总编排的关系

- 仓库根 `AGENTS.md` 是个人工作流**总编排**（技能+代理+工具三域）
- 本文件只负责**代理领域**：任务归属代理时在此聚焦，避免总编排信息过载
- 属于「技能/工具」的任务回到总编排按对应入口执行（`skill-creator/AGENTS.md`、`tools/`）

## 原则（与总编排一致）

- **身份先于指令**：先定义角色与边界，再谈做什么
- **最小权限**：只授予职责必需的工具，破坏性操作默认拒绝
- **先查后建 / 生成必调**：先查本地 `agents/`（`CATALOG.md`）取现有候选；创建需求无论有无都调用 agent-creator 生成，再**谁优用谁**
- **验证优先**：未经 `validate_agents.py` 验证的代理不安装
- **引导不自动**：不代替用户执行安装/提交等副作用操作
- **升级路径**：代理不确定或越权时必须停下交还人类