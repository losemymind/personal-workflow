# 按需安装与能力目录方案（ON-DEMAND-INSTALL）

> 状态：**方案评审中（未实现）**。本文是规划文档：正文用普通字体的路径（如 skills/CATALOG.md、tools/scripts/build_catalog.py）均为**待交付产物**，尚未入库；反引号仅用于当前已存在的仓库路径。
> 相关：`docs/HANDOFF.md`（交接）、`docs/DEVELOPMENT-PLAN.md`（v1.0 开发计划）、`tools/docs/lifecycle.md`（生命周期）

## 1. 背景与问题

用户在使用 PersonalWorkflow 仓库时，希望**按需安装**本仓库已验证的 skills 与 agents，而不是手动翻目录、记忆命令。核心诉求：让宿主 LLM（claude / opencode / codex / deepseek）能根据一句自然语言需求，找到本地库里"合适的能力"，并给出可执行的安装路径。

### 范围边界（已确认）

- **AI 按需检索的源 = 本地 skills/ 与 agents/ 已验证库**（准入已由 strict 验证 + 真实试跑背书）。
- **两个上游库（aas= sickn33/agentic-awesome-skills、addy= addyosmani/agent-skills）只服务 skill-creator 的"创建/对比择优"流程**，不参与按需安装检索。上游候选必须先落地到 skills/、agents/（或在本方案 V1 范围外由用户显式确认），才可被安装。
- 现有 skill-creator **创建决策流**（本地查 → 建 → 上游查 → 对比 → 取最优回填）尚未写入引导文档，本方案一并补齐。

## 2. 方法选型与决策记录

对三种候选做过权衡（详见对话纪要）：

| | 方法1 索引+AI 全提取 | 方法2 纯清单 | 方法3 必装清单+AI 补 |
|---|---|---|---|
| 可发现性 | 弱（黑箱） | 强（一眼全览） | 中 |
| 维护成本 | 零 | 高（登记漂移） | 最高（两套） |
| 确定性/审计 | 差 | 好 | 基座好/补装差 |
| 覆盖面 | 自动覆盖新增 | 需登记 | 需登记 |
| 原则冲突 | 无（源已验证） | 无 | 撞"引导不自动" |

**采纳：方法2 为骨架 + 生成式消漂移 + AI 只做查询前端。**

- 用**自动生成**的能力目录替代"手写清单"：目录内容由脚本从各 SKILL.md/AGENT.md 的 frontmatter 生成，**事实源唯一**，无人工增量 → 消除登记漂移。
- **不做"必装"**（方法3 语义与个人库"按需启用"本质冲突：会无差别污染每个客户端的 config）。可选"批量推荐"见 §6.5，默认关闭。
- AI（宿主客户端 LLM）**只读目录做自然语言→条目匹配**，人类是唯一安装闸门，走现有安装器。

## 3. 目标架构

```
用户需求（自然语言）
   │
   ▼
宿主 LLM（claude/opencode/...）读能力目录   ← 只读，不自动执行
   │  skills/CATALOG.md · agents/CATALOG.md
   ▼
匹配条目 → 给出安装命令 + 风险/权限提示
   │
   ▼
用户确认（人类闸门）
   │
   ▼
python tools/scripts/install_skill.py skills/<name>   ← 现有安装器，不改
python tools/scripts/install_agent.py agents/<name>
   │
   ▼
manifest 记账 · 重启客户端生效
```

配套能力（本方案新增）：

- **生成器**（规划落点 tools/scripts/build_catalog.py）：扫描 frontmatter → 重写 skills/CATALOG.md 与 agents/CATALOG.md。
- **防漂移校验** `--check`：CI 内确认目录条目与 CATALOG 一一对应（skills/、agents/ 有 SKILL.md/AGENT.md 但目录缺条目即失败）。
- **引导更新**：根 `AGENTS.md`、skill-creator/AGENTS.md、agent-creator/AGENTS.md 增加"按需安装"入口与 5 场景创建决策流。
- **验证器配套**：validate_agents.py 将 CATALOG.md 加入文件排除名单（否则会被兜底扫描误判为代理定义）。

## 4. 能力目录（CATALOG.md）规范

### 4.1 文件形态与命名

- 两个独立文件：skills/CATALOG.md、agents/CATALOG.md。
- 文件名**大写**（延续"目录小写 + 文件大写"约定）；**自动生成、禁止手改**——顶部声明自动生成、勿手改，事实源 = 各 SKILL.md/AGENT.md frontmatter。
- README 仍写给人读的说明（用途/准入/结构），二者职责分离。

