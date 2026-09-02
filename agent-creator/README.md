# agent-creator

创建和管理自定义 Agent（代理）的目录。与 skill-creator 平行同构：skill 回答「怎么做」，agent 回答「谁来做」。

## 结构

```
agent-creator/
  README.md                        # 说明
  SKILL.md                         # 核心：创建/改进/验证/安装代理的方法论（身份先于指令、最小权限、协作协议）
  scripts/
    create_agent.py                # 交互式脚手架生成器
    validate_agents.py             # 自动验证器（frontmatter/边界/权限/协作/链接）
    _project_paths.py              # 仓库根定位辅助
  references/
    agent-template.md              # 代理模板：字段与四端兼容矩阵
    agent-anatomy.md               # 代理解剖：结构与技能/代理取舍
    agent-quality-bar.md           # 质量标准（5 项质量检查）
  templates/
    AGENT.template.md              # 新代理骨架
  <agent-name>/                    # 创建的单个代理实例（安装到客户端时复制该目录）
    AGENT.md
```

## 使用

1. 参考本目录 `SKILL.md` 的代理创建方法论
2. 使用 `templates/AGENT.template.md` 作为骨架（或 `create_agent.py` 脚手架）
3. 运行自动验证：`python agent-creator/scripts/validate_agents.py --dir <你的代理目录>`
4. 安装到客户端：`python tools/scripts/install_agent.py [--client ...] <代理目录>`
5. 经验证的代理提交到仓库 `agents/<agent-name>/`

## 技能 vs 代理

| | 技能 | 代理 |
|---|---|---|
| 回答 | 怎么做 | 谁来做 |
| 内容 | 步骤与规则 | 身份、边界、权限、协作 |
| 时机 | 用户触发场景 | 被调用/被分派 |
| 例子 | `skill-creator` | 审查者、规划者、测试者 |