#!/usr/bin/env python3
"""
AI 胶囊抓取脚本
抓取所有数据源 → 去重 → 输出 data/pending.json
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import feedparser
import requests
import yaml
from bs4 import BeautifulSoup

SKILL_DIR = Path(__file__).parent
SOURCES_DIR = SKILL_DIR / "sources"

def _resolve_data_dir() -> Path:
    config_path = Path(os.environ.get("AI_CAPSULE_CONFIG", str(Path.home() / ".ai-capsule" / "config.yaml")))
    if config_path.exists():
        with open(config_path) as f:
            cfg = yaml.safe_load(f) or {}
        raw = cfg.get("data_dir", "")
        if raw:
            p = Path(raw.replace("~", str(Path.home()))).expanduser()
            p.mkdir(parents=True, exist_ok=True)
            return p
    fallback = Path.home() / ".ai-capsule" / "data"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback

DATA_DIR = _resolve_data_dir()
DEDUP_FILE = DATA_DIR / "dedup-titles.txt"
PENDING_FILE = DATA_DIR / "pending.json"

CUTOFF_DAYS = 3  # 只收录过去 N 天内发布的内容

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def load_dedup() -> set:
    if not DEDUP_FILE.exists():
        return set()
    return set(line.strip() for line in DEDUP_FILE.read_text().splitlines() if line.strip())


def is_duplicate(title: str, dedup: set) -> bool:
    return title.strip() in dedup


def fetch_url(url: str, timeout: int = 15) -> Optional[str]:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"  [WARN] fetch failed: {url} — {e}", file=sys.stderr)
        return None


def parse_rss(url: str) -> list[dict]:
    """解析 RSS，返回 [{title, url, summary, published_at}]，已按时效过滤"""
    cutoff = datetime.utcnow() - timedelta(days=CUTOFF_DAYS)
    try:
        feed = feedparser.parse(url)
        items = []
        for e in feed.entries[:20]:
            # 尝试解析发布时间
            pub = None
            if hasattr(e, "published_parsed") and e.published_parsed:
                try:
                    pub = datetime(*e.published_parsed[:6])
                except Exception:
                    pass
            if hasattr(e, "updated_parsed") and e.updated_parsed and pub is None:
                try:
                    pub = datetime(*e.updated_parsed[:6])
                except Exception:
                    pass

            # 有时间则过滤，无时间则放行（宁可多收不漏）
            if pub is not None and pub < cutoff:
                continue

            items.append({
                "title": e.get("title", "").strip(),
                "url": e.get("link", ""),
                "summary": e.get("summary", e.get("description", ""))[:300],
                "published_at": pub.isoformat() if pub else None,
            })
        return items
    except Exception as e:
        print(f"  [WARN] RSS parse failed: {url} — {e}", file=sys.stderr)
        return []


def soup_text(html: str, selector: str = None) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if selector:
        el = soup.select_one(selector)
        return el.get_text(" ", strip=True)[:400] if el else ""
    return soup.get_text(" ", strip=True)[:400]


# ── 各数据源抓取函数 ──────────────────────────────────────────────────────────

def fetch_huggingface() -> list[dict]:
    print("  HuggingFace Papers API...")
    cutoff = datetime.utcnow() - timedelta(days=CUTOFF_DAYS)
    data = fetch_url("https://huggingface.co/api/papers?limit=50")
    if not data:
        # 降级 WebFetch（无时间信息，放行）
        html = fetch_url("https://huggingface.co/papers")
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        items = []
        for a in soup.select("h3 a, h2 a")[:20]:
            title = a.get_text(strip=True)
            href = a.get("href", "")
            if title and href:
                items.append({
                    "title": title,
                    "url": f"https://huggingface.co{href}" if href.startswith("/") else href,
                    "summary": "",
                    "source": "HuggingFace 论文",
                })
        return items

    papers = json.loads(data)
    items = []
    skipped = 0
    for p in papers:
        title = p.get("title", "").strip()
        if not title:
            continue
        # 过滤发布时间
        pub_str = p.get("publishedAt") or p.get("published_at") or ""
        if pub_str:
            try:
                pub = datetime.fromisoformat(pub_str.replace("Z", "+00:00")).replace(tzinfo=None)
                if pub < cutoff:
                    skipped += 1
                    continue
            except Exception:
                pass
        pid = p.get("id", "")
        abstract = p.get("abstract", "")[:300]
        url = f"https://arxiv.org/abs/{pid}" if pid else ""
        items.append({
            "title": title,
            "url": url,
            "summary": abstract,
            "source": "HuggingFace 论文",
            "published_at": pub_str,
        })
    if skipped:
        print(f"    → 过滤掉 {skipped} 篇 {CUTOFF_DAYS} 天前的旧论文")
    return items


def fetch_rss_source(url: str, source_name: str, limit: int = 5) -> list[dict]:
    print(f"  {source_name} RSS...")
    items = parse_rss(url)
    for item in items:
        item["source"] = source_name
    return items[:limit]


def fetch_webpage_articles(url: str, source_name: str, limit: int = 5) -> list[dict]:
    """抓取博客首页，提取文章列表"""
    print(f"  {source_name} WebFetch...")
    html = fetch_url(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")

    items = []
    seen = set()
    # 通用策略：找 <a> 标签里包含文章标题的链接
    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        href = a["href"]
        # 过滤：标题长度合理、不是导航链接
        if len(title) < 15 or len(title) > 200:
            continue
        if any(skip in href for skip in ["#", "mailto:", "twitter", "github.com/", "javascript"]):
            continue
        if title in seen:
            continue
        seen.add(title)

        if href.startswith("/"):
            base = "/".join(url.rstrip("/").split("/")[:3])
            href = base + href
        elif not href.startswith("http"):
            continue

        items.append({
            "title": title,
            "url": href,
            "summary": "",
            "source": source_name,
        })
        if len(items) >= limit:
            break

    return items


def fetch_anthropic_engineering() -> list[dict]:
    print("  Anthropic 工程博客...")
    html = fetch_url("https://www.anthropic.com/engineering")
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    items = []
    seen = set()
    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        href = a["href"]
        if len(title) < 15 or len(title) > 200:
            continue
        if "/engineering/" not in href:
            continue
        if title in seen:
            continue
        seen.add(title)
        full_url = f"https://www.anthropic.com{href}" if href.startswith("/") else href
        items.append({
            "title": title,
            "url": full_url,
            "summary": "",
            "source": "Anthropic 工程博客",
        })
        if len(items) >= 5:
            break
    return items


def fetch_claude_blog() -> list[dict]:
    print("  Anthropic 产品博客 (claude.com/blog)...")
    html = fetch_url("https://claude.com/blog")
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    items = []
    seen = set()
    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        href = a["href"]
        if len(title) < 15 or len(title) > 200:
            continue
        if "/blog/" not in href:
            continue
        if title in seen:
            continue
        seen.add(title)
        full_url = f"https://claude.com{href}" if href.startswith("/") else href
        items.append({
            "title": title,
            "url": full_url,
            "summary": "",
            "source": "Anthropic 产品博客",
        })
        if len(items) >= 10:
            break
    return items


def fetch_producthunt_daily() -> list[dict]:
    """抓取 Product Hunt 昨日榜"""
    yesterday = datetime.now() - timedelta(days=1)
    url = f"https://www.producthunt.com/leaderboard/daily/{yesterday.year}/{yesterday.month}/{yesterday.day}"
    print(f"  Product Hunt 日榜 ({yesterday.strftime('%Y-%m-%d')})...")
    html = fetch_url(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    items = []
    seen = set()
    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        href = a["href"]
        if len(title) < 5 or len(title) > 100:
            continue
        if "/products/" not in href and "/posts/" not in href:
            continue
        if title in seen:
            continue
        seen.add(title)
        full_url = f"https://www.producthunt.com{href}" if href.startswith("/") else href
        items.append({
            "title": title,
            "url": full_url,
            "summary": "",
            "source": "Product Hunt 日榜",
        })
        if len(items) >= 10:
            break
    return items


def fetch_hacker_news() -> list[dict]:
    print("  Hacker News RSS (100分+)...")
    items = parse_rss("https://hnrss.org/newest?q=AI&points=100")
    for item in items:
        item["source"] = "Hacker News"
    return items[:5]


def fetch_reddit_localllama() -> list[dict]:
    """Reddit 直接访问不稳定，通过 old.reddit.com RSS 尝试"""
    print("  Reddit r/LocalLLaMA (RSS)...")
    try:
        url = "https://old.reddit.com/r/LocalLLaMA/hot.rss?limit=10"
        r = requests.get(
            url,
            headers={**HEADERS, "User-Agent": "ai-capsule:v1.0"},
            timeout=20
        )
        if r.status_code == 200:
            feed = feedparser.parse(r.text)
            items = []
            for e in feed.entries[:5]:
                title = e.get("title", "").strip()
                if not title or title.startswith("Comment"):
                    continue
                items.append({
                    "title": title,
                    "url": e.get("link", ""),
                    "summary": BeautifulSoup(e.get("summary", ""), "html.parser").get_text()[:200],
                    "source": "Reddit LocalLLaMA",
                })
            return items
    except Exception as e:
        print(f"  [WARN] Reddit RSS failed: {e} — 请在 Claude 评分时用 Tavily 补充", file=sys.stderr)
    return []


# ── 主流程 ────────────────────────────────────────────────────────────────────

def load_rss_sources(industry: str = "ai") -> list[tuple[str, callable]]:
    """从 sources/{industry}.yaml 加载 type=rss 的来源，返回 (name, fn) 列表"""
    path = SOURCES_DIR / f"{industry}.yaml"
    if not path.exists():
        print(f"  [WARN] 找不到 {path}，使用内置默认来源", file=sys.stderr)
        return _default_sources()
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    sources = []
    for s in (data.get("sources") or []):
        if s.get("type") != "rss":
            continue
        name = s["name"]
        handler = s.get("handler")
        url = s.get("url", "")
        limit = s.get("limit", 5)
        if handler == "huggingface":
            sources.append((name, fetch_huggingface))
        elif handler == "hacker_news":
            sources.append((name, fetch_hacker_news))
        else:
            sources.append((name, lambda u=url, n=name, lim=limit: fetch_rss_source(u, n, limit=lim)))
    return sources


def _default_sources() -> list[tuple[str, callable]]:
    """内置兜底来源，当 yaml 文件不存在时使用"""
    return [
        ("HuggingFace 论文",   fetch_huggingface),
        ("OpenAI 官方",        lambda: fetch_rss_source("https://openai.com/news/rss.xml", "OpenAI 官方")),
        ("Microsoft Research", lambda: fetch_rss_source("https://www.microsoft.com/en-us/research/feed/", "Microsoft Research")),
        ("Ben's Bites",        lambda: fetch_rss_source("https://www.bensbites.com/feed", "Ben's Bites", limit=2)),
        ("Hacker News",        fetch_hacker_news),
    ]


def main(industry: str = "ai"):
    DATA_DIR.mkdir(exist_ok=True)
    dedup = load_dedup()
    print(f"已处理标题: {len(dedup)} 条")
    print(f"数据源行业: {industry}")

    all_items = []
    failed = []

    for name, fn in load_rss_sources(industry):
        try:
            items = fn()
            new_items = [i for i in items if i.get("title") and not is_duplicate(i["title"], dedup)]
            print(f"  → {name}: 抓到 {len(items)} 条，新增 {len(new_items)} 条")
            all_items.extend(new_items)
        except Exception as e:
            failed.append(name)
            print(f"  [ERROR] {name}: {e}", file=sys.stderr)
        time.sleep(0.3)

    # 去掉标题重复（跨来源）
    seen_titles = set()
    unique_items = []
    for item in all_items:
        t = item["title"].strip()
        if t not in seen_titles:
            seen_titles.add(t)
            unique_items.append(item)

    print(f"\n待评分: {len(unique_items)} 条")
    if failed:
        print(f"失败来源: {', '.join(failed)}")

    PENDING_FILE.write_text(
        json.dumps(unique_items, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"已写入: {PENDING_FILE}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--industry", default="ai", help="行业名称（对应 sources/{industry}.yaml）")
    args = ap.parse_args()
    main(industry=args.industry)
