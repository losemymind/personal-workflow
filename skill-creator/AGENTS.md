# skill-creator AGENTS 引导（技能创建器）

skill-creator 是一个**可独立安装**到 LLM 客户端（claude / opencode / codex / deepseek）的**技能创建器**：把用户的真实工作流蒸馏为可复用、可验证、跨客户端安装的高质量技能（Skill）。它自带上游索引检索、脚手架、对比评分、自动验证与触发测试，走**检索上游 → 创建 → 对比择优 → 验证 → 测试 → 安装 → 回馈**的完整闭环。

> 本文件是 skill-creator 自身的使用引导，随技能一起安装、独立生效；用户或宿主需要创建/改进技能时按本引导执行。完整方法论见 `SKILL.md`（10 阶段），规范在 `references/`（渐进式披露：按需读取，不一次全部加载）。

## 何时使用本技能

- 用户要求「把某个工作流做成技能」「创建一个 skill」「改进/重构现有技能」
- 需要先检索上游看是否已有同类技能（先查后建，避免重复造轮子）
- 需要评估技能触发准确性与质量、运行自动验证
- 需要把技能安装到 claude / opencode / codex / deepseek 客户端的 skills 目录
- 用户提到触发词：「创建skill」「写个技能」「skill-creator」「把xx做成技能」「添加技能」「改进这个技能」

## 工作流（引导型：每步向用户确认后再执行）

### 1. 检索上游（先查后建）

动手创建前，先在本地上游索引中检索是否已有可用技能：

```bash
python scripts/search_index.py "<需求关键词>" [--category <分类>] [--risk <级别>] [--limit 10]
python scripts/search_index.py --stats                # 索引状态
python scripts/search_index.py --list-categories      # 分类分布
```

- 索引文件 `indexes/upstream.db` 已随技能分发，无需联网。
- 索引落后于上游时运行 `python scripts/build_index.py` 重建。
- **有匹配候选** → 记录候选，照常创建，在第 4 步与候选对比择优。
- **无匹配候选** → 跳过对比，用自建版本。

### 2. 创建（脚手架）

先按 `SKILL.md` 阶段 1-2 捕捉用户实际做过的工作与「唯一人力决策点」（不确定就向用户逐条确认），再生成骨架：

```bash
python scripts/create_skill.py --name <技能名> --category <分类> --risk <级别> [--out <目录>]
```

frontmatter 必须含 `version: "0.1.0"`（生命周期记账用）。骨架生成后按 `SKILL.md` 阶段 4 完善正文（概述 → 何时使用 → 工作原理 → 示例 → 限制）。

### 3. 与上游候选对比择优（有候选时）

将自建技能与上游候选结构化对比（质量 6 维 + 结构 4 维）：

```bash
python scripts/compare_skills.py <自建目录> <上游候选目录>
```

- **上游更优** → 采纳上游；提炼学习点记入 `evolutions/`，反哺优化本技能方法论（反馈闭环）。
- **自建更优或持平** → 用自建版本。

### 4. 自动验证

```bash
python scripts/validate_skills.py [--strict] [--dir <技能目录>]
```

失败必须修复后再继续。检查项（详见 `references/quality-bar.md`）：frontmatter 有效性、`name` 与目录一致、risk/version 合法、何时使用/示例/限制章节、安全护栏、引用不悬空。

### 5. 真实任务测试 + 触发测试

按 `SKILL.md` 阶段 5-7：**确定性脚本打底 + 拉起子代理判断（`agents/`）+ 脚本聚合收尾**：

```bash
# 触发测试（两档：启发式默认 / 真实客户端无头 CLI）
python scripts/run_eval.py --eval-set <技能目录>/evals.json --skill-dir <技能目录>
python scripts/run_eval.py --eval-set <技能目录>/evals.json --skill-dir <技能目录> --mode cli --client claude
python scripts/run_loop.py --eval-set <技能目录>/evals.json --skill-dir <技能目录> --improve-mode manual|cli
# 聚合（--notes 合并分析子代理的观察笔记）
python scripts/aggregate_benchmark.py <workspace>/iteration-N --skill-name <技能名> [--notes <notes文件>]
```

