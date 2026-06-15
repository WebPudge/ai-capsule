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

```
/plugin marketplace add WebPudge/ai-capsule
/plugin install ai-capsule@ai-capsule
```

Then run the environment setup:

```bash
bash ~/.claude/plugins/ai-capsule/scripts/setup-env.sh
```

Then say `daily`.

### OpenClaw

```bash
openclaw skills install ai-capsule
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

Real output from a June 2026 digest — engineer profile, familiar with LLM app development / RAG / Agent frameworks:

---

### #1 ★★★★☆ 6.9/10 · [Conan — Claude Code Visual Control Panel](https://conan.sh)

🔗 [https://conan.sh](https://conan.sh)
📌 **Product Hunt Daily** · engineer · learn mode · 🎯 **TRY**
`R:9` `U:8` `N:7` `D:5` | `W:6` `P:6` `S:3` | `F:9`

| Dim | |
|---|---|
| **R** | A direct companion tool for Claude Code, immediately useful for engineers who use it heavily |
| **U** | Downloadable macOS app, dmg available on GitHub Releases, usable today |
| **N** | A visual HUD for Claude Code fills a real gap — context window monitoring solves a daily pain point |
| **D** | Product page, clear feature descriptions but no technical implementation details |
| **W** | Context monitoring solves a real developer pain point more elegantly than expected |
| **P** | Visualizing runtime state as a HUD reframes the experience from "black box" to observable |
| **S** | No cross-domain inspiration |

**Summary:** Native macOS app that adds a real-time HUD to Claude Code — Timeline (streaming prompt/tool call view), Context window usage monitor, Pulse throughput, Skills & MCP visualizer. $29 one-time.
**Value:** You use Claude Code heavily — Conan immediately shows how much context each conversation consumes and which tools fire how often, so you know when to /compact before the context fills up silently.

---

### #3 ★★★★☆ 7.0/10 · [Mapping SQLite result columns back to their source table.column](https://simonwillison.net/2026/Jun/13/sqlite-column-provenance/)

🔗 [https://simonwillison.net/2026/Jun/13/sqlite-column-provenance/](https://simonwillison.net/2026/Jun/13/sqlite-column-provenance/)
📌 **Simon Willison** · engineer · learn mode · 🎯 **TRY**
`R:7` `U:8` `N:7` `D:7` | `W:5` `P:5` `S:3` | `F:8`

| Dim | |
|---|---|
| **R** | SQL result provenance is a real problem in RAG and Agent tool-call workflows |
| **U** | All three approaches include code; column_provenance.py on GitHub is ready to use |
| **N** | Bridging ctypes to sqlite3_column_table_name() is a trick most developers don't know |
| **D** | Covers the rationale and tradeoffs of three approaches with working code |
| **W** | The ctypes bypass of Python's stdlib has some elegance, though it's a known pattern |
| **P** | Reveals that SQLite internally computes this via SQLITE_ENABLE_COLUMN_METADATA — a hidden capability |
| **S** | No cross-domain perspective |

**Summary:** Simon Willison uses Claude Code to research how to map SQL query result columns back to their source table.column. Explores three approaches — apsw, ctypes bridge to SQLite C API, and EXPLAIN analysis — with code published on GitHub.
**Value:** When your RAG Agent executes SQL and needs to explain the results, column_provenance.py lets it return "users.name from the users table" instead of a bare column name — a direct upgrade for multi-table JOIN explainability.

---

### #5 ★★★★☆ 6.9/10 · [Why AI hasn't replaced software engineers, and won't](https://simonwillison.net/2026/Jun/14/why-ai-hasnt-replaced-software-engineers/)

🔗 [https://simonwillison.net/2026/Jun/14/why-ai-hasnt-replaced-software-engineers/](https://simonwillison.net/2026/Jun/14/why-ai-hasnt-replaced-software-engineers/)
📌 **Simon Willison** · engineer · learn mode · 🎯 **READ**
`R:8` `U:6` `N:6` `D:7` | `W:6` `P:8` `S:3` | `F:9`

| Dim | |
|---|---|
| **R** | Directly addresses AI's impact on software engineers — a core concern for engineer readers |
| **U** | Provides the NY WARN Act data as a concrete source, and the decision/verification/understanding framework |
| **N** | Counters the popular "threshold theory" with three specific cognitive bottlenecks |
| **D** | Arvind Narayanan's deep analysis with academic grounding; Simon adds his own perspective |
| **W** | No counter-intuitive finding — the three-part framework lands in expected territory |
| **P** | "Decision-making and accountability matter more than code input speed" reframes what engineers do |
| **S** | Pulls in labor economics data (WARN Act) to analyze a tech trend |

**Summary:** Arvind Narayanan and Sayash Kappor argue that AI hasn't replaced software engineers because of three irreducible bottlenecks: decision-making and specification, verification and accountability, and deep contextual understanding. Backed by NY WARN Act filings showing zero companies attributed layoffs to AI.
**Value:** You're an AI application engineer — this piece articulates clearly why you haven't been replaced. Decision-making and verification are exactly what you do every day; use this framework to explain AI tool boundaries to PMs, managers, or clients.

---

The same 31 articles ranked for a fine-tuning researcher would look completely different — the SQLite and Agent tooling pieces above would rank lower, and model architecture or training papers would float to the top.

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
