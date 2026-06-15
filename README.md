# AI Capsule

[中文文档](README.zh.md)

An AI agent skill that scores and ranks your daily AI news feed based on what *you* actually care about.

Tell it your role and your familiar areas — it scores every article against your profile and ranks them so the most relevant ones appear first. Nothing is filtered out: every article makes it into the digest, just in the right order. An Agent engineer and a fine-tuning researcher reading the same 40 articles will get completely different ranked digests.

Built around AI industry sources by default (HuggingFace, OpenAI, Anthropic, DeepMind, HN, Reddit…), but the source system is industry-agnostic — drop in a `sources/finance.yaml` or `sources/crypto.yaml` and it works the same way.

Works with **Claude Code** and **OpenClaw**. Any agent runtime that supports `SKILL.md` can use it.

Every day it pulls from 16 sources (HuggingFace Papers, OpenAI, Anthropic, DeepMind, Simon Willison, GitHub Trending, HN, Reddit, and more), scores each article across 7 dimensions (Relevance, Utility, Novelty, Depth, Wow, Perspective, Cross-domain), and applies a **Personal Fit** score calibrated to your background. The result is a ranked daily report where the most useful articles for *you* float to the top.

![daily report example](https://via.placeholder.com/800x400?text=daily+report+screenshot)

---

## How it works

Each article gets a **RUND+WPS** score:

| Dimension | What it measures |
|-----------|-----------------|
| R — Relevance | Does it match your tech stack? |
| U — Utility | Can you do something with it? |
| N — Novelty | Is this actually new? |
| D — Depth | Paper/source-level or blog-level? |
| W — Wow | Counter-intuitive or elegant? |
| P — Perspective | Does it shift how you think? |
| S — Cross-domain | Unexpected combination? |

A **Personal Fit (F)** multiplier then re-ranks by how close each article is to your `familiar_areas`. An Agent paper ranks higher for you than for someone who only does fine-tuning.

Action tags tell you what to do with each card:
- `TRY` — has a GitHub repo or runnable code
- `READ` — deep content worth your full attention
- `SCAN` — 30-second skim is enough

---

## Requirements

- [Claude Code](https://claude.ai/code) (or any Claude agent runtime)
- Python 3.9+

---

## Installation

### Claude Code

```bash
git clone https://github.com/WebPudge/ai-capsule ~/.claude/skills/ai-capsule
cd ~/.claude/skills/ai-capsule
bash scripts/setup-env.sh
```

Then start Claude Code and say `daily`.

### OpenClaw

```bash
openclaw skills install https://github.com/WebPudge/ai-capsule
cd ~/.openclaw/skills/ai-capsule
bash scripts/setup-env.sh
```

Then say `daily` in your OpenClaw session.

---

Claude will walk you through a short setup (role, familiar areas, output language) and write your config to `~/.ai-capsule/config.yaml`. Your data lives in `~/.ai-capsule/data/` — separate from the skill, safe across updates.

---

## Usage

Say any of these to Claude:

| What you say | What happens |
|-------------|-------------|
| `daily` | Pull today's AI news, score everything, output ranked digest |
| `reconfigure` | Re-run the setup questionnaire |
| Paste a URL | Score that single article |
| Paste article text | Score that single article |

---

## Daily digest example

Real output from a June 2026 digest (engineer profile, familiar with LLM apps / RAG / Agent frameworks):

```
### #1 ★★★★★ 8.4/10 · Evoflux: Inference-Time Evolution of Executable Tool Workflows for Complex Reasoning

🔗 https://arxiv.org/abs/2606.12674
📌 HuggingFace Papers · engineer · learn mode · 🎯 READ
`R:9` `U:7` `N:9` `D:8` | `W:8` `P:8` `S:6` | `F:10`

> R: Inference-time adaptive tool workflows are directly relevant to Agent frameworks
> U: Provides new design patterns for automatic workflow optimization, with paper code
> N: Dynamically evolving workflows at inference time is a paradigm shift from static tool calls
> D: arxiv paper with full methodology and experimental results
> W: The idea of letting LLMs self-optimize their call flow at inference time is elegantly counter-intuitive
> P: Introduces "workflow-as-search-space" — a new way to think about tool use design
> S: Evolutionary algorithm concepts applied to LLM tool calling

**Summary:** Method for dynamically evolving executable tool workflows at inference time, letting LLMs automatically optimize tool call sequences for complex reasoning tasks.
**Value:** New direction for your Agent workflow design — shift from statically defined flows to inference-time self-evolution. The paper architecture is a concrete reference for retrofitting your existing tool use system.

---

### #2 ★★★★☆ 7.8/10 · Initial impressions of Claude Fable 5

🔗 https://simonwillison.net/2026/Jun/9/claude-fable-5/
📌 Simon Willison · engineer · learn mode · 🎯 READ
`R:9` `U:8` `N:8` `D:7` | `W:7` `P:7` `S:4` | `F:10`

> R: Claude Fable 5 directly affects engineers building on the Claude API
> U: Concrete capability test cases to decide whether to migrate and what to watch out for
...

**Summary:** Simon Willison's first-hand evaluation of Claude Fable 5 — capability benchmarks, new behavior patterns, differences from the previous generation.
**Value:** You're building on the Claude API — Fable 5 behavior changes affect you directly. Read this to decide whether to upgrade now and whether you need a compatibility shim.

---

### #3 ★★★★☆ 7.8/10 · Respan Gateway

🔗 https://respan.ai
📌 Product Hunt Daily · engineer · learn mode · 🎯 TRY
`R:9` `U:9` `N:7` `D:5` | `W:6` `P:6` `S:4` | `F:10`

> R: LLM gateway tooling directly applies to production LLM app engineering
> U: Two-line integration, built-in monitoring and evals — immediately usable
...

**Summary:** Two-line LLM gateway with built-in monitoring and evaluation. #3 on Product Hunt (422 votes).
**Value:** Worth a direct trial to see if it can replace your hand-rolled LLM routing and monitoring layer, saving production infrastructure time.
```

The same 40 articles ranked for a fine-tuning researcher would look completely different — the Agent workflow paper above would rank lower, and model architecture papers would float to the top.

---

## Configuration

Config lives at `~/.ai-capsule/config.yaml` (created on first run):

```yaml
initialized: true
default_identity: engineer      # engineer | pm | researcher | learner | founder
default_purpose: learn          # learn | solve | scout
output_language: en             # en | zh | any language name
familiar_areas:
  - LLM application development
  - RAG
  - Agent frameworks
data_dir: ~/.ai-capsule/data
```

Override config path: `export AI_CAPSULE_CONFIG=/path/to/config.yaml`

### Example: LLM application engineer

```yaml
initialized: true
default_identity: engineer
default_purpose: learn
output_language: en
familiar_areas:
  - LLM application development
  - RAG
  - Agent frameworks
  - Prompt Engineering
dislikes: pure marketing content, trend articles with no code
data_dir: ~/.ai-capsule/data
```

With this config, articles about RAG retrieval strategies or Agent tool-calling rank higher than general AI industry news. A paper on speech recognition scores low on Personal Fit even if the overall quality is high — it still appears in the digest, just near the bottom.

---

## Data sources

### Built-in AI sources (16 out of the box)

**RSS (auto-fetched):** HuggingFace Papers · OpenAI Blog · Microsoft Research · Ben's Bites · Hacker News

**URL fetch:** Anthropic (3 feeds) · Google DeepMind · Meta AI · Simon Willison · Eugene Yan · Chip Huyen · Product Hunt Daily · GitHub Trending

**Search:** Reddit LocalLLaMA

### Extend to other industries

Sources are organized by industry file. Add a new industry by creating `sources/{industry}.yaml`:

```bash
# Add a source to the AI industry list
bash scripts/add-source.sh --industry ai --type rss --name "My Blog" --url https://example.com/feed

# Start a new industry (e.g. finance, crypto, security)
cp sources/ai.yaml sources/finance.yaml
# then edit sources/finance.yaml with finance-specific feeds

# Run daily digest for a specific industry
# say "daily --industry finance" to Claude
```

Three source types are supported in any industry:

| Type | Fetched by | Use for |
|------|-----------|---------|
| `rss` | `fetch.py` automatically | RSS/Atom feeds, APIs |
| `webfetch` | Agent at runtime | Blogs, leaderboards, pages without RSS |
| `tavily` | Agent at runtime | Reddit, forums, search-based discovery |

---

## Agent compatibility

Works with any agent that can fetch URLs and run Bash:

| Runtime | Fetch tool used |
|---------|----------------|
| Claude Code | `WebFetch` |
| Codex / shell agents | `curl` + python parse |
| Tavily-enabled agents | `tavily_extract` |
| OpenClaw | falls back to system Python gracefully |

---

## Project structure

```
ai-capsule/
  SKILL.md              # skill entrypoint (instructions for Claude)
  fetch.py              # RSS/API fetcher
  sources_extract.py    # source config reader
  requirements.txt
  scripts/
    setup-env.sh        # one-time Python venv setup
    add-source.sh       # add a data source
  sections/
    scoring.md          # RUND+WPS+F scoring framework
    output-format.md    # card format spec
    daily-mode.md       # daily mode execution flow
  sources/
    ai.yaml             # AI industry source list
```

User data (`~/.ai-capsule/`):
```
config.yaml             # your profile and preferences
data/
  daily-YYYY-MM-DD.md   # daily reports
  history.jsonl         # all scored articles
  dedup-titles.txt      # seen titles (prevents re-scoring)
```

---

## License

MIT
