# 上游技能索引（Skill Index）

基于 agentic-awesome-skills 官方 `skills_index.json` 构建的本地 SQLite 检索索引，让 skill-creator 在创建前能快速检查"上游是否已有可用技能"。

## 数据来源与规模

| 项 | 值 |
|---|---|
| 上游仓库 | `https://github.com/sickn33/agentic-awesome-skills` |
| 数据源 | 官方 `skills_index.json`（权威元数据）+ 目录扫描补充结构信息 |
| 索引文件 | `skill-creator/indexes/upstream.db` |
| 技能总数 | ~2100（随上游更新变化） |
| 许可 | 上游 MIT License |

## 索引说明

每条记录包含：`name` / `path` / `description` / `category` / `risk` / `source` / `date_added` / `tags` / `tools` / 客户端支持（`client_targets`）/

结构信息：`has_script` / `has_references` / `has_examples` / `has_templates` / `body_lines` / `file_count` / `subdirs`。

内含 FTS5 全文检索表 `skills_fts`，支持关键词匹配 name/description/category/tags。

## 使用

```bash
# 检索（关键词全文搜索）
python skill-creator/scripts/search_index.py "debugging"
python skill-creator/scripts/search_index.py "git push" --category devops --risk safe
python skill-creator/scripts/search_index.py "react" --tool opencode
python skill-creator/scripts/search_index.py "api" --only-references --limit 20

# 查看索引状态 / 分类分布
python skill-creator/scripts/search_index.py --stats
python skill-creator/scripts/search_index.py --list-categories

# JSON 输出（便于程序化处理）
python skill-creator/scripts/search_index.py "pdf" --json
```

## 构建与更新

```bash
# 完整重建（默认：下载上游 tarball → 构建 → 自动清理）
python skill-creator/scripts/build_index.py

# 保留 tarball
python skill-creator/scripts/build_index.py --keep

# 从本地已解压的上游仓库构建（避免重复下载）
python skill-creator/scripts/build_index.py --from-extracted <上游解压目录>
```

**同步策略：** 手动触发（推荐）。索引文件已提交入仓库，用户克隆即得索引；仅当需要更新上游技能列表时重跑构建。

## 后续演进

- 上游新增技能 → 重跑 `build_index.py` 增量更新
- 客户端定制索引（如仅索引某分类）→ 可在 `search_index.py` 增加 `--category` 组合筛选
- 语义检索 → 后续可在索引中加入 embedding 向量（需要时再设计）