（evals.json 从 `templates/evals.json.template` 复制；给出触发准确性启发式信号）

语义判断由子代理完成：输出打分拉起 `agents/grader.md`（写 `grading.json`），定性对比拉起 `agents/comparator.md`（A/B 盲测），基准模式分析拉起 `agents/analyzer.md`（产出笔记数组，经 `--notes` 并入 `benchmark.json`）。客户端无子代理派发时由主持会话按同一份指令内联完成，产物格式不变。

### 6. 安装到客户端

将技能目录放置到目标客户端的安装目录；按客户端文档说明完成注册。

安装后重启客户端生效；后续更新/卸载/回滚由客户端工具或独立管理脚本处理。

### 7. 回馈稳定技能

技能稳定后：完善元数据（source/date_added/version/tags）→ 归档到技能库/可分发目录 → 含 `evolutions/` 对比记录一并沉淀。

## 资源路径基准

本技能是**自包含完整体**：内部所有引用（`scripts/`、`references/`、`templates/`、`examples/`、`evolutions/`、`agents/`、`indexes/upstream.db`）一律以 **skill-creator 目录自身为根**书写，不依赖任何外部布局。脚本调用：在本技能目录内执行 `python scripts/xxx.py ...`；不在技能目录内执行时加目录前缀 `python "<技能目录>/scripts/xxx.py" ...`（目录定位方法见 SKILL.md「资源路径基准」）。

读取规则：references 文档**按需读取**；需要字段/分类时读 `references/skill-template.md`，结构规范读 `references/skill-anatomy.md`，质量标准读 `references/quality-bar.md`，写作规律（TDD 化/表述匹配失败类型/防借口）读 `references/skill-writing-guide.md`，索引细节读 `references/skill-index.md`，对比评分读 `references/skill-comparison.md`。

## 资源导览（按需读取）

| 资源 | 何时读取 |
|---|---|
| `SKILL.md` | 任务开始时：完整方法论（10 阶段工作流） |
| `references/skill-template.md` | 需要字段/分类/风险级别细节时 |
| `references/skill-anatomy.md` | 需要结构规范/渐进式披露时 |
| `references/quality-bar.md` | 需要质量标准/验证器检查项时 |
| `references/skill-writing-guide.md` | 编写/改进技能正文时：写作规律（TDD 化、表述匹配失败类型、防借口、措辞微测、description 触发面） |
| `references/skill-index.md` | 需要索引构建/检索/增量同步说明时 |
| `references/skill-comparison.md` | 进行对比择优时 |
| `references/benchmark-schema.md` | 做量化基准（run_eval / run_loop / aggregate_benchmark 的 JSON 结构）时 |
| `agents/grader.md` | 需要给运行产物打断言分时（拉起子代理或内联执行）→ `grading.json` |
| `agents/comparator.md` | 需要定性盲测比较两份输出时 → `comparison.json` |
| `agents/analyzer.md` | 复盘盲测胜因（模式一）或分析基准模式产笔记（模式二）时 |
| `examples/` | 创建前研究结构范本（上游学习样本，验证豁免） |
| `evolutions/` | 记录"上游更优"对比结论（反馈闭环） |
| `templates/` | `SKILL.template.md`（骨架）、`evals.json.template`（触发测试模板） |
| `indexes/upstream.db` | 检索上游（随技能分发，安装即得） |

## 其他创建器

- `agent-creator` — 同构的代理创建器（技能沉淀到一定规模后，可升级为专职 Agent）
- 技能 vs 代理取舍：可描述的步骤化流程 → 技能（本技能）；需要常驻角色/权限/协作 → 代理（`agent-creator`）

## 设计原则

- **先查后建**：先检索上游是否已有同类，避免重复造轮子
- **验证优先**：未经 `validate_skills.py` 验证的技能不安装/不回馈
- **引导不自动**：只给路径与命令，不代替用户执行安装/提交等副作用操作
- **回馈闭环**：每次"上游更优"的对比都是学习机会（记入 `evolutions/`，反哺本技能）
