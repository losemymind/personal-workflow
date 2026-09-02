# PersonalWorkflow 开发计划 v1.0

> 目标：完整实现 PersonalWorkflow 的最终形态——用户安装到目标项目后，通过 AGENTS.md 引导，检索/创建/对比/验证/安装/回馈技能与代理的完整闭环。

## 1. 需求基线（已确认）

| 维度 | 决策 |
|---|---|
| 范围 | 完整实现最终形态（分发闭环 + 工具化补全） |
| 安装器 | 脚本 + 文档指导（install_skill.py / install_agent.py + SKILL 指导） |
| 客户端 | 四端并行：claude / opencode / codex / deepseek-harness |
| 生命周期 | 完整四操作：install / update / uninstall / rollback + 版本记录 |
| 顶层结构 | `skills/` + `agents/` + `tools/` 三目录 |
| 工具化 | 全套：create_skill.py 脚手架 + version 字段 + evals 模板 + 触发测试运行器 |
| AGENTS.md | 引导型（定义路径、引用命令，不自动执行） |

## 2. 目标架构

```
PersonalWorkflow/
├── AGENTS.md                    ← [W2] 分发入口：检索→对比→创建→验证→安装→回馈
├── README.md                    ← [W5] 更新为最终形态说明
├── skills/                      ← [W1] 已验证技能库（回馈目标位置）
├── agents/                      ← [W1] 已验证代理库
├── tools/                       ← [W1] 基础工具集
│   ├── scripts/
│   │   ├── install_skill.py     ← [W3b] 四端安装
│   │   ├── install_agent.py     ← [W3b] 四端代理安装
│   │   ├── update_skill.py      ← [W3c] 升级（保留旧版备份）
│   │   ├── uninstall_skill.py   ← [W3c] 卸载
│   │   ├── rollback_skill.py    ← [W3c] 回滚到上一版本
│   │   └── client_paths.py      ← [W3a] 四端路径矩阵（共享模块）
├── skill-creator/               ← （现有，工具化补全 W4）
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── create_skill.py      ← [W4a] 脚手架生成器（NEW）
│   │   ├── run_trigger_tests.py ← [W4c] 触发测试运行器（NEW）
│   │   ├── build_index.py / search_index.py / compare_skills.py / validate_skills.py
│   ├── templates/
│   │   ├── SKILL.template.md    ← [W4b] 加 version 字段
│   │   └── evals.json.template  ← [W4c] 测试用例模板（NEW）
│   └── examples/ references/ indexes/ evolutions/（现有）
└── agent-creator/               ← 预留（后续工作）
```

## 3. 工作分解与交付顺序

### W1：顶层目录骨架
- 创建 `skills/` `agents/` `tools/` 三个目录
- 各目录一份 README：用途、准入规则（验证通过才能入库）、目录结构约定

### W2：AGENTS.md（引导型）
- 定义完整路径：检索上游（索引）→ 创建（skill-creator）→ 对比择优 → 验证 → 安装 → 回馈
- 引用各命令（不自动执行），说明各客户端如何引入此文件

### W3：分发与生命周期（核心交付）
- W3a `client_paths.py`：四端路径矩阵（用户级/项目级、skills/agents 路径、配置文件位置）
- W3b `install_skill.py` / `install_agent.py`：
  - 从 PersonalWorkflow 源目录复制到目标客户端目录
  - 校验（源技能需通过 validate_skills / 基本结构检查）
  - 写安装清单（.personal-workflow-manifest.json：名称/版本/源路径/目标路径/时间）
  - `--client` 指定客户端（不传则自动探测已安装客户端）
- W3c `update_skill.py` / `uninstall_skill.py` / `rollback_skill.py`：
  - update：备份旧版本到 `~/.personal-workflow/backups/<name>/<version>/` → 复制新版
  - uninstall：删除目标 + 清理清单
  - rollback：从备份恢复并更新清单
  - 版本记录：读取 SKILL.md frontmatter 的 `version` 字段（W4b）

### W4：skill-creator 工具化补全
- W4a `create_skill.py`：交互式脚手架（名称/分类/风险/客户端）→ 生成完整骨架目录（SKILL.md + 可选 scripts/references/examples/templates）
- W4b `version` 字段：SKILL.template.md 增加 `version: "0.1.0"`；validate_skills.py 校验格式（x.y.z）
- W4c `evals.json.template` + `run_trigger_tests.py`：触发查询集模板（应触发/不应触发各 10 条），运行器输出触发率对比

### W5：文档整合
- 根 README.md 更新为最终形态说明（安装流程、四端支持、目录导览）
- skill-creator SKILL.md 增加阶段引用（安装器使用、version 规范）
- 新增 references/skill-lifecycle.md（生命周期操作说明）

### W6：端到端验证
- 模拟：create_skill.py 生成测试技能 → 四端 install → update → rollback → uninstall 全链路
- 回归：validate_skills.py --strict 通过

## 4. 版本与兼容约定

- 技能 version 采用语义化 `x.y.z`（初版 0.1.0，稳定 1.0.0）
- 所有工具脚本兼容 Windows（PowerShell）/类 Unix，路径统一走 `client_paths.py`
- 安装清单 JSON 是生命周期操作的唯一事实来源（manifest-driven）

## 5. 风险与缓解

| 风险 | 缓解 |
|---|---|
| DeepSeek Harness 路径未知 | client_paths.py 中标记 TODO+可覆盖，探测失败时输出提示并允许手动指定 |
| 客户端路径随版本变化 | 矩阵集中在 client_paths.py 单一文件，便于更新；文档标注"以官方文档为准" |
| 误卸载用户已有技能 | uninstall 前校验清单（manifest 中源路径必须来自本仓库）|

## 6. 验收标准

1. `python tools/scripts/install_skill.py --client opencode <技能>` 安装成功且清单生成
2. update/uninstall/rollback 三操作数据一致（清单为准）
3. `validate_skills.py --strict` 通过；`create_skill.py` 产出可通过验证
4. AGENTS.md 可被四端客户端引用（路径说明准确）