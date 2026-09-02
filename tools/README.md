# tools/ — 基础工具集

本目录存放 PersonalWorkflow 的**跨组件基础工具**（与 skill-creator、agent-creator 平行、被它们共享的设施）。

## 目录结构

```
tools/
├── README.md
├── docs/                  # 工具文档
└── scripts/               # 可执行工具脚本
    ├── client_paths.py    # 四端客户端路径矩阵（claude/opencode/codex/deepseek-harness）
    ├── install_skill.py   # 安装技能到客户端
    ├── install_agent.py   # 安装代理到客户端
    ├── update_skill.py    # 升级技能（保留旧版本备份）
    ├── update_agent.py    # 升级代理（保留旧版本备份）
    ├── uninstall_skill.py # 卸载技能
    ├── uninstall_agent.py # 卸载代理
    ├── rollback_skill.py  # 回滚技能到上一版本
    ├── rollback_agent.py  # 回滚代理到上一版本
    ├── build_catalog.py   # 生成 skills/CATALOG.md + agents/CATALOG.md（--check 防漂移）
    └── check_docs_refs.py # 文档引用与 git 索引大小写敏感校验
```

## 设计约定

- **manifest-driven**：安装清单（`.personal-workflow-manifest.json`）是生命周期操作（install/update/uninstall/rollback）的唯一事实来源。
- **单一路径矩阵**：所有客户端路径差异集中在 `client_paths.py`，其他脚本只调用接口，不硬编码路径。
- **跨平台**：脚本兼容 Windows PowerShell / 类 Unix，路径统一由 `client_paths.py` 解析。
- **不重复造轮子**：skill 的创建/验证归 `skill-creator/`，代理创建归 `agent-creator/`，`tools/` 只负责"分发与生命周期"。

## 使用入口

- 安装技能：`python tools/scripts/install_skill.py --client <claude|opencode|codex|deepseek> <技能目录>`
- 安装代理：`python tools/scripts/install_agent.py --client <...> <代理目录>`
- 生命周期操作参见 `tools/docs/lifecycle.md`

## 演进

首个版本聚焦"技能分发与生命周期"；能力目录生成器（build_catalog.py）已补齐按需安装的发现层；后续可扩展：索引同步、跨客户端安装批量脚本、仓库级状态报告。