### 4.2 每个条目 schema（一个条目 = 一个二级标题 = 能力名）

锚点固定，便于 LLM 与脚本解析：

```text
## <name>

| 字段 | 值 |
|---|---|
| category | <frontmatter.category；缺省 未分类> |
| risk | <frontmatter.risk；缺省 unknown> |
| version | <frontmatter.version；缺省 -> |
| source | <frontmatter.source；缺省 -> |
| date_added | <frontmatter.date_added；缺省 -> |
| mode | <AGENT 专用：primary/subagent> |
| install | python tools/scripts/install_skill.py skills/<name> |

**用途**：<frontmatter.description>（AI 匹配主字段）
**触发器**：<SKILL.md 的"何时使用"首条提炼 / AGENT.md description 的关键调用场景>
```

- skill 与 agent 各自条目头字段不同（skill 无 mode），由生成器按类型输出对应模板。
- install 行永远指向真实目录相对路径（与仓库根 AGENTS.md 一致），AI 命中后原样输出即为可执行命令。

### 4.3 匹配规则（AI 查询前端）

- AI 在 CATALOG.md 的 name / category / 用途 / 触发器上做关键词与语义匹配，覆盖中文与英文（frontmatter description 常为中文）。
- 命中多个 → 列出前 2-3 条并简述差异让用户选；不确定归类时给 risk 提示。
- **只读不自动**：AI 不直接执行安装，输出命令 + 等待用户确认。
- 本地目录无命中 → 提示走 skill-creator 创建流程（见 §6.3），**不**把上游库当作安装源。

## 5. 生成器设计

### 5.1 build_catalog.py（规划落点 tools/scripts/）

```text
用法：
  python tools/scripts/build_catalog.py                 # 重写 skills/CATALOG.md + agents/CATALOG.md
  python tools/scripts/build_catalog.py --check         # 只校验不写盘（exit 0/1）
  python tools/scripts/build_catalog.py --verbose       # 打印每个条目的数据源
```

逻辑：

1. 扫 skills/*/SKILL.md、agents/*/AGENT.md（跳过 `.` 开头目录与 examples/）。
2. 解析 frontmatter（**轻量自解析**：约 30 行，只取本目录所需字段；**不 import 验证器**——避免工具间 import 脆弱与 sys.path hack）。
3. 缺省字段回填默认值（category→未分类 等），保证条目 schema 完整。
4. 触发器提炼：对 skill 从"何时使用"小节取第一段非空行；对 agent 从 description 提取（V1 简化：可整段引用 description，或留 见 SKILL.md）。
5. 按 name 排序写入，保持幂等（同一仓库内容两次生成 diff 为空）。

### 5.2 `--check` 防漂移

- 读盘 CATALOG 条目集合 vs 目录实际 SKILL.md/AGENT.md 集合，二者差集非空即失败。
- 用途：CI 里跑，防止"回馈了新技能却忘跑生成器"导致目录过期。

## 6. 与现有流程的衔接

### 6.1 与生命周期工具

- **不改**安装器 / update / uninstall / rollback / manifest 机制——安装器接受任意目录，skills/、agents/ 下的目录天然是合法源目录。
- CATALOG 只是"发现层"，安装后一切照旧走 manifest 记账。

### 6.2 与验证器 / 引用检查

- validate_agents.py：agents/CATALOG.md 会被"无 AGENT.md 时扫 *.md"的兜底逻辑误扫为代理定义（名字不在现有 readme/changelog 排除名单）。需在该排除名单加入 `catalog.md`（`conftest.py` 的 AGENT_FIXTURE 侧不受影响）。
- validate_skills.py：只扫 SKILL.md，天然忽略 CATALOG.md，无需改。
- check_docs_refs.py：CATALOG 条目内的反引号引用（skills/ 下真实目录、安装命令首 token）均指向已跟踪真实路径，应零误报；新增真实回馈后保持与 git 索引一致即可。

### 6.3 与 skill-creator 创建决策流（一并补齐方法论）

用户说"要一个做 X 的技能"时，skill-creator 引导现缺"先本地查"步骤。补入 skill-creator/AGENTS.md 工作流与 SKILL.md 阶段 0-2 描述，形成 5 场景闭环：

