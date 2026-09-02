# 技能解剖（Skill Anatomy）

基于 agentic-awesome-skills 的 `skill-anatomy.md` 适配，解释技能文件的每个组成部分。

## 基本文件夹结构

```
skills/
└── my-skill-name/
    ├── SKILL.md              ← 必需：主要技能定义
    ├── examples/             ← 可选：示例文件
    ├── scripts/              ← 可选：辅助脚本
    ├── templates/            ← 可选：代码/输出模板
    ├── references/           ← 可选：参考文档
    └── README.md             ← 可选：附加文档
```

**关键规则：**只有 `SKILL.md` 是必需的。其他一切都是可选的！

## SKILL.md 结构

每个 `SKILL.md` 两个主要部分：

1. **前置元数据（frontmatter）** — `---` 包裹的 YAML
2. **内容（指令）** — Markdown 正文

## 前置元数据

```yaml
---
name: my-skill-name          # 必需：与文件夹名完全一致
description: "..."           # 必需：一句话摘要 + 触发场景
category: productivity       # 必需：分类
risk: safe                   # 必需：安全分类
source: self                 # 必需：来源归属
date_added: "YYYY-MM-DD"     # 必需
author: "name-or-handle"     # 可选
tags: ["python", "testing"]  # 可选：≤5 个
tools: [claude, opencode]    # 可选：支持的客户端
---
```

字段细节与分类/风险值见 `skill-template.md`。

## 内容推荐结构

1. **标题（H1）** — 清晰描述性，通常与技能名匹配或扩展
2. **概述** — 2-4 句：做什么、为什么存在
3. **何时使用此技能** — 触发场景（帮助 LLM 决定何时激活）
4. **工作原理** — 步骤化核心指令
5. **示例** — 至少 1 个可立即复制的代码块
6. **最佳实践** — ✅ 这样做 / ❌ 避免
7. **相关技能** — `@other-skill` 引用
8. **安全与安全说明** — 涉及命令/网络/攻击性内容时必加

## 渐进式披露（Progressive Disclosure）

技能分为三层加载：

1. **元数据**（name + description）— 始终在上下文中（约 100 词），决定是否触发
2. **SKILL.md 正文** — 触发时加载（理想 <500 行）
3. **捆绑资源**（scripts/references/assets）— 按需加载，无限量

**关键模式：**
- 正文逼近 500 行时，增加层级结构并把细节指向 `references/`
- 大参考文件（>300 行）提供目录
- 多领域按变体组织：正文放工作流+选择，`references/` 每领域一个文件

## 可选组件

**scripts/**：确定性/重复性任务的辅助脚本（被运行，不占上下文）
```
scripts/
├── setup.sh       ← 设置自动化
├── validate.py    ← 验证工具
└── generate.js    ← 代码生成器
```
在 SKILL.md 中引用：`bash scripts/setup.sh`

**examples/**：真实示例，展示良好输出长什么样

**templates/**：可复用代码/输出模板

**references/**：外部文档或 API 参考，按需注入

## 技能大小指南

- **最小可行**：name+description + 100-200 字 + 概述+指令
- **标准**：name+description + 300-800 字 + 概述+触发+指令+示例
- **综合**：全部推荐章节 + 脚本/示例/模板

**经验法则**：从小处开始，根据反馈扩展。

## 格式最佳实践

- 代码块始终指定语言
- 列表格式一致（含嵌套）
- **粗体**重要术语、*斜体*强调、`代码`命令
- 标题遵循层级（H1 → H2 → H3）

## 有效性测试

- **清晰度**：不了解主题的人能遵循吗？
- **完整性**：覆盖快乐路径 + 边缘情况 + 错误场景？
- **有用性**：解决实际问题吗？省时间或提质量吗？

## 常见错误

- ❌ 太模糊（「使代码更好。」）
- ❌ 太复杂（5000 字密集术语）→ 拆成多技能或渐进披露
- ❌ 无示例 → 至少加 2-3 个真实示例
- ❌ 过时信息 → 用当前最佳实践更新