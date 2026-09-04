# 技能生命周期操作（Lifecycle）

PersonalWorkflow 的分发机制采用 **manifest-driven** 设计：所有安装目录内都有一个
`.personal-workflow-manifest.json`，记录名称/版本/来源/安装时间，是
update / uninstall / rollback 的唯一事实来源。

## 安装（install）

```bash
# 指定客户端（--scope 缺省会交互式询问全局/工作区）
python tools/scripts/install_skill.py --client opencode <技能目录> --scope global
python tools/scripts/install_skill.py --client claude   <技能目录> --scope workspace
python tools/scripts/install_skill.py --client codex    <技能目录> --scope global
python tools/scripts/install_skill.py --client deepseek <技能目录> --scope global

# 自动探测已安装的客户端
python tools/scripts/install_skill.py <技能目录> --scope global

# 预览将安装到哪里（不实际安装）
python tools/scripts/install_skill.py <技能目录> --scope workspace --dry-run
```

作用域：`global` = 用户级（所有项目可用）；`workspace` = 项目级（装到当前 git 仓库根，
三端都从 cwd 向上扫描到仓库根，装进子目录会漏）。完整安装运行手册见 `skill-creator/INSTALL.md`。

代理安装同构：`python tools/scripts/install_agent.py ...`

## 代理生命周期（update / uninstall / rollback）

与技能同构（manifest-driven），命令为：

```bash
# 升级（先备份旧版到 ~/.personal-workflow/backups/<name>/<旧版本>/）
python tools/scripts/update_agent.py <代理名> --source <新版代理目录或 .md 文件>

# 卸载（仅删带 manifest 标记的安装）
python tools/scripts/uninstall_agent.py <代理名>

# 回滚（恢复备份版本）
python tools/scripts/rollback_agent.py <代理名> [--version 0.1.0]
```

差异说明：
- 代理支持**目录形态**（`agents/<name>/AGENT.md`）与**单文件形态**（`<name>.md`）两种安装方式。
- 单文件形态的 manifest 是**侧车文件** `<name>.manifest.json`（与代理文件同目录），生命周期工具按此查找。
- 版本记录读取 AGENT.md frontmatter 的 `version` 字段（缺失时按 0.1.0）。

## 升级（update）

```bash
python tools/scripts/update_skill.py <技能名> --source <新版技能目录>
```

行为：
1. 读取新版的 `version`（frontmatter）
2. 自动备份当前已装版本到 `~/.personal-workflow/backups/<name>/<旧版本>/`
3. 替换为新版并更新 manifest

## 卸载（uninstall）

```bash
python tools/scripts/uninstall_skill.py <技能名>
```

行为：仅删除**带 manifest 标记**的安装（保护用户自己装的技能不受误删）；
卸载后自动回收因此变空的父目录。**卸载不创建备份**——需要时用
`install_skill.py` 重新安装即可（备份仅在 update 升级旧版时产生，
rollback 只能恢复那些被 update 备份过的版本）。

## 回滚（rollback）

```bash
python tools/scripts/rollback_skill.py <技能名>            # 回滚到最新备份
python tools/scripts/rollback_skill.py <技能名> --version 0.1.0   # 指定版本
```

行为：从备份目录恢复，更新 manifest 的 version。

## 客户端路径矩阵

| 客户端 | skills 全局（用户级） | skills 工作区（项目级，装到 git 根） | 配置 | 备注 |
|---|---|---|---|---|
| claude | `~/.claude/skills/` | `<项目根>/.claude/skills/` | `~/.claude/settings.json` | 同名时全局覆盖工作区；目录可为符号链接 |
| opencode | `~/.config/opencode/skills/` | `<项目根>/.opencode/skills/` | `~/.config/opencode/opencode.json` | 或 `skills.paths` 注册；另兼容读 `~/.claude/skills/` 与 `~/.agents/skills/` |
| codex | `~/.agents/skills/`（USER 域） | `<项目根>/.agents/skills/`（REPO 域） | `~/.codex/config.toml` | `~/.codex/skills/` 是 SYSTEM 域（内置技能），禁写；内置同名 `.system/skill-creator` 会并存 |
| deepseek | `~/.../skills/`(随版本) | 无官方约定（best-effort） | `harness.json` 等 | 用 `DEEPSEEK_HARNESS_ROOT` 覆盖，以官方文档为准 |

agents 目录（用户级）：claude `~/.claude/agents/`、opencode `~/.config/opencode/agent/`、
codex `~/.codex/agents/`（代理放置无官方约定，best-effort）、deepseek 随版本。

所有路径统一由 `tools/scripts/client_paths.py` 解析；安装器不接受硬编码路径。
Windows 下 `~` 对应 `%USERPROFILE%`；`~/.config` 对应 `%USERPROFILE%\.config`（**不是** `%APPDATA%`——opencode 在 Windows 只从 `%USERPROFILE%\.config\opencode` 加载，已实测 `%APPDATA%\opencode` 不被读取）。设 `XDG_CONFIG_HOME` 可覆盖配置根。
工作区安装的生命周期（update/uninstall/rollback）用 `--dest <项目根>/<端目录>` 指向对应位置。

## 约定

- 技能/代理 frontmatter 应含 `version: x.y.z`（语义化版本），安装/升级/回滚依赖它记账。
- 只卸载/回滚"本仓库安装的"（manifest 标记的）技能/代理，不动用户自有安装。
- 安装后需重启客户端才生效。