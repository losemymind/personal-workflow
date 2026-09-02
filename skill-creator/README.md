# skill-creator

创建和管理自定义 Skill 的目录。融合 5 个成熟 skill-creator 的实现精华（agentic-awesome-skills / Anthropic 官方 / MCPMarket / codex-skill-creator / agent-skill-creator）：证据驱动、渐进式披露、自由度匹配脆弱性、高信号命名、迭代测试循环、触发优化与治理化验证。

## 上游外部仓库（索引来源）

「先查后建」检索的上游技能目录已内置为多源索引（`indexes/upstream.db`，随仓库提交）：

| 源 | 仓库 | 技能数 | 索引方式 | 检索 `--source` |
|---|---|---|---|---|
| **aas** | [sickn33/agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills) | ~2100 | 官方 `skills_index.json` + 目录扫描 | `aas` |
| **addy** | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 25 | 扫描 `skills/*/SKILL.md`（无官方索引） | `addy` |

- 检索全库：`python skill-creator/scripts/search_index.py "<关键词>"`（默认查所有源）
- 按源检索：加 `--source addy`（或 `aas`）
- 重建/增量：`python skill-creator/scripts/build_index.py [--source all|aas|addy] [--incremental]`
- 双源均在 MIT 许可下使用，入库技能需保留来源归属
- 索引细节见 `references/skill-index.md`；新建技能时先在两库中「先查后建」

## 约定

- 每个 Skill 一个子目录，命名 `kebab-case`，例如 `code-review/`
- 每个 Skill 以 `SKILL.md` 为核心，含 frontmatter（含 `version: x.y.z`）与说明

## 结构

```
skill-creator/
  README.md                 # 说明
  SKILL.md                  # 核心：创建/改进/验证/安装技能的方法论（10 阶段工作流）
  AGENTS.md                 # 技能领域入口（总编排 AGENTS.md 分流至此）
  scripts/
    build_index.py          # 构建上游技能索引（tarball→SQLite，支持 --incremental）
    search_index.py         # 检索上游索引（FTS5 全文/分类/风险过滤）
    compare_skills.py       # 自建 vs 上游对比评分（质量6维+结构4维）
    create_skill.py         # 交互式脚手架生成器（含 version 字段）
    run_trigger_tests.py    # 触发测试运行器（启发式准确率/精确率/召回率）
    validate_skills.py      # 自动验证器（frontmatter/章节/安全/链接）
    _project_paths.py       # 仓库根定位辅助
  indexes/
    upstream.db             # SQLite 索引（官方 skills_index.json + 结构扫描，随仓库提交）
  references/
    skill-template.md       # 技能模板：字段与分类完整参考
    skill-anatomy.md        # 技能解剖：结构与渐进式披露
    quality-bar.md          # 质量标准与验证标准（6 项质量检查）
    skill-index.md          # 上游索引：构建/检索/增量更新说明
    skill-comparison.md     # 对比评分维度与择优流程
  templates/
    SKILL.template.md       # 新技能骨架模板（含 version 字段）
    evals.json.template     # 触发测试用例模板
  examples/                 # 上游学习样本（MIT 许可，验证豁免）
    brainstorming/          # 单文件·结构教科书
    copywriting/            # 单文件·流程门控
    git-pushing/            # 单文件+scripts·高风险模板
    systematic-debugging/   # 单文件+references·阶段强制序
    react-best-practices/   # 多文件·渐进式披露范本
    loki-mode/              # 综合·复杂工作流范本
  evolutions/               # 对比择优学习记录（反馈闭环）
  <skill-name>/             # 创建的单个技能实例（安装到客户端时使用 install_skill.py）
    SKILL.md
```

## 使用

1. 参考本目录 `SKILL.md` 的技能创建方法论（10 阶段工作流：阶段 0 检索→9 安装回馈）
2. 使用 `scripts/create_skill.py` 脚手架或 `templates/SKILL.template.md` 作为骨架创建你的 Skill
3. 运行自动验证：`python skill-creator/scripts/validate_skills.py --strict --dir <技能目录>`（失败必须修复）
4. 安装到客户端：`python tools/scripts/install_skill.py [--client claude|opencode|codex|deepseek] <技能目录>`（重启客户端生效）
5. 经验证的技能提交到仓库 `skills/<skill-name>/`（含 `evolutions/` 对比记录）