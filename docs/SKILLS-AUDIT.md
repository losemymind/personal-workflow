# PersonalWorkflow 技能审计（SKILLS-AUDIT）

> 用途：审计 `skills/` 库中每个技能的**数据来源** 与 **入库流程合规性**。事实源 = 各 `SKILL.md` frontmatter + git 历史 + `skill-creator/evolutions/` 对比记录。
> 依据：根 `AGENTS.md`「入库准入规则」第 2、3、4 条（规则 2：技能入库**无论参考本地文件还是远程仓库，必须经过 skill-creator**；规则 3：**参考外部仓库的技能必须在审计文件中标注数据来源**；规则 4：**技能按功能放入分类目录 `skills/<分类>/<name>/`，分类不存在则创建**）。
> 本次审计日期：2026-09-03

## 1. 审计结论摘要

| 指标 | 数值 |
|---|---|
| 技能总数 | 2（pr-summarizer / code-review-skill） |
| 经 skill-creator 生成流程 | 2 ✅ |
| 远程仓库来源（参考上游 / 直接导入） | 2（sickn33/agentic-awesome-skills 的 comprehensive-review-pr-enhance；awesome-skills/code-review-skill） |
| 本地文件来源 | 0 |
| `source: self`（自建） | 1 |
| `source: community`（上游导入） | 1 |

**审计结论**：
- ✅ **pr-summarizer 合规（规则 2）**：本仓库自建，完整经过 skill-creator 流程（创建 → 检索上游 → 对比择优 → `evolutions/` 记录 → 验证）。
- ✅ **code-review-skill 合规（规则 2、3、4）**：2026-09-03 按用户指定从上游 `awesome-skills/code-review-skill`（MIT）直接导入并适配——整目录（reference/assets/scripts + LICENSE）入库 `skills/development/code-review-skill/`；frontmatter 补齐本地 schema（category/risk/source/version/date_added/tags/tools），补 `Examples`/`Limitations` 章节，`validate_skills.py --strict` 通过。
- ✅ **规则 3 达标**：本文件已标注全部外部数据来源（上游 comprehensive-review-pr-enhance 与 code-review-skill）。

## 2. 数据来源

| 来源类型 | 来源详情 | 涉及技能 |
|---|---|---|
| 自建（skill-creator 流程） | 本仓库创建；frontmatter `source: self` | pr-summarizer |
| 远程仓库（上游参考） | `sickn33/agentic-awesome-skills` 的 `comprehensive-review-pr-enhance`（83 行，2 文件，risk: critical） | pr-summarizer（吸收其变更分类表/类别驱动清单/大 diff 分拆/风险标注精华） |
| 远程仓库（整目录导入，MIT） | `awesome-skills/code-review-skill`（https://github.com/awesome-skills/code-review-skill，1.9k star，SKILL.md ~232 行 + reference/ 26 语言指南 + cross-cutting 5 + assets/ + scripts/，约 848KB/50 文件） | code-review-skill（整目录导入并适配本地 schema，保留 LICENSE 归属） |

> 上游对比/导入记录：`skill-creator/evolutions/2026-09-02-compare-pr-summarizer.md`（自建版采纳上游精华 + 差异化定位）；`skill-creator/evolutions/2026-09-03-import-code-review-skill.md`（本地无候选 A → 直接导入上游 B）。

## 3. 技能清单

| 技能名 | 位置 | category | risk | source | 数据来源 | 经 skill-creator | 结论 |
|---|---|---|---|---|---|---|---|
| pr-summarizer | `skills/git/pr-summarizer/SKILL.md` | git | safe | self | 自建 + 上游 sickn33/agentic-awesome-skills（comprehensive-review-pr-enhance） | ✅ | ✅ 合规（2026-09-03 按规则 4 迁入 `skills/git/`） |
| code-review-skill | `skills/development/code-review-skill/SKILL.md` | development | safe | community | 上游 `awesome-skills/code-review-skill`（MIT）整目录导入 | ✅ | ✅ 合规（2026-09-03 导入，保留 LICENSE 归属） |

## 4. 维护要求

- 新增/迁移/改进技能入库后，**必须更新本文件**：登记数据来源（规则 3）与是否经 skill-creator（规则 2）。
- 参考外部仓库（远程或本地）的技能，数据来源必须可追溯到具体上游仓库与条目（连同 `evolutions/` 对比记录）。
- 本文件与 `docs/AGENTS-AUDIT.md` 同构，均为数据来源的唯一记录入口。

## 5. 整改建议（未完成项）

- 后续每个入库技能都应在本文件中登记；若存在上游同类技能但未做对比择优，需补走 `skill-creator` 对比环节并记录到 `skill-creator/evolutions/`。