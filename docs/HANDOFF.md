# PersonalWorkflow 交接文档（HANDOFF）

> 用途：新会话快速恢复上下文。读完本文件即可接手开发。
> 生成日期：2026-09-04 ｜ 最近提交见 `git log --oneline -5`（基线：本轮「交接提示语输出经验（可整段复制代码块 + 自包含内容）写入根 AGENTS 与本文件 §6」提交；上一轮为「skill-creator 全面审计 10 项修复 + 生命周期三缺陷修复」4c0f4d7）
## 1. 这是什么

个人工作流工具库，跑通 **检索上游 → 创建 → 对比择优 → 验证 → 安装 → 回馈** 的完整闭环。支持四个 LLM 客户端：**claude / opencode / codex / deepseek-harness**。仓库远程：`https://github.com/losemymind/personal-workflow.git`（分支 `main`）。

## 2. 顶层架构（总编排 → 独立生产器）

```
AGENTS.md                 # 总编排/分发入口：判定需求→按需安装 或 调用生产器→谁优用谁
├── skill-creator/            # 独立技能「技能生产器」（自含 AGENTS.md 引导 + SKILL.md 方法论）
│   └── AGENTS.md / SKILL.md  #   闭环：创建 → 检索上游对比 → 上游更优反哺自身（不含上层编排）
├── agent-creator/            # 独立技能「代理生产器」（同构，闭环：创建→验证→测试→安装）
│   └── AGENTS.md / SKILL.md
├── tools/docs/lifecycle.md   # 安装/生命周期通用入口
├── skills/               # 已验证技能库（分类化：git/pr-summarizer、development/code-review-skill；生成器内部另有 examples/）
├── agents/               # 已验证代理库（分类化：ue-game-studio×25、academic×5、code-quality×2，共 32 个；无「留顶层」）
├── tools/scripts/        # 四端双作用域安装器（global/workspace）+ 生命周期 + 能力目录生成器（manifest-driven）
├── tests/                # pytest（42 用例，覆盖验证器/路径矩阵/作用域/生成器/生命周期/quant eval）
├── .github/workflows/validate.yml  # CI：双验证器 --strict + pytest + 文档引用 + 目录同步
└── docs/                 # DEVELOPMENT-PLAN.md（开发计划）、HANDOFF.md（本文件）、AGENTS-AUDIT.md（代理审计）、SKILLS-AUDIT.md（技能审计）、ON-DEMAND-INSTALL.md（按需安装方案）
```

**核心原则**：先查后建（**先本地 `skills/CATALOG.md`/`agents/CATALOG.md`、后上游索引**）→ 引导不自动（AGENTS.md 只指引）→ 验证优先 → 回馈闭环（`evolutions/` 记录"上游更优"的学习点）。

**按需安装**：`skills/CATALOG.md` 与 `agents/CATALOG.md` 由 `tools/scripts/build_catalog.py` 从各 frontmatter 自动生成（勿手改，CI `--check` 防漂移），是 LLM 读目录匹配需求 → 给出 `install` 命令的机器可读清单。**上游索引只服务两个生产器内部的"创建/对比择优"，不是安装源**——skill-creator 查技能索引（aas/addy），agent-creator 查代理索引（agency/ccgs/agency-zh）。

> **职责分层**：skill-creator/agent-creator 是**可独立安装的技能**（与上层编排无耦合，自身闭环完整）；"是否调用生成器"与"本地候选 A vs 生成 B 谁优用谁"均由**根 AGENTS（总编排）**判定——编排逻辑只写在这一个文件，不写入生成器目录。

## 3. 已交付能力（按模块）

### skill-creator（技能生产器，最成熟）
- `SKILL.md`：10 阶段方法论（阶段 0 检索上游 → 9 安装回馈）
- 上游**双源 SQLite 索引** `skill-creator/indexes/upstream.db`（2132 技能）：
  - `aas` = sickn33/agentic-awesome-skills（2107，官方索引）
  - `addy` = addyosmani/agent-skills（25，目录扫描）
