# skill-creator

创建和管理自定义 Skill 的目录。融合 5 个成熟 skill-creator 的实现精华（agentic-awesome-skills / Anthropic 官方 / MCPMarket / codex-skill-creator / agent-skill-creator）：证据驱动、渐进式披露、自由度匹配脆弱性、高信号命名、迭代测试循环、触发优化与治理化验证。

## 约定

- 每个 Skill 一个子目录，命名 `kebab-case`，例如 `code-review/`
- 每个 Skill 以 `SKILL.md` 为核心，含 frontmatter 与说明

## 结构

```
skill-creator/
  README.md              # 说明
  SKILL.md               # 核心：创建/改进/验证/安装技能的方法论
  templates/
    SKILL.template.md    # 新技能骨架模板
  <skill-name>/          # 创建的单个技能实例（安装到客户端时只复制该子目录）
    SKILL.md
```

## 使用

1. 参考本目录 `SKILL.md` 的技能创建方法论（9 阶段核心工作流）
2. 使用 `templates/SKILL.template.md` 作为骨架创建你的 Skill
3. 运行自动验证：`python tools/scripts/validate_skills.py`（或 `--strict` 严格模式）
4. 把`<skill-name>/` 目录复制到目标客户端的 skills 目录（Claude: `~/.claude/skills/`、OpenCode: `~/.config/opencode/skills/` 或 `.opencode/skills/`、Codex: `~/.codex/skills/`），重启客户端生效
5. 经验证的技能提交到仓库 `skills/<skill-name>/`