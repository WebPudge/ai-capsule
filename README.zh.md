# AI 胶囊

[English](README.md)

一个 Claude Code skill，把每天的 AI 资讯变成专属于你的日报——按你的技术栈评分排序。

每天从 16 个来源抓取内容（HuggingFace 论文、OpenAI、Anthropic、DeepMind、Simon Willison、GitHub Trending、HN、Reddit 等），对每篇文章按 7 个维度打分（相关性、实用性、新颖性、深度、震撼感、认知冲击、跨界启发），再结合你的背景算出**个人匹配度**。最终你看到的日报里，对你最有用的文章排在最前面。

---

## 工作原理

每篇文章得到一个 **RUND+WPS** 分数：

| 维度 | 衡量什么 |
|-----|---------|
| R — 相关性 | 与你的技术栈匹配吗？ |
| U — 实用性 | 看完能直接做什么？ |
| N — 新颖性 | 这是真正的新信息吗？ |
| D — 深度 | 论文/源码级，还是博客摘要？ |
| W — 震撼感 | 违反直觉或算法优雅？ |
| P — 认知冲击 | 改变你的思维方式？ |
| S — 跨界启发 | 意想不到的领域组合？ |

**个人匹配度（F）** 根据你的 `familiar_areas` 配置对文章重新排序。你做 RAG 的话，Agent 架构文章比模型预训练文章排得更靠前。

每张卡片附带行动标签：
- `TRY` — 有 GitHub repo 或可运行代码
- `READ` — 值得完整阅读的深度内容
- `SCAN` — 30 秒扫标题+摘要即可

---

## 环境要求

- [Claude Code](https://claude.ai/code)（或其他 Claude agent 运行时）
- Python 3.9+

---

## 安装

**1. 克隆到 Claude skills 目录：**

```bash
git clone https://github.com/WebPudge/ai-capsule ~/.claude/skills/ai-capsule
cd ~/.claude/skills/ai-capsule
```

**2. 初始化 Python 环境：**

```bash
bash scripts/setup-env.sh
```

**3. 打开 Claude Code，说 `daily`。**

Claude 会引导你完成简短配置（角色、熟悉方向、输出语言），把配置写到 `~/.ai-capsule/config.yaml`。你的数据存在 `~/.ai-capsule/data/`，与 skill 本体分离，升级 skill 不会丢数据。

---

## 使用方式

对 Claude 说：

| 说什么 | 发生什么 |
|-------|---------|
| `daily` 或 `每日模式` | 抓取今日 AI 资讯，全部评分，输出排序日报 |
| `reconfigure` 或 `重新配置` | 重新走一遍配置引导 |
| 粘贴 URL | 对单篇文章评分 |
| 粘贴文章正文 | 对单篇文章评分 |

---

## 日报卡片格式

```
### #1 ★★★★☆ 7.4/10 · [文章标题]

🔗 https://...
📌 Simon Willison · engineer · 学习模式 · 🎯 TRY
`匹配:9` `实用:8` `新颖:7` `深度:7` | `震撼:5` `认知:6` `跨界:4` | `个人:9`

> 匹配：直接涉及 RAG 管道工程
> 实用：含可运行示例和 GitHub repo
...

**内容：** ...
**价值：** 你在做 RAG——这个实现可以在半天内替换掉你自己写的 chunker。
```

---

## 配置文件

配置存在 `~/.ai-capsule/config.yaml`（首次运行时自动创建）：

```yaml
initialized: true
default_identity: engineer      # engineer | pm | researcher | learner | founder
default_purpose: learn          # learn | solve | scout
output_language: zh             # zh | en | 其他语言名称
familiar_areas:
  - LLM 应用开发
  - RAG
  - Agent 框架
data_dir: ~/.ai-capsule/data
```

自定义配置路径：`export AI_CAPSULE_CONFIG=/path/to/config.yaml`

---

## 数据来源

开箱即用 16 个来源：

**RSS（自动抓取）：** HuggingFace Papers · OpenAI Blog · Microsoft Research · Ben's Bites · Hacker News

**URL 抓取：** Anthropic（3 个 feed）· Google DeepMind · Meta AI · Simon Willison · Eugene Yan · Chip Huyen · Product Hunt 日榜 · GitHub Trending

**搜索：** Reddit LocalLLaMA

**新增数据源：**

```bash
# RSS
bash scripts/add-source.sh --industry ai --type rss --name "我的博客" --url https://example.com/feed

# URL 抓取
bash scripts/add-source.sh --industry ai --type webfetch --name "某博客" --url https://example.com

# Tavily 搜索
bash scripts/add-source.sh --industry ai --type tavily --name "Reddit X" --query "LLM 讨论" --domains "reddit.com"
```

---

## Agent 兼容性

适配任何能抓 URL 和执行 Bash 的 agent：

| 运行时 | 使用的抓取工具 |
|-------|-------------|
| Claude Code | `WebFetch` |
| Codex / shell agent | `curl` + Python 解析 |
| Tavily agent | `tavily_extract` |
| OpenClaw | 自动 fallback 到系统 Python |

---

## 项目结构

```
ai-capsule/
  SKILL.md              # skill 入口（Claude 的执行指令）
  fetch.py              # RSS/API 抓取脚本
  sources_extract.py    # 数据源配置读取器
  requirements.txt
  scripts/
    setup-env.sh        # 一次性 Python 环境初始化
    add-source.sh       # 新增数据源
  sections/
    scoring.md          # RUND+WPS+F 评分框架
    output-format.md    # 卡片格式规范
    daily-mode.md       # 每日模式执行流程
  sources/
    ai.yaml             # AI 行业数据源列表
```

用户数据（`~/.ai-capsule/`）：
```
config.yaml             # 你的配置和偏好
data/
  daily-YYYY-MM-DD.md   # 每日日报
  history.jsonl         # 所有已评分文章
  dedup-titles.txt      # 已见标题（防止重复评分）
```

---

## License

MIT
