# 技能生命周期操作（Lifecycle）

PersonalWorkflow 的分发机制采用 **manifest-driven** 设计：所有安装目录内都有一个
`.personal-workflow-manifest.json`，记录名称/版本/来源/安装时间，是
update / uninstall / rollback 的唯一事实来源。

## 安装（install）

```bash
# 指定客户端
python tools/scripts/install_skill.py --client opencode <技能目录>
python tools/scripts/install_skill.py --client claude   <技能目录>
python tools/scripts/install_skill.py --client codex    <技能目录>
python tools/scripts/install_skill.py --client deepseek <技能目录>

# 自动探测已安装的客户端
python tools/scripts/install_skill.py <技能目录>

# 预览将安装到哪里（不实际安装）
python tools/scripts/install_skill.py <技能目录> --dry-run
```

代理安装同构：`python tools/scripts/install_agent.py ...`

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
备份保留在 `~/.personal-workflow/backups/`，可回滚恢复。

## 回滚（rollback）

```bash
python tools/scripts/rollback_skill.py <技能名>            # 回滚到最新备份
python tools/scripts/rollback_skill.py <技能名> --version 0.1.0   # 指定版本
```

行为：从备份目录恢复，更新 manifest 的 version。

## 客户端路径矩阵

| 客户端 | skills 目录（用户级） | agents 目录（用户级） | 配置 | 备注 |
|---|---|---|---|---|
| claude | `~/.claude/skills/` | `~/.claude/agents/` | `~/.claude/settings.json` | 项目级 `.claude/` |
| opencode | `~/.config/opencode/skills/` | `~/.config/opencode/agent/` | `~/.config/opencode/opencode.json` | 项目级 `.opencode/` 或 `skills.paths` |
| codex | `~/.codex/skills/` | `~/.codex/agents/` | `~/.codex/config.toml` | 需要 experimental skills 特性 |
| deepseek | `~/.../skills/`(随版本) | `~/.../agents/`(随版本) | `harness.json` 等 | 用 `DEEPSEEK_HARNESS_ROOT` 覆盖，以官方文档为准 |

所有路径统一由 `tools/scripts/client_paths.py` 解析；安装器不接受硬编码路径。
Windows 下 `~` 对应 `%USERPROFILE%`，`~/.config` 对应 `%APPDATA%`。

## 约定

- 技能 frontmatter 应含 `version: x.y.z`（语义化版本），安装/升级/回滚依赖它记账。
- 只卸载/回滚"本仓库安装的"（manifest 标记的）技能，不动用户自有安装。
- 安装后需重启客户端才生效。