- 脚本：`search_index.py`（检索/--source/stats）、`build_index.py`（多源/增量）、`compare_skills.py`（质量6维+结构4维评分）、`create_skill.py`（脚手架）、`validate_skills.py`（严格验证）、`run_trigger_tests.py`（触发启发式）
- `references/`：template/anatomy/quality-bar/index/comparison/**skill-writing-guide**（写作规律：TDD 化·表述匹配失败类型·防借口·措辞微测——反哺自 obra/superpowers writing-skills）
- `examples/`：6 个上游学习样本（MIT，验证豁免）；`evolutions/`：对比学习记录（pr-summarizer、2026-09-03 借鉴 Anthropic 官方量化 eval 引擎、code-review-skill 导入、**2026-09-03 采纳 superpowers writing-skills 方法论**）
- 量化 eval 引擎（移植自 Anthropic claude-plugins-official）：`scripts/run_eval.py`（heuristic/cli 双模式；`--output-dir` 落盘 `eval-results-<名>.json`）、`run_loop.py`（description 自动优化，train/test 60/40 防过拟合）、`aggregate_benchmark.py`（benchmark.json+md，纯 stdlib；`--notes` 合并分析笔记）、`references/benchmark-schema.md`（schema）——全部客户端无关，默认 heuristic 无需外部 CLI；**职责边界**：run_eval 只产触发判定信号，评分工作区布局由编排层搭建
- **eval agent 编排（2026-09-04 移植自官方）**：`skill-creator/agents/grader.md`（断言打分→grading.json）、comparator.md（盲测 A/B→comparison.json）、analyzer.md（复盘改进建议 / 基准模式笔记）——由 SKILL.md 阶段 5/5.5/6 按需拉起子代理执行（语义判断），脚本负责确定性聚合；客户端无子代理派发时主持会话按同一份指令内联完成。记录 `evolutions/2026-09-04-adopt-official-agent-orchestration.md`
- **description 上限 1024**：验证器/模板/质量条/参考全部统一（触发场景优先 + 一句能力定位，禁流程摘要——E 规律）；`description = 何时用不是做什么`
- `INSTALL.md`：安装运行手册（第 0 步问全局/工作区 → 3 端落点 → 3 道验证关卡 → 交付；手册自身也自包含，不引用外部工具）
- **自包含完整体**：内部所有引用以技能目录为根（`python scripts/...`、`references/...`、`<技能目录>/indexes/upstream.db`），不引用任何外部资源/文档；「资源路径基准」含各端目录定位规程
- 验证器安装可移植：支持 `--dir .`（安装副本自校验）；模块式自指引用（`<技能名>/...` 前缀）按技能目录解析
- `opencode.json` 已注册 `skills.paths = ["skill-creator", "agent-creator"]`

### agent-creator（代理生产器）
- `SKILL.md`：身份先于指令 / 最小权限 / 协作协议 / 升级路径 / 独立安装（不含上层编排）
- 上游**三源 SQLite 索引** `agent-creator/indexes/upstream.db`（568 代理）：
  - `agency` = msitarzewski/agency-agents（258，division 目录扫描）
  - `ccgs` = Donchitos/Claude-Code-Game-Studios（49，.claude/agents 扫描）
  - `agency-zh` = jnMetaCode/agency-agents-zh（261，中文版，含公司/法务/HR/供应链等 division）
- 脚本：`search_agent_index.py`（检索/--source/stats/--list-categories，含 CJK LIKE 兜底）、`build_agent_index.py`（多源构建/--from-extracted）、`compare_agents.py`（自建 vs 上游对比，质量6维+结构4维，`--all-candidates`/`--json`）、`create_agent.py`（脚手架）、`validate_agents.py`（边界/权限/协作/链接校验）
- `references/`：agent-template（四端兼容矩阵）/ agent-anatomy / agent-quality-bar / agent-index（索引说明）/ agent-comparison（对比择优评分维度，与 skill-comparison 同构）
- `evolutions/`：对比学习记录（与 skill-creator 同构，模板见 README）
- `INSTALL.md`：同构安装运行手册（验证关卡 = 索引 568 条 + 脚手架过 `--strict` + 资源就位）
- **自包含完整体**：与 skill-creator 同规（引用以技能目录为根）；SKILL.md「多客户端安装指引」含产出代理的 4 端落点矩阵（claude `~/.claude/agents/`、opencode `~/.config/opencode/agent/`、codex/deepseek best-effort）

### tools（分发与生命周期）
- `client_paths.py`：四端**双作用域**路径矩阵（global/workspace，唯一事实源）。已修正两处实证错误：Windows 配置根为 `~/.config`（opencode **不读** `%APPDATA%\opencode`，曾致 pr-summarizer/code-reviewer 装了不加载）；codex skills 为 `~/.agents/skills`（USER 域；`~/.codex/skills` 是 SYSTEM 域，禁写）。拷贝排除 `__pycache__`；客户端检测增强（`~/.claude`/`~/.codex` 存在即视为已装）
- `install_skill.py`：四端安装（manifest 标记 `.personal-workflow-manifest.json`）；`--scope global|workspace`，未指定时交互询问；工作区强制装到 git 仓库根（三端从 cwd 向上扫描到仓库根），非仓库环境礼貌报错。`install_agent.py` 尚未加 --scope（同构待补）
- `build_catalog.py`：能力目录生成器（`skills/CATALOG.md` + `agents/CATALOG.md`，`--check` 防漂移；agent 条目渲染 `maturity` 字段；**递归扫描子目录** `agents/**/AGENT.md`，agent 条目按顶层类别分组渲染——`ue-game-studio` / `academic` / `code-quality`，无「留顶层」例外）
- `update/uninstall/rollback_skill.py` + `_agent.py`：生命周期（备份仅 update 产生至 `~/.personal-workflow/backups/`，卸载不备份、回收因此变空的父目录）；工作区安装的生命周期用 `--dest <项目根>/<端目录>`；manifest `source` 记录真实安装来源（非安装目标）
- `check_docs_refs.py`：md 引用与 git 索引的大小写敏感校验（零误报）；含「模块根探针」（自包含模块子目录文档的引用按模块根解析，如 `skill-creator/references/` 中的裸引用 indexes/upstream.db 解析为 `skill-creator/indexes/upstream.db`）
- deepseek 路径为 best-effort（`DEEPSEEK_HARNESS_ROOT` 覆盖），未实测

### 按需安装 + 创建决策（能力目录）
- `skills/CATALOG.md` / `agents/CATALOG.md`：本地已验证能力清单（LLM 检索 → 命中给 install 命令 → 人类确认）
- **职责分层**：skill-creator/agent-creator 是可独立安装的生产器（闭环 = 创建 → 检索上游对比 → 上游更优反哺自身 `evolutions/`，目录内不含上层编排）；**编排只在根 AGENTS**：查本地候选 A → 无论有无都调生成器产出 B → A vs B 谁优用谁
- agent 字段 schema 与 skill 不同：agent 无 category/source/date_added，用 mode/tags 分类；另有 `maturity` 字段分两档：`runtime-verified`（真实试跑过）/ `static-verified`（仅静态 --strict，待运行时验证）——`build_catalog.py` 会把该字段渲染进 CATALOG 条目

### 外部库迁移（UEGameStudio → agents/）
- 来源：`E:\GitHub\UEGameStudio\UEGameStudio\agents`（30 代理，7 层：academic×5 / design×3 / directors×4 / orchestration×1 / production×3 / qa×3 / technical×11）
- 结构：6 个层（design/directors/orchestration/production/qa/technical，25 代理）迁入 `agents/ue-game-studio/<layer>/<id>/AGENT.md`（UE 专用安装包）；`academic/`（5 代理）作为**公共代理**保留在 `agents/academic/`（**层内不以 `academic-` 作前缀**，如 `anthropologist/`）；通用代理 code-reviewer / code-simplifier 归入 `agents/code-quality/`（代码质量分类，无「留顶层」例外）
- 自包含：包内文件**已去除对 UEGameStudio 源仓库的引用**（AGENTS.md/README.md 改写为自包含描述）；包内引用公共代理用包相对路径 `../academic/<agent>`（仓库根视角 `agents/academic/<agent>`），经 `Test-Path` 验证可解析；包文件 = `AGENTS.md`（协作规则）+ `README.md`（安装清单 + 冲突处理：冲突让用户选择保留哪一个，确认前不覆盖）
- 适配：保留全部正文与 frontmatter；补 `name`/`version`/`tags[maturity]`；`完成检查`→`完成标准`；注入 职责范围(必须做/拒绝做)/工具与权限/协作协议(升级交还) 指针化章节——全部通过 `validate_agents.py --strict`（31/31 含 code-reviewer）
- `domain` 标签：统一为 `ue-game-studio`（30 个全部）；layer 保留原 7 层；目录放置与 `layer` 标签一致
- 状态：全部 `static-verified`（仅静态），仅 code-reviewer 为 `runtime-verified`；真实 UE Editor / 运行时验证待后续

### 入库准入规则 + 审计文件（2026-09-03 新增）
- 根 `AGENTS.md` 新增「入库准入规则」四条硬性约束：
  1. 入库 `agents/` 的代理**无论参考本地文件还是远程仓库，必经 agent-creator**，并在 `docs/AGENTS-AUDIT.md` 登记
  2. 入库 `skills/` 的技能**无论参考本地文件还是远程仓库，必经 skill-creator**，并在 `docs/SKILLS-AUDIT.md` 登记
  3. 参考外部仓库的代理/技能必须在对应审计文件中**标注数据来源**
  4. 分类目录必入：**按功能归入分类文件夹，分类不存在则创建；无「留顶层」例外**（2026-09-03 起 code-reviewer / code-simplifier 已迁入 `agents/code-quality/`）
- `docs/AGENTS-AUDIT.md` / `docs/SKILLS-AUDIT.md`：数据来源与入库合规的**唯一记录入口**；新增/迁移/改进/整改能力后必须同步更新
- **审计现状**：**32 个代理全部合规**——code-reviewer 创建时经 agent-creator；academic×5 + ue-game-studio×25 于 2026-09-03 逐一补走 agent-creator 对比择优（上游 agency/ccgs/agency-zh 比对，结论自建更优/持平），证据见 `agent-creator/evolutions/2026-09-03-compare-migrated-ue-agents.md`；code-simplifier 于同日经官方仓库导入+对比（0.86 vs 0.48）转合规；pr-summarizer + code-review-skill 均合规（2 技能）

### 文档质量
- 根 `AGENTS.md` 为总编排；`skill-creator/AGENTS.md` / `agent-creator/AGENTS.md` 为各自独立技能引导（随技能分发）
- 各 README 结构树与实际文件已对齐（曾全量核对过一轮）
- 关键点：**文件名大小写敏感**（目录小写 + `SKILL.md`/`AGENT.md`/`AGENTS.md` 大写）——Windows 开发时易踩坑，克隆到 Linux 会断链，务必用 `git ls-files` 校验引用

## 4. 常用命令速查

```bash
# 按需安装已有能力（先查后建：本地优先）—— 让 LLM 读目录匹配，命中给 install 命令
#   skills/CATALOG.md  ·  agents/CATALOG.md
# 安装器未指定 --scope 时会交互询问全局/工作区；创建器安装按各自 INSTALL.md 执行
python tools/scripts/install_skill.py [--client opencode|claude|codex|deepseek] [--scope global|workspace] skills/<name>
python tools/scripts/install_agent.py [--client opencode|claude|codex|deepseek] agents/ue-game-studio/<layer>/<name>   # UE 包内 agent
python tools/scripts/install_agent.py [--client opencode|claude|codex|deepseek] agents/academic/<name>                 # 公共学术代理
python tools/scripts/install_agent.py [--client opencode|claude|codex|deepseek] agents/<顶层分类>/<name>            # 分类内代理

