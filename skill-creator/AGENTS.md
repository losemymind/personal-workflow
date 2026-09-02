# skill-creator AGENTS 引导（技能领域入口）

本文件是 **PersonalWorkflow 技能领域** 的入口（总编排见仓库根 `AGENTS.md`）。当任务涉及**创建/改进/验证/对比/安装技能**时，从总编排进入本文件，按此引导执行；细节方法论在 `SKILL.md`，规范在 `references/`（渐进式披露：按需读取，不一次全部加载）。

## 何时进入本文件

- 用户要求「把某个工作流做成技能」「创建一个 skill」「改进现有技能」
- 需要检索上游是否已有可用技能（先查后建）
- 需要对比自建与上游候选、评估技能质量与触发
- 需要为技能安装到 claude / opencode / codex / deepseek 客户端
- 用户提到过时关键词：「创建skill」「写个技能」「skill-creator」「把xx做成技能」

## 领域工作流（引导型：每步向用户确认后再执行）

### 1. 检索上游（先查后建）

```bash
python skill-creator/scripts/search_index.py "<需求关键词>" [--category X] [--risk Y] [--limit 10]
```

- 有匹配候选 → 记录候选，继续第 2 步
- 无匹配 → 跳到第 3 步创建

### 2. 对比择优（有候选时）

```bash
python skill-creator/scripts/compare_skills.py <本地候选或新建> <上游候选目录>
```

- 上游更优 → 建议采纳上游；提炼学习点记录到 `evolutions/`（反馈闭环）
- 自建更优 → 用自建版本

### 3. 创建（脚手架）

```bash
python skill-creator/scripts/create_skill.py --name <技能名> --category <分类> --risk <级别>
```

frontmatter 必须含 `version: "0.1.0"`（生命周期记账用）。骨架生成后按 `SKILL.md` 阶段 4 完善正文。

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

技能稳定后：完善元数据（source/date_added/version/tags）→ 放入 `skills/<name>/` → 提交（含 `evolutions/` 对比记录）。

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

## 与总编排的关系

- 仓库根 `AGENTS.md` 是个人工作流**总编排**（技能+代理+工具三域）
- 本文件只负责**技能领域**：任务归属技能时在此聚焦，避免总编排信息过载
- 属于「代理/工具」的任务回到总编排按对应入口执行（`agent-creator/AGENTS.md`、`tools/`）

## 原则（与总编排一致）

- **先查后建**：永远先检索上游再创建
- **验证优先**：未经 `validate_skills.py` 验证的技能不安装
- **引导不自动**：不代替用户执行安装/提交等副作用操作
- **回馈闭环**：「上游更优」的对比是学习机会（记录到 `evolutions/`）