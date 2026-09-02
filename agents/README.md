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
└── <agent-name>/          # kebab-case，与 frontmatter 的 name 一致
    ├── AGENT.md           # 代理定义（body = prompt）
    └── references/        # 可选：支撑文档、子代理定义
```

## 与 agent-creator 的关系

- 创建/改进代理 → 使用 `agent-creator/`（预留）
- 从本目录安装代理到 LLM 客户端 → 使用 `tools/scripts/install_agent.py`

## 回馈流程

1. 代理验证通过并稳定使用一段时间
2. 完善 frontmatter 元数据
3. 提交到仓库

## 注意

各客户端代理格式有差异（如 opencode 用单文件 .md，claude 也可用单个文件）；入库统一采用**单文件 AGENT.md + 可选子目录**，由安装器按客户端格式落地。