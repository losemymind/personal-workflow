# skill-creator

创建和管理自定义 Skill 的目录。

## 约定

- 每个 Skill 一个子目录，命名 `kebab-case`，例如 `code-review/`
- 每个 Skill 以 `SKILL.md` 为核心，含 frontmatter 与说明

## 结构

```
skill-creator/
  README.md
  templates/       # 通用模板（SKILL.md 骨架等）
  <skill-name>/    # 单个 Skill 的制作目录
    SKILL.md
```

## 使用

1. 参考 `templates/` 中的 SKILL.md 骨架创建你的 Skill
2. 将目录放入 `~/.config/opencode/skills/`（或工作区 `.opencode/skills/`）