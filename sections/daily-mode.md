# Daily Mode Execution Flow

**Step 1: Run the fetch script**

```bash
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/fetch.py" --industry ai
```

The script reads all `type: rss` sources from `$SKILL_DIR/sources/ai.yaml` and outputs `pending.json` into the configured `data_dir` (default: `~/.ai-capsule/data`).

**Step 2: Supplemental fetch (non-RSS sources)**

First run the following to get the full fetch task list for the current industry:

```bash
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/sources_extract.py" --for-claude --industry ai
```

The output lists all non-RSS sources to fetch (includes cutoff date, URLs, and Tavily query parameters). For each source, **fetch the URL and extract article titles + URLs + summaries** using whichever tool your runtime provides:

| Runtime | Tool |
|---------|------|
| Claude Code | `WebFetch` |
| Codex / shell agents | `Bash: curl <url>` then parse with python |
| Tavily-enabled agents | `tavily_extract` for pages, `tavily_search` for query-based sources |

Skip a source on failure — do not block on it. **Use dates in article titles, body text, or page ordering to determine whether an article falls within the cutoff date; skip old articles immediately.**

**Step 3: Merge + dedup + produce the scoring list**

Use Bash to filter uniformly and output the list of titles that actually need scoring:

```bash
"$SKILL_DIR/.venv/bin/python" - << 'EOF'
import json, os, pathlib, yaml

def get_data_dir():
    cfg_path = pathlib.Path(os.environ.get("AI_CAPSULE_CONFIG", str(pathlib.Path.home() / ".ai-capsule" / "config.yaml")))
    if cfg_path.exists():
        cfg = yaml.safe_load(cfg_path.read_text()) or {}
        raw = cfg.get("data_dir", "")
        if raw:
            return pathlib.Path(raw.replace("~", str(pathlib.Path.home())))
    return pathlib.Path.home() / ".ai-capsule" / "data"

DATA_DIR = get_data_dir()
dedup = set(l.strip() for l in (DATA_DIR/"dedup-titles.txt").read_text().splitlines() if l.strip())

# Read pending.json
pending = json.loads((DATA_DIR/"pending.json").read_text())

# Filter already-scored
new_items = [i for i in pending if i.get("title","").strip() not in dedup]
skip_items = [i for i in pending if i.get("title","").strip() in dedup]

print(f"pending total: {len(pending)}")
print(f"already scored (skip): {len(skip_items)}")
print(f"to score (new): {len(new_items)}")
print()
for i, item in enumerate(new_items, 1):
    print(f"{i}. [{item['source']}] {item['title'][:60]}")
EOF
```

WebFetch-sourced entries must also pass through this same script (add them temporarily to the pending list before running), confirm they are new before scoring.

**All unprocessed entries must be scored — none may be skipped, not even low-scoring ones.**

After scoring, verify:

```bash
"$SKILL_DIR/.venv/bin/python" - << 'EOF'
import os, pathlib, yaml
def get_data_dir():
    cfg_path = pathlib.Path(os.environ.get("AI_CAPSULE_CONFIG", str(pathlib.Path.home() / ".ai-capsule" / "config.yaml")))
    if cfg_path.exists():
        cfg = yaml.safe_load(cfg_path.read_text()) or {}
        raw = cfg.get("data_dir", "")
        if raw:
            return pathlib.Path(raw.replace("~", str(pathlib.Path.home())))
    return pathlib.Path.home() / ".ai-capsule" / "data"
DATA_DIR = get_data_dir()
lines = (DATA_DIR / "dedup-titles.txt").read_text().splitlines()
print(f'dedup current total: {len(lines)}')
EOF
```

**Step 4: Write to file**

Check whether today's report file already exists:

```bash
"$SKILL_DIR/.venv/bin/python" - << 'EOF'
import os, pathlib, yaml
from datetime import date
def get_data_dir():
    cfg_path = pathlib.Path(os.environ.get("AI_CAPSULE_CONFIG", str(pathlib.Path.home() / ".ai-capsule" / "config.yaml")))
    if cfg_path.exists():
        cfg = yaml.safe_load(cfg_path.read_text()) or {}
        raw = cfg.get("data_dir", "")
        if raw:
            return pathlib.Path(raw.replace("~", str(pathlib.Path.home())))
    return pathlib.Path.home() / ".ai-capsule" / "data"
d = get_data_dir() / f"daily-{date.today()}.md"
print("EXISTS" if d.exists() else "NOT EXISTS")
EOF
```

- **EXISTS**: append newly scored cards to the end of the file, and update the total count in the header
- **NOT EXISTS**: create a new file with the full report

Write all scored results (**no card may be omitted regardless of score**) sorted by `final_score` descending, append to history.jsonl, append titles to dedup-titles.txt, and delete pending.json.

> Card headers display `total` score; card sequence number #N follows `final_score` order. `final_score` is not written into cards.
