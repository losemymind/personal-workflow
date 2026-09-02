# skill-creator AGENTS 引导（技能领域入口）

本文件是 **PersonalWorkflow 技能领域** 的入口（总编排见仓库根 `AGENTS.md`）。当任务涉及**创建/改进/验证/对比/安装技能**时，从总编排进入本文件，按此引导执行；细节方法论在 `SKILL.md`，规范在 `references/`（渐进式披露：按需读取，不一次全部加载）。

## 何时进入本文件

- 根 AGENTS 判定用户要「创建/改进一个技能」→ 进入本文件的**生成流程**
- 用户要「按需安装/用现成的本地技能」→ 见下方「按需安装路径」（不生成）
- 需要为技能安装到 claude / opencode / codex / deepseek 客户端
- 用户提到触发词：「创建skill」「写个技能」「skill-creator」「把xx做成技能」「添加技能」

## 领域工作流（引导型：每步向用户确认后再执行）

> **职责分层**：是否调用 skill-creator（生成器）由上层（根 AGENTS）判定；本领域文件的生成流程 = **查本地现有候选 → 必定调用 skill-creator 生成 → 与本地候选对比取最优**。skill-creator 是可独立安装的生产器，其自身闭环见 `SKILL.md`（按需求创建 → 检索上游对比 → 上游更优则优化自身）。

### 0. 按需安装路径（只想用现成的，不生成）

用户明确只要**现成的**（非创建需求）→ 读本地能力目录 `skills/CATALOG.md`，命中即给条目的 `install` 命令（如 `python tools/scripts/install_skill.py skills/pr-summarizer`），**用户确认后**再执行，不调用生成器。

### 1. 查本地现有候选（先查后建）

用户要**创建/改进**「做 X 的技能」时，先读 `skills/CATALOG.md`（由 `tools/scripts/build_catalog.py` 从各 `SKILL.md` frontmatter 自动生成）判断本地是否已有合适技能：

- 命中 → 记作「现有候选 A」（有则可用作对比基座）
- 未命中 → 候选 A 为空

**无论 A 是否存在，都继续调用 skill-creator 生成**（不因本地已有而跳过）。

### 2. 调用 skill-creator 生成（必定执行）

生成器内部闭环（细节见 `SKILL.md`）：**按需求创建一个技能 → 检索上游 → 有候选则对比取最优 B / 无则 B=自建 → 上游更优则记录 evolutions 并优化 skill-creator**。

按顺序执行：

**2a. 检索上游**（判断是否有候选，供阶段 5.5 对比）：

```bash
python skill-creator/scripts/search_index.py "<需求关键词>" [--category X] [--risk Y] [--limit 10]
```

有匹配候选 → 记录候选；无匹配 → 用自建版（跳过 2c）。

**2b. 创建（脚手架）**：

```bash
python skill-creator/scripts/create_skill.py --name <技能名> --category <分类> --risk <级别>
```

frontmatter 必须含 `version: "0.1.0"`（生命周期记账用）。骨架生成后按 `SKILL.md` 阶段 4 完善正文。

**2c. 与上游候选对比择优**（有候选时）：

```bash
python skill-creator/scripts/compare_skills.py <自建目录> <上游候选目录>
```

- 上游更优 → 采纳上游，提炼学习点记录到 `evolutions/`（反馈闭环），得到 B
- 自建更优或持平 → 用自建版，得到 B

### 3. 与本地现有候选对比取最优（A vs B）

将第 1 步的「现有候选 A」与生成器产出的「最优 B」对比，谁优用谁：

- **B 更优（或 A 为空）** → 采用 B（放入 `skills/<name>/` 供后续验证/安装/回馈）
- **A 更优/持平** → 保留 A（可将 B 的亮点吸收进 A）

> 目的：本地现有已验证能力不被盲目替换，新生成能力也不会被埋没——**谁优用谁**。

### 4. 自动验证

```bash
python skill-creator/scripts/validate_skills.py --strict --dir <技能目录>
```

失败必须修复后再继续；`--dir` 指定校验目录（默认扫描 `<repo>/skills/`）。

### 5. 真实任务测试 + 触发测试

按 `SKILL.md` 阶段 6-7：先用真实场景跑一次技能，再运行触发测试：

```bash
python skill-creator/scripts/run_trigger_tests.py <技能目录> --evals <技能目录>/evals.json
```

（evals.json 从 `templates/evals.json.template` 复制）

### 6. 安装到客户端

```bash
python tools/scripts/install_skill.py [--client <claude|opencode|codex|deepseek>] <技能目录>
```

安装后重启客户端生效；生命周期（更新/卸载/回滚）见 `tools/docs/lifecycle.md`。

### 7. 回馈仓库

技能稳定后：完善元数据（source/date_added/version/tags）→ 放入 `skills/<name>/` → 运行 `python tools/scripts/build_catalog.py` 刷新能力目录 → 提交（含 `evolutions/` 对比记录）。

## 资源导览（按需读取）

| 资源 | 何时读取 |
|---|---|
| `SKILL.md` | 任务开始时：完整方法论（10 阶段工作流） |
| `references/skill-template.md` | 需要字段/分类/风险级别细节时 |
| `references/skill-anatomy.md` | 需要结构规范/渐进式披露时 |
| `references/quality-bar.md` | 需要质量标准/验证器检查项时 |
| `references/skill-index.md` | 需要索引构建/增量同步说明时 |
| `references/skill-comparison.md` | 进行对比择优时 |
| `examples/` | 创建前研究结构范本（6 个上游样本，验证豁免） |
| `evolutions/` | 记录对比学习结论 |
| `templates/` | `SKILL.template.md`（骨架）、`evals.json.template`（测试集模板） |
| `indexes/upstream.db` | 检索上游（已提交，克隆即得） |
| `skills/CATALOG.md` | 按需安装/本地查找时（自动生成，见 `tools/scripts/build_catalog.py`） |

## 与总编排的关系

- 仓库根 `AGENTS.md` 是个人工作流**总编排**（技能+代理+工具三域）
- 本文件只负责**技能领域**：任务归属技能时在此聚焦，避免总编排信息过载
- 属于「代理/工具」的任务回到总编排按对应入口执行（`agent-creator/AGENTS.md`、`tools/`）

## 原则（与总编排一致）

- **先查后建**：先查本地 `skills/`（`CATALOG.md`）取现有候选、后查上游对比，避免重复造轮子
- **生成必调**：创建需求无论本地有无，都调用 skill-creator 生成，再与本地候选**谁优用谁**
- **验证优先**：未经 `validate_skills.py` 验证的技能不安装
- **引导不自动**：不代替用户执行安装/提交等副作用操作
- **回馈闭环**：「上游更优」的对比是学习机会（记录到 `evolutions/`）