# agents/ — 已验证代理库

本目录存放**经验证、可复用**的代理（Agents），是 PersonalWorkflow 代理分发与回馈的目标位置。

## 准入规则

一个代理进入本目录，必须满足：

1. 有明确的 frontmatter（name/description/mode 等）与可辨识的用途
2. 经过真实任务试跑验证
3. 符合各客户端代理定义规范（claude 的 `.claude/agents/`、opencode 的 `agent/*.md` 等）

## 目录结构约定

```
agents/
├── README.md
├── CATALOG.md             # 自动生成的能力目录（勿手改；见 tools/scripts/build_catalog.py）
└── <agent-name>/          # kebab-case，与 frontmatter 的 name 一致
    ├── AGENT.md           # 代理定义（body = prompt）
    └── references/        # 可选：支撑文档、子代理定义
```

## 与 agent-creator 的关系

- 创建/改进代理 → 使用 `agent-creator/`（方法论见 `agent-creator/SKILL.md`，脚手架 `create_agent.py`，验证器 `validate_agents.py`）
- 从本目录安装代理到 LLM 客户端 → 使用 `tools/scripts/install_agent.py`

## 能力目录（CATALOG.md）

`CATALOG.md` 由 `tools/scripts/build_catalog.py` 从各 `AGENT.md` frontmatter 自动生成（勿手改）。它是 LLM 按需安装的检索入口：读目录匹配需求 → 命中即给条目 `install` 命令，用户确认后执行。新增/删除代理后重跑生成器（CI 用 `--check` 防漂移）。

## 回馈流程

1. 代理验证通过并稳定使用一段时间
2. 完善 frontmatter 元数据
3. 运行 `python tools/scripts/build_catalog.py` 刷新能力目录
4. 提交到仓库

## 注意

各客户端代理格式有差异（如 opencode 用单文件 .md，claude 也可用单个文件）；入库统一采用**单文件 AGENT.md + 可选子目录**，由安装器按客户端格式落地。