# 能力目录：生成 / 校验（新增回馈后跑，CI 用 --check）
python tools/scripts/build_catalog.py
python tools/scripts/build_catalog.py --check

# 检索上游（仅技能创建对比时）—— 默认全库，--source aas|addy 过滤
python skill-creator/scripts/search_index.py "<关键词>" [--source addy] [--category X]

# 检索上游代理（仅代理创建对比时）—— --source agency|ccgs|agency-zh，支持中文
python agent-creator/scripts/search_agent_index.py "<关键词>" [--source agency-zh] [--category X]
python agent-creator/scripts/search_agent_index.py --stats / --list-categories

# 索引：重建/增量（技能 / 代理同构；代理为三源）
python skill-creator/scripts/build_index.py [--source all|aas|addy] [--incremental]
python skill-creator/scripts/build_index.py --source addy --from-extracted <本地仓库>
python agent-creator/scripts/build_agent_index.py [--source all|agency|ccgs|agency-zh]
python agent-creator/scripts/build_agent_index.py --source agency --from-extracted <本地仓库>

# 创建/验证
python skill-creator/scripts/create_skill.py --name x --category git --risk safe --no-interactive
python skill-creator/scripts/validate_skills.py --strict --dir skills/x
python agent-creator/scripts/create_agent.py --name x --mode subagent --no-interactive
python agent-creator/scripts/validate_agents.py --strict --dir agents/x

