# skills/ — 已验证技能库

本目录存放**经验证、可复用**的技能（Skills），是 PersonalWorkflow 回馈与分发机制的目标位置。

## 准入规则

一个技能进入本目录，必须满足：

1. 通过自动验证：`python skill-creator/scripts/validate_skills.py --strict --dir skills/<name>`
2. 经过真实任务试跑（skill-creator 阶段 6）
3. 若上游已有同类技能，需完成对比择优并记录到 `skill-creator/evolutions/`

## 目录结构约定

```
skills/
├── README.md
├── CATALOG.md             # 自动生成的能力目录（勿手改；见 tools/scripts/build_catalog.py）
└── <skill-name>/          # kebab-case，与 SKILL.md 的 name 一致
    ├── SKILL.md
    ├── scripts/           # 可选：辅助脚本
    ├── references/        # 可选：参考文档
    ├── examples/          # 可选：示例
    └── templates/         # 可选：模板
```

## 与 skill-creator 的关系

- 创建/改进/验证技能 → 使用 `skill-creator/`
- 从本目录安装技能到 LLM 客户端 → 使用 `tools/scripts/install_skill.py`
- 技能更新/卸载/回滚 → 使用 `tools/scripts/` 对应命令

## 能力目录（CATALOG.md）

`CATALOG.md` 由 `tools/scripts/build_catalog.py` 从各 `SKILL.md` frontmatter 自动生成（勿手改）。它是 LLM 按需安装的检索入口：读目录匹配需求 → 命中即给条目 `install` 命令，用户确认后执行。新增/删除技能后重跑生成器（CI 用 `--check` 防漂移）。

## 回馈流程

1. 技能在本目录验证通过并稳定使用一段时间
2. 补充 frontmatter 元数据（source/date_added/author/tags）
3. 运行 `python tools/scripts/build_catalog.py` 刷新能力目录
4. 提交到仓库（含 evolutions/ 对比记录）