# agent-creator

创建和管理自定义 Agent 的目录。

## 约定

- 每个 Agent 一个子目录，命名 `kebab-case`，例如 `test-writer/`
- Agent 定义放在 opencode 的 `agent` 配置中，或映射到本地 `agent` 子目录

## 结构

```
agent-creator/
  README.md
  templates/       # 通用模板（agent 定义骨架等）
  <agent-name>/    # 单个 Agent 的制作目录
```

## 使用

1. 参考 `templates/` 中的骨架创建你的 Agent
2. 在 `opencode.json` 的 `agent` 数组中注册，或放入 `.opencode/agent/`