# 对比择优（有上游候选时）
 python skill-creator/scripts/compare_skills.py <自建目录> <上游目录>
 python agent-creator/scripts/compare_agents.py <自建目录> <上游目录>

# 量化基准（脚本打底 → 拉起子代理判断 → 脚本聚合收尾；子代理指令在 skill-creator/agents/）
python skill-creator/scripts/aggregate_benchmark.py <workspace>/iteration-N --skill-name <名> [--notes <分析笔记json>]

# 生命周期
python tools/scripts/update_skill.py <名> --source <新版>   # 代理用 _agent 版同构
python tools/scripts/uninstall_skill.py <名>
python tools/scripts/rollback_skill.py <名>

# 测试/CI 等价
python -m pytest tests/ -q          # 42 用例
python tools/scripts/check_docs_refs.py   # 文档引用完整性（exit 0）
python tools/scripts/build_catalog.py --check   # 目录同步检查（exit 0）
```

## 5. 当前状态与未完成事项

| 项 | 状态 |
|---|---|
| 技能双源索引（aas+addy，2132 技能） | ✅ 已重建入库 |
| **代理三源索引（agency+ccgs+agency-zh，568 代理）** | ✅ 已入库（agent-creator/indexes/upstream.db，含中文 agency-zh） |
| 中文检索（CJK LIKE 兜底） | ✅ search_index / search_agent_index 均支持中文关键词 |
| 首个入库技能/代理（pr-summarizer / code-reviewer） | ✅ 已验证并安装到 opencode |
| **外部库迁移：UEGameStudio 30 代理** | ✅ 6 层（25 代理）入 `agents/ue-game-studio/<layer>/`，academic 5 个保留 `agents/academic/`（公共，层内无 `academic-` 前缀）；包内已自包含（无 UEGameStudio 源引用），公共代理用 `../academic/` 相对路径引用；31/31 strict 通过 |
| **能力目录递归 + 分组** | ✅ build_catalog.py 递归扫 `agents/**/AGENT.md`，agent 条目按顶层类别分组渲染（`ue-game-studio` / `academic` / `code-quality`），install 路径含层前缀；无「留顶层」例外 |
| agent 生命周期（update/uninstall/rollback） | ✅ 已补齐（目录+单文件形态） |
| CI（strict 验证 + pytest + 文档检查 + 目录同步） | ✅ 已配置 |
| 按需安装 + 创建决策（分层） | ✅ CATALOG.md 生成器 + 生产器独立化（闭环 3 步，不含编排）+ 编排收敛到根 AGENTS（A vs B 谁优用谁） |
| agent-creator evolutions | ✅ 首个真实记录：`2026-09-03-compare-migrated-ue-agents.md`（30 个迁移代理批量对比，全部自建更优/持平） |
| skill-creator evolutions | ✅ 反馈闭环记录：`2026-09-03-borrow-upstream-quant-eval.md`（Anthropic 官方量化 eval）、`2026-09-03-import-code-review-skill.md`、`2026-09-03-adopt-superpowers-writing-skills.md` |
| **量化 eval 引擎（移植自 Anthropic 官方）** | ✅ `scripts/run_eval.py`（heuristic/cli）、`run_loop.py`（train/test 60/40 优化）、`aggregate_benchmark.py`（benchmark.json+md，`--notes` 合并分析笔记）、`references/benchmark-schema.md`；四端通用、默认 heuristic 无需 CLI |
| **eval agent 编排（官方 agents/ 三件套移植）** | ✅ 2026-09-04：`skill-creator/agents/`（grader/comparator/analyzer 三件套）+ SKILL.md 阶段 5/5.5/6「脚本打底 → 拉起子代理判断 → 脚本聚合收尾」编排 + `--notes` 合并（38 测试通过）；真实任务端到端试跑待做 |
| **docs-refs 基线遗留失败修复** | ✅ 2026-09-04 发现 4d17071 基线 `check_docs_refs.py` 即失败（HANDOFF 裸引用 indexes/upstream.db 无法在 docs/ 解析），已改为模块根限定表述 |
| **skill-creator 全面审计 + 10 项修复** | ✅ 2026-09-04：SKILL.md 结构树补齐（agents/ 三件套等 8 项缺失）、quality-bar 重编号（6→7 项，第 7 项归位）、validate_skills.py 去 PersonalWorkflow 宿主残留、「规则 4」悬空引用自包含化、README evolutions 节点修正、阶段 0 双源表述、5 源出处补全、INSTALL/AGENTS 互提补齐、run_eval.py 加 `--output-dir`（+1 回归，39 用例全绿）、grading 工作区编排层搭建边界写入文档；六件套全绿 |
| **生命周期三缺陷修复（卸载语义定案：不备份）** | ✅ 2026-09-04 用户拍板卸载不备份（需重装即重新安装）：① install_skill.py manifest `source` 记真源（原记安装目标；agent 侧本就正确）② 卸载去虚假备份提示 + 删死旗标 `--keep-backup`（skill/agent 双侧）③ 卸载回收因此变空的父目录（双侧）；`tools/docs/lifecycle.md` 同步；+3 回归钉住（42 用例全绿）；缺陷 1（大写名拒收）确认为预期行为不修 |
| 文档引用一致性检查器 | ✅ 零误报 |
| **入库准入规则 + 审计文件（AGENTS/SKILLS-AUDIT）** | ✅ 根 AGENTS 已加四条规则（+提交前收尾交接）；`docs/AGENTS-AUDIT.md`（32 代理）+ `docs/SKILLS-AUDIT.md`（2 技能）已建 |
| **30 个 UEGameStudio 迁移代理补走 agent-creator** | ✅ 已完成：academic×5 + ue-game-studio×25 逐一对比择优（上游 agency/ccgs/agency-zh）→ 结论自建更优/持平 → 审计转合规 |
| **code-review-skill 导入（awesome-skills，MIT）** | ✅ 2026-09-03 整目录导入 `skills/development/code-review-skill/`（26 语言指南+cross-cutting+assets+scripts+LICENSE），适配本地 schema + description ≤1024；审计登记；对比 0.96 vs 0.71 采纳适配版 |
| **code-simplifier 导入（anthropics/claude-plugins-official）** | ✅ 2026-09-03 导入适配 `agents/code-quality/code-simplifier/`（官方方法论重组本地 7 章节）；审计登记；对比 0.86 vs 0.48 采纳适配版 |
| **规则 4 收紧：分类目录必入（无留顶层例外）** | ✅ AGENTS.md 规则 4 去例外；code-reviewer/code-simplifier 迁入 `agents/code-quality/`、pr-summarizer 迁入 `skills/git/`；`agents/`/`skills/` 根目录无散置能力 |
| **skill-creator 反哺 superpowers writing-skills** | ✅ 2026-09-03 完整采纳：新增 `references/skill-writing-guide.md`（先失败后写/表述匹配失败类型/防借口/措辞微测）+ SKILL.md 阶段 6 纪律块 + description 触发面规范 + 禁 `@` 引用；quality-bar 检查项 7 |
| **description 上限 1024** | ✅ validate_skills/template/quality-bar/skill-template/skill-anatomy 统一；code-review-skill 描述重写为完整触发词 |
| **deepseek-harness 路径实测** | ⚠️ 未做（需真实环境；`DEEPSEEK_HARNESS_ROOT` 兜底） |
| **四端双作用域安装（全局/工作区）** | ✅ client_paths scope 矩阵 + `install_skill.py --scope`（未指定交互询问，工作区装 git 根）；3 端 × 2 作用域沙箱实证 |
| **双创建器 INSTALL.md 运行手册** | ✅ `skill-creator/INSTALL.md` + `agent-creator/INSTALL.md`（作用域选择 + 验证关卡 + 客户端中立生命周期），手册自身自包含 |
| **双创建器自包含完整体** | ✅ 内部引用一律以技能目录为根（`python scripts/...`），不引用外部资源/文档；`check_docs_refs.py` 增模块根探针；脚本 usage 同步 |
| **opencode 路径修正（Windows）** | ✅ 配置根 `~/.config` 而非 `%APPDATA%`（实证 `%APPDATA%\opencode` 不被读取）；回归测试已钉住 |
| **codex 路径修正** | ✅ USER 域 `~/.agents/skills`（原矩阵指向 `~/.codex/skills` SYSTEM 域）；注意 Codex 内置 `.system/skill-creator` 同名并存 |
| **pr-summarizer/code-reviewer 错装迁移** | ✅ 2026-09-04 用安装器重装到 `~/.config\opencode`（skills\pr-summarizer + agent\code-reviewer，带 manifest）；`%APPDATA%\opencode` 旧副本已删除 |
| **opencode 真实安装待重启验证** | ⚠️ 真实安装已执行（2026-09-04 迁移重装），加载效果待 opencode 重启后确认 |
| **UEGameStudio 30 代理运行时验证** | ⚠️ 全为 `static-verified`，需在真实 UE Editor / 目标项目试跑后逐档升 `runtime-verified`，并同步 CATALOG |
| **上游索引更新频率** | 建议定期用 `--source <单源>` 手动同步（技能/代理各自脚本） |
| **新技能/代理持续沉淀** | 按需用本仓库流程创建后回馈到 skills/、agents/（重跑 build_catalog.py） |

## 6. 给新会话的开场提示

接手时：
1. 先 `git log --oneline -5` + `git status` 确认基线
2. 用户需求先定域：**用现成能力** → 读 `skills/CATALOG.md`/`agents/CATALOG.md` 给 install 命令（不调生成器）；**创建/改进能力** → 编排在根 `AGENTS.md`：查本地候选 A → 调对应生成器产出 B（skill-creator 或 agent-creator，各自 `AGENTS.md`/`SKILL.md` 是独立技能引导）→ A vs B 谁优用谁
3. **入库必检准入规则**（根 `AGENTS.md`「入库准入规则」）：入库 `agents/` 必走 agent-creator、入库 `skills/` 必走 skill-creator，且参考外部仓库的必须在 `docs/AGENTS-AUDIT.md` / `docs/SKILLS-AUDIT.md` 标注数据来源；新增/迁移/改进后同步更新审计文件
4. 改动文档时牢记**大小写敏感**（目录小写 + `SKILL.md`/`AGENT.md`/`AGENTS.md` 大写）
5. 改后防回归六件套全跑：
   ```bash
   python -m pytest tests/ -q                        # 42 用例（含路径矩阵/作用域/生命周期/quant eval）
   python tools/scripts/check_docs_refs.py           # md 引用大小写校验（exit 0）
   python skill-creator/scripts/validate_skills.py --strict --dir skills
   python skill-creator/scripts/validate_skills.py --strict --dir skill-creator
   python agent-creator/scripts/validate_agents.py --strict --dir agents
   python tools/scripts/build_catalog.py --check
   ```
6. 涉及副作用（安装/提交/推送）先向用户确认（引导不自动）
7. **写好本交接文件后，向用户输出「新会话交接提示语」**：以下列新会话开场提示的完整文本为准，用**可整段复制的代码块**输出（含本轮基线提交号 + 一句话摘要），供用户直接粘贴到下一个会话使用

## 7. 参考

- 开发计划：`docs/DEVELOPMENT-PLAN.md`（v1.0 目标 + 各阶段标记）
- 生命周期：`tools/docs/lifecycle.md`
- 审计文件：`docs/AGENTS-AUDIT.md`（代理入库合规 + 数据来源）、`docs/SKILLS-AUDIT.md`（技能入库合规 + 数据来源）
- 索引/对比细节：`skill-creator/references/skill-index.md`、`skill-comparison.md`
- 代理索引细节：`agent-creator/references/agent-index.md`
- 按需安装方案：`docs/ON-DEMAND-INSTALL.md`
