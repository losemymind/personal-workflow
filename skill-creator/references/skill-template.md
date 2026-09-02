# 技能模板（Skill Template）

基于 agentic-awesome-skills 的 `skill-template.md` 适配。创建新技能时以此骨架开始，逐项替换字段与章节。

## 模板文件

仓库内置骨架见 `skill-creator/templates/SKILL.template.md`，直接复制使用：

```markdown
---
name: your-skill-name
description: "一句话说明技能做什么以及何时触发（≤200 字符）"
category: <category>
risk: <none|safe|critical|offensive|unknown>
source: self
date_added: "YYYY-MM-DD"
author: your-name-or-handle
tags: [tag-one, tag-two]
tools: [claude, opencode, codex, deepseek]
---

# 技能标题

## 概述
2-4 句话：做什么、为什么存在。

## 何时使用此技能
触发场景列表（这是自动验证要求的关键章节）。

## 工作原理
步骤化执行流程。

## 示例
至少 1 个可复制立即使用的示例。

## 最佳实践
✅ 推荐做法 / ❌ 避免的陷阱。

## 相关技能
@other-skill 引用。

## 常见问题
常见问题与排查。

## 限制和注意事项
已知边界与做不到的事（自动验证要求的关键章节）。

## 安全与安全说明
涉及命令/安装/权限/高风险时才需要。
```

## 字段说明

**必需字段：**
- `name`：小写-连字符，与目录名完全一致，≤100 字符
- `description`：≤200 字符，包含「做什么 + 何时触发」，触发关键词前置
- `category`：见下方分类列表
- `risk`：`none` / `safe` / `critical` / `offensive` / `unknown`（新技能避免 `unknown`）
- `source`：`self`（原创）/ 社区 / 官方 / URL
- `date_added`：`YYYY-MM-DD` 格式

**可选字段：**
- `author`：作者名称或 handle
- `tags`：小写、连字符分隔、≤5 个
- `tools`：支持的客户端列表（claude/opencode/codex/deepseek 等）

**外部来源追加字段：**
- `source_repo`：上游仓库（OWNER/REPO 格式）
- `source_type`：`official` / `community` / `self`

## 技能分类列表

- **开发类**：`development` `frontend` `backend` `mobile` `testing` `devops`
- **架构类**：`architecture` `design` `database` `api`
- **安全类**：`security` `pen-testing` `compliance` `cryptography`
- **AI 类**：`ai` `machine-learning` `prompt-engineering` `data-science`
- **工具类**：`git` `productivity` `documentation` `deployment`
- **业务类**：`product` `planning` `communication` `research`

## 风险级别定义

- `none` — 纯文本/推理，无命令或状态变更
- `safe` — 代码审查、文档编写、只读命令（多数指导类技能用此级）
- `critical` — 修改状态、删除文件、推送生产环境、自动化脚本
- `offensive` — 渗透测试/红队，**必须**含「仅限授权使用」警告
- `unknown` — 遗留/未分类，新技能应避免

## 标签规范

- 小写字母 + 连字符分隔，避免特殊字符，最多 5 个
- 技术标签：`react` `python` `aws`
- 概念标签：`patterns` `security` `testing`
- 领域标签：`frontend` `backend` `api`

## 章节要求

**必需章节**：概述、何时使用此技能、工作原理
**质量门槛要求章节**：示例、限制和注意事项
**可选章节**：最佳实践、相关技能、常见问题、安全与安全说明