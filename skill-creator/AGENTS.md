# skill-creator AGENTS 引导（技能领域入口）

本文件是 **PersonalWorkflow 技能领域** 的入口（总编排见仓库根 `AGENTS.md`）。当任务涉及**创建/改进/验证/对比/安装技能**时，从总编排进入本文件，按此引导执行；细节方法论在 `SKILL.md`，规范在 `references/`（渐进式披露：按需读取，不一次全部加载）。

## 何时进入本文件

- 用户要求「把某个工作流做成技能」「创建一个 skill」「改进现有技能」
- 用户要「按需安装/找一个已有的本地技能」→ 先读 `skills/CATALOG.md`
- 需要检索上游是否已有可用技能（先查后建）
- 需要对比自建与上游候选、评估技能质量与触发
- 需要为技能安装到 claude / opencode / codex / deepseek 客户端
- 用户提到过时关键词：「创建skill」「写个技能」「skill-creator」「把xx做成技能」「添加技能」

## 领域工作流（引导型：每步向用户确认后再执行）

### 第一步：查本地已验证库（先查后建）

用户要「一个做 X 的技能」时，**先读本地能力目录 `skills/CATALOG.md`**（由 `tools/scripts/build_catalog.py` 从各 `SKILL.md` frontmatter 自动生成，条目 = 已验证技能）判断本地是否已有合适能力：

- **本地有合适技能，且用户只是想用** → 让 LLM 读目录匹配，命中后给出条目的 `install` 命令（如 `python tools/scripts/install_skill.py skills/pr-summarizer`），**用户确认后**再执行。
- **本地有合适技能，但需改进** → 进入下方创建流程，以本地版为基座迭代。
- **本地无合适技能** → 进入下方创建决策流。

### 创建决策流（本地 × 上游，5 场景）

「先查后建」指**先本地 `skills/`、后上游索引**。5 场景决策（本地有/无 × 上游有/无 → 动作；场景 5 为上游更优）：

| 场景 | 本地 `skills/` | 上游索引 | 动作 |
|---|---|---|---|
| 1 | ✅ 有 | ✅ 有 | 两者对比取最优 → **最优的替换本地的** |
| 2 | ✅ 有 | ❌ 无 | 直接用本地的（跳过上游） |
| 3 | ❌ 无 | ✅ 有 | 创建后再与上游对比取最优 → **最优的放入 `skills/`** |
| 4 | ❌ 无 | ❌ 无 | 创建 → 用创建的放入 `skills/` |
| 5 | — | 上游更优 | 提炼学习点 → 记录到 `evolutions/` → 优化 skill-creator |

> 安装与回馈**永远以本地 `skills/<name>` 为源**；上游候选只用于「对比择优」，不直接安装（验证优先）。

### 检索上游（场景 1/3 需要时）

```bash
python skill-creator/scripts/search_index.py "<需求关键词>" [--category X] [--risk Y] [--limit 10]
```

有匹配候选 → 记录候选；无匹配 → 场景 2/4 直接使用本地。

### 对比择优（场景 1/3/5 有上游候选时）

```bash
python skill-creator/scripts/compare_skills.py <本地候选或新建> <上游候选目录>
```

- 上游更优 → 采纳最优（场景 1 替换本地 / 场景 3 放入 `skills/`）；提炼学习点记录到 `evolutions/`（反馈闭环）
- 自建更优或持平 → 用自建版本

### 创建（场景 3/4 需新建时）

```bash
python skill-creator/scripts/create_skill.py --name <技能名> --category <分类> --risk <级别>
```

frontmatter 必须含 `version: "0.1.0"`（生命周期记账用）。骨架生成后按 `SKILL.md` 阶段 4 完善正文。

### 自动验证

```bash
python skill-creator/scripts/validate_skills.py --strict --dir <技能目录>
```

失败必须修复后再继续；`--dir` 指定校验目录（默认扫描 `<repo>/skills/`）。

### 真实任务测试 + 触发测试

按 `SKILL.md` 阶段 6-7：先用真实场景跑一次技能，再运行触发测试：

```bash
python skill-creator/scripts/run_trigger_tests.py <技能目录> --evals <技能目录>/evals.json
```

（evals.json 从 `templates/evals.json.template` 复制）

### 安装到客户端

```bash
python tools/scripts/install_skill.py [--client <claude|opencode|codex|deepseek>] <技能目录>
```

安装后重启客户端生效；生命周期（更新/卸载/回滚）见 `tools/docs/lifecycle.md`。

### 回馈仓库

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

- **先查后建**：先查本地 `skills/`（`CATALOG.md`）再查上游，避免重复造轮子
- **验证优先**：未经 `validate_skills.py` 验证的技能不安装
- **引导不自动**：不代替用户执行安装/提交等副作用操作
- **回馈闭环**：「上游更优」的对比是学习机会（记录到 `evolutions/`）