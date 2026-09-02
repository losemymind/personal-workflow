# PersonalWorkflow 交接文档（HANDOFF）

> 用途：新会话快速恢复上下文。读完本文件即可接手开发。
> 生成日期：2026-09-02 ｜ 最近提交见 `git log --oneline -5`

## 1. 这是什么

个人工作流工具库，跑通 **检索上游 → 创建 → 对比择优 → 验证 → 安装 → 回馈** 的完整闭环。支持四个 LLM 客户端：**claude / opencode / codex / deepseek-harness**。仓库远程：`https://github.com/losemymind/personal-workflow.git`（分支 `main`）。

## 2. 顶层架构（总编排 → 领域入口）

```
AGENTS.md                 # 总编排/分发入口：先定领域再分流
├── skill-creator/AGENTS.md   # 技能领域入口（含 SKILL.md 方法论 + AGENTS.md 指引）
├── agent-creator/AGENTS.md   # 代理领域入口（含 SKILL.md 方法论 + AGENTS.md 指引）
├── tools/docs/lifecycle.md   # 安装/生命周期通用入口
├── skills/               # 已验证技能库（回馈目标；现有 pr-summarizer）
├── agents/               # 已验证代理库（回馈目标；现有 code-reviewer）
├── tools/scripts/        # 四端安装器 + 生命周期（manifest-driven）
├── tests/                # pytest（11 用例，覆盖验证器/路径矩阵）
├── .github/workflows/validate.yml  # CI：双验证器 --strict + pytest + 文档引用检查
└── docs/                 # DEVELOPMENT-PLAN.md（开发计划）、HANDOFF.md（本文件）
```

**核心原则**：先查后建（检索上游索引）→ 引导不自动（AGENTS.md 只指引）→ 验证优先 → 回馈闭环（`evolutions/` 记录"上游更优"的学习点）。

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
- `SKILL.md`：身份先于指令 / 最小权限 / 协作协议 / 升级路径
- `references/`：agent-template（四端兼容矩阵）/ agent-anatomy / agent-quality-bar
- 脚本：`create_agent.py`（脚手架）、`validate_agents.py`（边界/权限/协作/链接校验）

### tools（分发与生命周期）
- `client_paths.py`：四端路径矩阵（唯一事实源）
- `install_skill.py` / `install_agent.py`：四端安装（manifest 标记 `.personal-workflow-manifest.json`）
- `update/uninstall/rollback_skill.py` + `_agent.py`：生命周期（备份至 `~/.personal-workflow/backups/`）
- `check_docs_refs.py`：md 引用与 git 索引的大小写敏感校验（零误报）
- deepseek 路径为 best-effort（`DEEPSEEK_HARNESS_ROOT` 覆盖），未实测

### 文档质量
- 根 `AGENTS.md` / `skill-creator/AGENTS.md` / `agent-creator/AGENTS.md` 分层入口
- 各 README 结构树与实际文件已对齐（曾全量核对过一轮）
- 关键点：**文件名大小写敏感**（目录小写 + `SKILL.md`/`AGENT.md`/`AGENTS.md` 大写）——Windows 开发时易踩坑，克隆到 Linux 会断链，务必用 `git ls-files` 校验引用

## 4. 常用命令速查

```bash
# 检索上游（先查后建）—— 默认全库，--source aas|addy 过滤
python skill-creator/scripts/search_index.py "<关键词>" [--source addy] [--category X]

# 索引：重建/增量
python skill-creator/scripts/build_index.py [--source all|aas|addy] [--incremental]
python skill-creator/scripts/build_index.py --source addy --from-extracted <本地仓库>

# 创建/验证
python skill-creator/scripts/create_skill.py --name x --category git --risk safe --no-interactive
python skill-creator/scripts/validate_skills.py --strict --dir skills/x
python agent-creator/scripts/create_agent.py --name x --mode subagent --no-interactive
python agent-creator/scripts/validate_agents.py --strict --dir agents/x

# 对比择优（有上游候选时）
python skill-creator/scripts/compare_skills.py <自建目录> <上游目录>

# 安装 + 生命周期
python tools/scripts/install_skill.py [--client opencode|claude|codex|deepseek] <技能目录>
python tools/scripts/update_skill.py <名> --source <新版>   # 代理用 _agent 版同构
python tools/scripts/uninstall_skill.py <名>
python tools/scripts/rollback_skill.py <名>

# 测试/CI 等价
python -m pytest tests/ -q          # 11 用例
python tools/scripts/check_docs_refs.py   # 文档引用完整性（exit 0）
```

## 5. 当前状态与未完成事项

| 项 | 状态 |
|---|---|
| 双源索引（aas+addy，2132 技能） | ✅ 已重建入库 |
| 首个入库技能/代理（pr-summarizer / code-reviewer） | ✅ 已验证并安装到 opencode |
| agent 生命周期（update/uninstall/rollback） | ✅ 已补齐（目录+单文件形态） |
| CI（strict 验证 + pytest + 文档检查） | ✅ 已配置 |
| 文档引用一致性检查器 | ✅ 零误报 |
| **deepseek-harness 路径实测** | ⚠️ 未做（需真实环境；`DEEPSEEK_HARNESS_ROOT` 兜底） |
| **opencode 真实安装待重启验证** | ⚠️ pr-summarizer/code-reviewer 已 install，需重启客户端确认加载 |
| **上游索引更新频率** | 建议定期 `--incremental` 手动同步 |
| **新技能/代理持续沉淀** | 按需用本仓库流程创建后回馈到 skills/、agents/ |

## 6. 给新会话的开场提示

接手时：
1. 先 `git log --oneline -5` + `git status` 确认基线
2. 用户需求落入哪一域（技能/代理/工具）→ 进对应 `AGENTS.md`（或直接读本文件 + 对应 `SKILL.md`）
3. 改动文档时牢记**大小写敏感**，改完跑 `python tools/scripts/check_docs_refs.py` + `validate_skills.py --strict --dir skill-creator` + `pytest`
4. 改 Python 脚本后跑 `pytest`（11 用例）防回归
5. 涉及副作用（安装/提交/推送）先向用户确认（引导不自动）

## 7. 参考

- 开发计划：`docs/DEVELOPMENT-PLAN.md`（v1.0 目标 + 各阶段标记）
- 生命周期：`tools/docs/lifecycle.md`
- 索引/对比细节：`skill-creator/references/skill-index.md`、`skill-comparison.md`
