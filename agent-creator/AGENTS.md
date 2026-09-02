# agent-creator AGENTS 引导（代理创建器）

agent-creator 是一个**可独立安装**到 LLM 客户端（claude / opencode / codex / deepseek）的**代理创建器**：把用户反复出现的工作角色与职责边界蒸馏为可复用、可验证、跨客户端安装的高质量代理（Agent）。它走**明确角色 → 创建 → 验证 → 场景测试 → 安装 → 回馈**的完整闭环。

> 本文件是 agent-creator 自身的使用引导，随技能一起安装、独立生效；用户或宿主需要创建/改进代理时按本引导执行。完整方法论见 `SKILL.md`，规范在 `references/`（渐进式披露：按需读取，不一次全部加载）。

## 何时使用本技能

- 用户要求「把这个角色做成一个代理」「创建一个 agent」「改进现有代理」
- 需要一个常驻 LLM 角色（审查者、调试者、规划者、测试者等）持续参与工作
- 需要子代理（subagent）承担独立职责的任务
- 需要把代理安装到 claude / opencode / codex / deepseek 客户端的 agents 目录
- 用户提到触发词：「创建agent」「写个代理」「agent-creator」「把这个角色做成代理」

**技能 vs 代理取舍**：可描述的步骤化流程 → 技能（用 `skill-creator`）；需要常驻角色/权限/协作 → 代理（本技能）。

## 工作流（引导型：每步向用户确认后再执行）

### 1. 明确角色与边界（先问后建）

先确认代理的**身份与边界**（不必一次问完，逐条确认）：
- 角色一句话怎么说？被谁调用、何时调用？
- 必须做什么？**坚决拒绝做什么**？（边界是代理质量的核心）
- 需要哪些工具？哪些绝不该碰？（最小权限）
- 完成标准如何验收？何时停下交还人类？（升级路径）

有现成的角色描述、协作流程文档就贴出来当证据。

### 2. 创建（脚手架）

```bash
python agent-creator/scripts/create_agent.py --name <代理名> --mode subagent [--tools read,grep,bash] [--out <目录>]
```

frontmatter 必须含 `version: "0.1.0"` 与最小权限声明。骨架生成后按 `SKILL.md` 阶段 4 完善（身份先于指令：角色定位 → 职责边界 → 协作协议）。

### 3. 自动验证

```bash
python agent-creator/scripts/validate_agents.py [--strict] [--dir <代理目录>]
```

检查项：frontmatter / `name` 一致 /「职责范围」含必须做+拒绝做 / 工具权限声明 / 协作协议含升级路径 / 引用不悬空。失败必须修复后再继续。

### 4. 与上游候选对比择优（有候选时）

若阶段 0 在 `indexes/upstream.db` 检索到匹配代理，将自建代理与上游候选结构化对比（质量 6 维 + 结构 4 维）：

```bash
python agent-creator/scripts/compare_agents.py <自建目录> <上游候选目录>        # 单个
python agent-creator/scripts/compare_agents.py <自建目录> <上游目录> --all-candidates   # 全部候选
```

- **上游更优** → 采纳上游；提炼学习点记入 `evolutions/`，反哺优化本技能方法论（反馈闭环）。
- **自建更优或持平** → 用自建版本。

### 5. 真实场景测试

按 `SKILL.md` 阶段 6：构造 2-3 个该代理会被调用的真实场景，实际跑一次：验证身份表述、边界执行（拒绝该拒绝的）、权限遵守、汇报格式。根据结果迭代 AGENT.md。

### 6. 安装到客户端

```bash
python tools/scripts/install_agent.py [--client <claude|opencode|codex|deepseek>] <代理目录>
```

安装后重启客户端生效；生命周期（更新/卸载/回滚）见 `tools/docs/lifecycle.md`。

### 7. 回馈稳定代理

代理稳定后：完善元数据（source/version/tags/tools_clients）→ 归档到代理库/可分发目录 → 含测试记录一并沉淀。

## 资源路径基准

本技能内资源引用（`references/`、`scripts/`、`templates/`）均以**技能目录本身**为基准：

- 在本技能随附的仓库内运行：`agent-creator/references/xxx.md`、`agent-creator/scripts/xxx.py`。
- 安装到客户端后：以实际技能目录为准（如 `~/.config/opencode/skills/agent-creator/...`）。

读取规则：references 文档**按需读取**；需要字段/四端差异时读 `references/agent-template.md`，结构规范读 `references/agent-anatomy.md`，质量标准读 `references/agent-quality-bar.md`，索引检索/更新读 `references/agent-index.md`，对比择优读 `references/agent-comparison.md`。

## 资源导览（按需读取）

| 资源 | 何时读取 |
|---|---|
| `SKILL.md` | 任务开始时：完整方法论（身份先于指令/最小权限/协作协议） |
| `references/agent-template.md` | 需要字段细节/四端兼容矩阵时 |
| `references/agent-anatomy.md` | 需要结构规范/技能代理取舍时 |
| `references/agent-quality-bar.md` | 需要质量标准/验证器检查项时 |
| `references/agent-index.md` | 需要检索上游/索引构建更新时 |
| `references/agent-comparison.md` | 进行对比择优（阶段 4，质量 6 维 + 结构 4 维）时 |
| `templates/AGENT.template.md` | 骨架模板（脚手架可自动生成） |
| `indexes/upstream.db` | 检索上游代理（已随技能分发，克隆即得） |
| `evolutions/` | 记录"上游更优"对比结论（反馈闭环） |

## 相关技能

- `skill-creator` — 同构的技能创建器（代理职责内的「怎么做」环节用技能承载）
- 技能 vs 代理取舍：可描述的步骤化流程 → 技能（`skill-creator`）；需要常驻角色/权限/协作 → 代理（本技能）

## 设计原则

- **身份先于指令**：先定义角色与边界，再谈做什么
- **最小权限**：只授予职责必需的工具，破坏性操作默认拒绝
- **验证优先**：未经 `validate_agents.py` 验证的代理不安装/不回馈
- **引导不自动**：只给路径与命令，不代替用户执行安装/提交等副作用操作
- **升级路径**：代理不确定或越权时必须停下交还人类
