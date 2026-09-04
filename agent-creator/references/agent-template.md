# 代理模板（Agent Template）

基于四端客户端（claude/opencode/codex/deepseek-harness）的代理定义规范适配。可复制的骨架见 `templates/AGENT.template.md`（复制后替换占位符）。

## 示例 frontmatter（openCode 兼容子集）

```yaml
---
name: my-reviewer
description: "PR 审查代理：负责代码风格与架构审查，当用户要求审查 PR 或合并请求时被调用。"
mode: subagent
model: anthropic/claude-sonnet-4-6
tools: [read, grep, glob]
permission:
  edit: deny
version: "0.1.0"
tools_clients: [claude, opencode, codex, deepseek]
---
```

## 字段说明

**必需字段：**
- `name`：kebab-case，与目录名一致，单行，≤50 字符
- `description`：≤200 字符（验证器上限 300），前端加载「做什么 + 何时被调用」

**可选字段（按客户端支持程度声明）：**
- `mode`：`primary` / `subagent` / `all`（opencode 语义）
- `model`：`provider/model-id` 格式（opencode/claude 支持）
- `tools`：允许的工具列表（最小权限原则，越少越好）
- `permission`：权限规则（如 `edit: deny`、`bash: ask`）
- `version`：语义化 `x.y.z`（生命周期记账用）
- `tools_clients`：声明适用客户端（claude/opencode/codex/deepseek）
- `temperature` / `top_p`：采样参数（opencode 支持）
- `tags`：≤5 个，小写-连字符

**代理专属字段（opencode）**：`hidden`（隐藏于 TUI 列表）、`color`、`steps`、`options`、`disable`（禁用内置代理）。

## 四端兼容矩阵

| 字段 | claude | opencode | codex | deepseek |
|---|---|---|---|---|
| `name` | ✅ | ✅ | ⚠️ 文件名即名称 | ⚠️ 随版本 |
| `description` | ✅（触发依据） | ✅（触发依据） | ✅ | ⚠️ 随版本 |
| `mode` | ⚠️ subagent 才有此语义 | ✅ primary/subagent/all | ⚠️ 随版本 | ⚠️ 随版本 |
| `model` | ✅ | ✅ | ✅ | ⚠️ |
| `tools` | ✅（Claude 工具名） | ✅（opencode 工具名） | ⚠️ | ⚠️ |
| `permission` | ✅（Claude 格式） | ✅（opencode 格式） | ⚠️ | ⚠️ |
| `version`/`tags` | 忽略（自定义） | ✅ | ⚠️ | ⚠️ |

**兼容策略**：使用通用子集（name/description/version/tags/tools_clients）+ 客户端专属字段；安装时按目标客户端规范转换，不能转换的字段忽略（以客户端文档为准）。

## 章节要求（AGENT.md 主体）

**必需章节**：角色定位、职责范围（必须做/拒绝做）、工具与权限
**质量门槛要求**：协作协议（含升级路径）、完成标准、限制与边界
**可选章节**：工作方式、相关技能/参考文档

## 质量检查清单

- [ ] name 与目录一致，description 含触发场景
- [ ] 职责范围同时含「必须做 / 拒绝做」
- [ ] 工具最小权限，破坏性动作显式声明或拒绝
- [ ] 有升级路径（何时交还人类）
- [ ] 完成标准可验证
- [ ] 通过 `validate_agents.py --strict`