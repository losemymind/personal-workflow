# agent-creator 安装指引（INSTALL）

> 本文件是 agent-creator **自身的**安装运行手册。agent-creator 是自包含完整体：安装 = 把本目录完整放置到目标客户端的技能目录，跑完下方验证关卡即完成，不依赖任何外部工具。
> 覆盖已支持的 3 端：**claude / opencode / codex**。deepseek-harness 路径随版本变动，以其当前版本官方文档为准（best-effort，不在本手册范围）。
> 注意：本手册只管 **agent-creator 技能本身**的安装；它产出的**代理**如何放置到各端 agents 目录，见 SKILL.md「多客户端安装指引」。

## 0. 安装作用域（执行前必须询问用户）

| 作用域 | 含义 | 何时选 |
|---|---|---|
| **全局（global）** | 装到用户级目录，所有项目可用 | 想让每个项目都能用创建器 |
| **目标工作区（workspace）** | 装到**目标仓库根**的项目级目录，仅该仓库可用 | 只想在某个项目内启用，或想随项目提交共享 |

落点矩阵（**工作区必须装到 git 仓库根**——三端都从 cwd 向上扫描到仓库根，装进子目录会漏）：

| 端 | 全局 | 工作区 |
|---|---|---|
| claude | `~/.claude/skills/agent-creator/` | `<项目根>/.claude/skills/agent-creator/` |
| opencode | `~/.config/opencode/skills/agent-creator/` | `<项目根>/.opencode/skills/agent-creator/` |
| codex | `~/.agents/skills/agent-creator/`（USER 域） | `<项目根>/.agents/skills/agent-creator/`（REPO 域） |

询问模板：
> 「安装到**全局**（所有项目可用）还是**目标工作区**（仅当前/指定仓库）？默认全局。要装到哪几端？（默认：全部支持的端）」

## 1. 前置自检（安装前，在本技能目录内执行）

```bash
# 依赖：Python 3 + PyYAML（脚本与验证器依赖）
python -c "import yaml; print('PyYAML OK')"

# 索引与脚本可运行（三源上游代理索引，离线可用）
python scripts/search_agent_index.py --stats      # 期望：3 个来源共 568 个代理
```

完整目录必须包含：`SKILL.md`、`AGENTS.md`、`scripts/`（5 个脚本）、`indexes/upstream.db`、`references/`、`templates/`、`evolutions/`。缺任何一项（尤其 `indexes/upstream.db`）都会导致方法论不完整。

## 2. 安装（放置目录）

把**本技能整个目录**复制到第 0 步选定的落点，目录名保持 `agent-creator`。复制时排除 `__pycache__/` 等缓存噪音。

```bash
# Unix / WSL 示例（claude 全局）：
cp -r <本技能目录> ~/.claude/skills/agent-creator

# Windows PowerShell 示例（opencode 工作区，$root = 目标仓库根）：
Copy-Item -Recurse <本技能目录> "$root\.opencode\skills\agent-creator"
```

若宿主环境提供安装/生命周期工具，可使用它完成复制与记账；手册本身不依赖任何特定工具。

## 3. 验证关卡（全部通过才算安装完成）

进入**安装后**的技能目录逐项执行：

```bash
cd <安装目录>     # 例如 ~/.claude/skills/agent-creator

# 1) 索引完整性：应显示 3 个来源共 568 个代理（离线可用，无需联网）
python scripts/search_agent_index.py --stats

# 2) 脚手架 + 验证器链路：生成临时代理并通过严格验证
python scripts/create_agent.py --name install-check --mode subagent --no-interactive --out ./install-check-tmp
python scripts/validate_agents.py --strict --dir ./install-check-tmp
#    通过后删除临时目录：rm -r ./install-check-tmp（Windows: Remove-Item -Recurse .\install-check-tmp）

# 3) 关键资源就位
python -c "from pathlib import Path; [print(p, p.exists()) for p in map(Path, ['indexes/upstream.db','references','templates','scripts/validate_agents.py'])]"
```

任一项失败：删除该安装目录，修复来源后重新放置，不要带病交付。

## 4. 交付（重启 + 触发测试 + 告知路径）

1. 提示用户**重启客户端**使技能生效。
2. 用真实请求触发一次（如「帮我创建一个代理」），确认技能被加载、按 SKILL.md 执行。
3. 向用户输出**确切的安装路径**，供后续会话直接引用。

## 安装后的调用范式（代理/用户须知）

本技能内部命令一律以**技能目录为根**书写（见 SKILL.md「资源路径基准」）：

```
python scripts/<脚本>.py ...                      # 在技能目录内执行
python "<技能目录>/scripts/<脚本>.py" ...          # 在任意位置执行时加目录前缀
```

**如何定位技能目录**（客户端只把 SKILL.md 正文交给模型时）：

- **codex**：技能列表自带文件路径，直接使用。
- **claude / opencode**：按存在性依次探测——工作区候选 `<项目>/.claude/skills/agent-creator`、`<项目>/.opencode/skills/agent-creator`、`<项目>/.agents/skills/agent-creator`；全局候选 `~/.claude/skills/agent-creator`、`~/.config/opencode/skills/agent-creator`、`~/.agents/skills/agent-creator`。命中即用。

## 生命周期（客户端中立）

- **更新**：先备份已装目录，再用新版本整目录覆盖（保持目录名 `agent-creator`）。
- **卸载**：删除安装目录（建议先备份）。只删本技能的安装副本，不动其他技能。
- **回滚**：把备份目录复制回原安装位置。

## 注意事项

- **Opencode 多枢纽**：opencode 除自己的目录外还兼容读 `~/.claude/skills/` 与 `~/.agents/skills/`。同一技能别装多个枢纽，避免重复触发；本手册按端各装一处即可。
- **`~/.codex/skills` 禁写**：那是 Codex 的 SYSTEM 域（内置技能）。
- **工作区扫描方向**：客户端从 cwd 向上扫到仓库根，技能装在子目录会被漏掉——务必装到 git 仓库根。
- **与 skill-creator 的关系**：两者是平行同构的独立技能，互不依赖；可分别安装，也可都装。