1. 本地 skills/ 有 → 查上游索引，有 → 对比取最优 → **最优的替换本地的**。
2. 本地有 → 上游索引无 → **用本地的**。
3. 本地无 → 按需创建 → 查上游索引，有 → 对比取最优 → **最优的放入 skills/**。
4. 本地无 → 创建 → 上游索引无 → **用创建的放入 skills/**。
5. 上游更优 → **记入 skill-creator/evolutions/**，提炼学习点反哺 skill-creator 方法论。

场景 1/3 的"本地查找"第一步即读 skills/CATALOG.md（命中"已有"）；场景 3/4 才允许创建并触碰上游库。安装侧只认 skills/、agents/（结果归属地），上游库永不出现在安装命令里——与 §1 边界一致。

### 6.4 入口引导更新（各 AGENTS.md）

- 根 AGENTS.md「标准工作流」前插一小节「按需安装已有能力」：需求若是"用现成能力"→ 让 LLM 读对应 CATALOG.md 匹配 → 确认后 install。
- skill-creator/AGENTS.md：工作流第 1 步改"先读 CATALOG 查本地"再查上游；新增"按需安装"链接与 5 场景决策摘要。
- agent-creator/AGENTS.md：同构（读 agents/CATALOG.md）。
- 全部为**指引型**（描述路径 + 引用命令，不自动执行安装）。

### 6.5 可选"批量推荐"（V1 不做，预留）

不做全库必装。如需开箱基座，未来可在安装器加 `--from-catalog <list>`（逐项 dry-run 供确认），默认保持人工逐条确认。本节仅记录方向，避免范围蔓延。

## 7. 工作分解（WBS，按序）

| # | 工作项 | 落点 | 验收 |
|---|---|---|---|
| W1 | build_catalog.py（生成 + --check） | tools/scripts/ | 对当前库生成两文件；重复执行幂等；`--check` 通过 |
| W2 | CATALOG.md 初版入库 | skills/CATALOG.md、agents/CATALOG.md | 与现状各 1 条目精确对应；通过 §8 三件套 |
| W3 | validate_agents.py 排除名单加 `catalog.md` | agent-creator/scripts/validate_agents.py | agents/ 库 strict 通过且 CATALOG.md 不被当代理 |
| W4 | 5 场景决策流补入方法论 | skill-creator/AGENTS.md、skill-creator/SKILL.md | 引导含 5 场景表 + 本地查前置 |
| W5 | 按需安装入口更新三处 AGENTS.md | 根 + skill-creator/ + agent-creator/ | 用户可按指引让 LLM 读目录给出安装命令 |
| W6 | 补测试 | tests/ | CATALOG 生成/校验单测 + validate_agents 排除单测 |
| W7 | 端到端手测 | 本仓库 | 模拟需求 → LLM 读目录命中 → dry-run 安装 → manifest 正确 |

## 8. 防回归三件套（每次改动必跑）

```text
python -m pytest tests/ -q
python tools/scripts/check_docs_refs.py
python skill-creator/scripts/validate_skills.py --strict --dir skills
python skill-creator/scripts/validate_skills.py --strict --dir skill-creator
python agent-creator/scripts/validate_agents.py --strict --dir agents
```

CI（`.github/workflows/validate.yml`）追加一行 build_catalog.py --check 防目录漂移。

## 9. 风险与缓解

| 风险 | 缓解 |
|---|---|
| CATALOG 与目录漂移 | `--check` 进 CI；生成器幂等；文件头声明勿手改 |
| agents/CATALOG.md 被误判为代理 | W3 排除名单；W6 单测锁行为 |
| LLM 误装（命中到不想要的能力 / 覆盖已有） | 安装器已拒覆盖已存在目录（FileExistsError，需 update/uninstall）；AI 只给命令不执行；提示 risk |
| 上游库被当作安装源（范围蔓延） | AGENTS 引导显式声明"上游只在创建对比流程使用"；安装命令一律 skills/、agents/ 相对路径 |
| AI 对中文/英文触发词匹配不稳 | 匹配主字段为 description（frontmatter 双语触发区）+ CATALOG 触发器列提炼 |
| 未来文件在 check_docs_refs 报错 | 本文规划路径用普通字体（非反引号）；产物入库后自然通过 |

## 10. 验收标准

1. 生成器对当前仓库生成 skills/CATALOG.md 与 agents/CATALOG.md，条目与目录一一对应且幂等。
2. 按 §6.4 更新后，对 LLM 说"我需要在合并前审查代码"，能读目录命中 code-reviewer（agents）并给出 install_agent.py agents/code-reviewer；说"把 diff 变成 PR 总结"能命中 pr-summarizer（skills）。
3. validate_agents.py `--strict` 不把 CATALOG.md 当代理定义。
4. §8 三件套 + CI 全部通过；生成器 `--check` 绿。
5. 安装/更新/卸载/回滚行为与 V1 完全一致（本方案不改安装器）。
