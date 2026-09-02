# PersonalWorkflow 交接文档（HANDOFF）

> 用途：新会话快速恢复上下文。读完本文件即可接手开发。
> 生成日期：2026-09-02 ｜ 最近提交见 `git log --oneline -5`
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
├── skills/               # 已验证技能库（回馈目标；现有 pr-summarizer）
├── agents/               # 已验证代理库（回馈目标；现有 code-reviewer）
├── tools/scripts/        # 四端安装器 + 生命周期 + 能力目录生成器（manifest-driven）
├── tests/                # pytest（22 用例，覆盖验证器/路径矩阵/生成器）
├── .github/workflows/validate.yml  # CI：双验证器 --strict + pytest + 文档引用 + 目录同步
└── docs/                 # DEVELOPMENT-PLAN.md（开发计划）、HANDOFF.md（本文件）、ON-DEMAND-INSTALL.md（按需安装方案）
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
- `references/`：template/anatomy/quality-bar/index/comparison
- `examples/`：6 个上游学习样本（MIT，验证豁免）；`evolutions/`：对比学习记录（已有 pr-summarizer 真实记录）
- `opencode.json` 已注册 `skills.paths = ["skill-creator", "agent-creator"]`

### agent-creator（代理生产器）
- `SKILL.md`：身份先于指令 / 最小权限 / 协作协议 / 升级路径 / 独立安装（不含上层编排）
- 上游**三源 SQLite 索引** `agent-creator/indexes/upstream.db`（568 代理）：
  - `agency` = msitarzewski/agency-agents（258，division 目录扫描）
  - `ccgs` = Donchitos/Claude-Code-Game-Studios（49，.claude/agents 扫描）
  - `agency-zh` = jnMetaCode/agency-agents-zh（261，中文版，含公司/法务/HR/供应链等 division）
- 脚本：`search_agent_index.py`（检索/--source/stats/--list-categories，含 CJK LIKE 兜底）、`build_agent_index.py`（多源构建/--from-extracted）、`create_agent.py`（脚手架）、`validate_agents.py`（边界/权限/协作/链接校验）
- `references/`：agent-template（四端兼容矩阵）/ agent-anatomy / agent-quality-bar / agent-index（索引说明）
- `evolutions/`：对比学习记录（与 skill-creator 同构，模板见 README）

### tools（分发与生命周期）
- `client_paths.py`：四端路径矩阵（唯一事实源）
- `install_skill.py` / `install_agent.py`：四端安装（manifest 标记 `.personal-workflow-manifest.json`）
- `build_catalog.py`：能力目录生成器（`skills/CATALOG.md` + `agents/CATALOG.md`，`--check` 防漂移）
- `update/uninstall/rollback_skill.py` + `_agent.py`：生命周期（备份至 `~/.personal-workflow/backups/`）
- `check_docs_refs.py`：md 引用与 git 索引的大小写敏感校验（零误报）
- deepseek 路径为 best-effort（`DEEPSEEK_HARNESS_ROOT` 覆盖），未实测

### 按需安装 + 创建决策（能力目录）
- `skills/CATALOG.md` / `agents/CATALOG.md`：本地已验证能力清单（LLM 检索 → 命中给 install 命令 → 人类确认）
- **职责分层**：skill-creator/agent-creator 是可独立安装的生产器（闭环 = 创建 → 检索上游对比 → 上游更优反哺自身 `evolutions/`，目录内不含上层编排）；**编排只在根 AGENTS**：查本地候选 A → 无论有无都调生成器产出 B → A vs B 谁优用谁
- agent 字段 schema 与 skill 不同：agent 无 category/source/date_added，用 mode/tags 分类

### 文档质量
- 根 `AGENTS.md` 为总编排；`skill-creator/AGENTS.md` / `agent-creator/AGENTS.md` 为各自独立技能引导（随技能分发）
- 各 README 结构树与实际文件已对齐（曾全量核对过一轮）
- 关键点：**文件名大小写敏感**（目录小写 + `SKILL.md`/`AGENT.md`/`AGENTS.md` 大写）——Windows 开发时易踩坑，克隆到 Linux 会断链，务必用 `git ls-files` 校验引用

## 4. 常用命令速查

```bash
# 按需安装已有能力（先查后建：本地优先）—— 让 LLM 读目录匹配，命中给 install 命令
#   skills/CATALOG.md  ·  agents/CATALOG.md
python tools/scripts/install_skill.py [--client opencode|claude|codex|deepseek] skills/<name>
python tools/scripts/install_agent.py [--client opencode|claude|codex|deepseek] agents/<name>

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

# 生命周期
python tools/scripts/update_skill.py <名> --source <新版>   # 代理用 _agent 版同构
python tools/scripts/uninstall_skill.py <名>
python tools/scripts/rollback_skill.py <名>

# 测试/CI 等价
python -m pytest tests/ -q          # 22 用例
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
| agent 生命周期（update/uninstall/rollback） | ✅ 已补齐（目录+单文件形态） |
| CI（strict 验证 + pytest + 文档检查 + 目录同步） | ✅ 已配置 |
| 按需安装 + 创建决策（分层） | ✅ CATALOG.md 生成器 + 生产器独立化（闭环 3 步，不含编排）+ 编排收敛到根 AGENTS（A vs B 谁优用谁） |
| agent-creator evolutions | ✅ 已补（同构 skill-creator；暂无真实记录） |
| 文档引用一致性检查器 | ✅ 零误报 |
| **deepseek-harness 路径实测** | ⚠️ 未做（需真实环境；`DEEPSEEK_HARNESS_ROOT` 兜底） |
| **opencode 真实安装待重启验证** | ⚠️ pr-summarizer/code-reviewer 已 install，需重启客户端确认加载 |
| **上游索引更新频率** | 建议定期用 `--source <单源>` 手动同步（技能/代理各自脚本） |
| **新技能/代理持续沉淀** | 按需用本仓库流程创建后回馈到 skills/、agents/（重跑 build_catalog.py） |

## 6. 给新会话的开场提示

接手时：
1. 先 `git log --oneline -5` + `git status` 确认基线
2. 用户需求先定域：**用现成能力** → 读 `skills/CATALOG.md`/`agents/CATALOG.md` 给 install 命令（不调生成器）；**创建/改进能力** → 编排在根 `AGENTS.md`：查本地候选 A → 调对应生成器产出 B（skill-creator 或 agent-creator，各自 `AGENTS.md`/`SKILL.md` 是独立技能引导）→ A vs B 谁优用谁
3. 改动文档时牢记**大小写敏感**（目录小写 + `SKILL.md`/`AGENT.md`/`AGENTS.md` 大写）
4. 改后防回归三件套全跑：
   ```bash
   python -m pytest tests/ -q                        # 22 用例
   python tools/scripts/check_docs_refs.py           # md 引用大小写校验（exit 0）
   python skill-creator/scripts/validate_skills.py --strict --dir skills
   python skill-creator/scripts/validate_skills.py --strict --dir skill-creator
   python agent-creator/scripts/validate_agents.py --strict --dir agents
   python tools/scripts/build_catalog.py --check
   ```
5. 涉及副作用（安装/提交/推送）先向用户确认（引导不自动）

## 7. 参考

- 开发计划：`docs/DEVELOPMENT-PLAN.md`（v1.0 目标 + 各阶段标记）
- 生命周期：`tools/docs/lifecycle.md`
- 索引/对比细节：`skill-creator/references/skill-index.md`、`skill-comparison.md`
- 代理索引细节：`agent-creator/references/agent-index.md`
- 按需安装方案：`docs/ON-DEMAND-INSTALL.md`
