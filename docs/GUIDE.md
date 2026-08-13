# User Guide

> How to actually use `web-knowledge-crawler` day to day — from your first run to mass crawls. All output lands in `知识库/` by default (see `docs/输出规范.md`).

## Quick Start

```bash
# 1. One-command setup wizard (recommended)
python setup.py          # asks a few questions → installs deps + writes .env

# 2. Run the smart guide
python app/crawl_guide.py
```

Manual install: `pip install -r requirements.txt`, then copy `.env.example` to `.env` and fill in paths.

---

## Mode 1 — Single crawl (paste a link)

`python app/crawl_guide.py` → choose **1**.

1. Paste a link — a share-copy / short link / normal URL all work; the real URL is auto-extracted.
2. The site is auto-recognized (Douyin / Bilibili / YouTube / Weibo / Xiaohongshu / …).
3. Choose whether to **chain-crawl** (also download the author's recent series).
4. Pick speed: 🐇 fast / 🚶 standard / 🐢 full.
5. Pick save location (default `知识库/指定爬取/` or custom).
6. A plain-language confirmation shows what will happen — press Enter to go.

> Tip: Ctrl+C / Ctrl+D won't crash. Invalid input falls back to defaults.

---

## Mode 2 — Mass crawl (terms × sites)

`python app/crawl_guide.py` → choose **2**.

1. **Vocabulary source** — type terms / import a messy vocab file (auto-cleaned) / use the built-in 2740-term list.
2. Terms get a **personality** detected (academic / tutorial / hot / code) → recommended content types.
3. Pick content types (papers / videos / articles / … add or remove).
4. Pick sites (skip → use recommendations).
5. Details: time range / results per site / multi-episode / attachments.
6. Pick speed. 🐇 safe-but-quick, 🚶 standard, 🐢 full.
7. Pick save location.
8. A plain-language confirmation runs a **readiness check** — per-site browser / login state is shown, and the debug browser is auto-started if needed. Then it runs, with per-item progress logs.

> Speed affects concurrency (default 3 terms at once) and inter-site delay — tuned to be safe, not to trip anti-bot red lines.

---

## Direct CLI (advanced)

```bash
# Crawl terms from a term-list file on selected sites (--terms is a file path)
python app/crawl_all.py --terms config/seeds/vocab_terms.txt --sites arxiv --max-results 5

# Custom output directory
python app/crawl_all.py --terms config/seeds/vocab_terms.txt --sites arxiv,bilibili \
    --max-results 5 --out-dir /your/output

# Whole-site crawl
python app/crawl_sites.py

# Export cookies for login-required sites
python app/export_cookies.py
python app/export_all_cookies.py
```

`python app/crawl_all.py --help` lists every flag.

---

## Speed presets

| Preset | Concurrency | Inter-site delay | Use when |
|---|---|---|---|
| 🐇 fast | high | small | You're in a hurry and trust the sites |
| 🚶 standard | 3 terms | moderate | Default, balanced safety |
| 🐢 full | low | larger | Large batches / cautious about bans |

---

## Handling common situations

### "Why did a site return 0 results?"
1. The site requires login — the guide auto-opens the login page; log in once and cookies are collected.
2. An external tool is missing (yt-dlp / Crawl4AI / Playwright…) — a clear warning is logged and that site is skipped.
3. The site is on the disabled list (very aggressive anti-bot) — logged explicitly, never faked.
4. Rate-limited — the tool auto-skips and retries.

### YouTube won't download?
YouTube needs a local proxy (e.g. Clash, port 7897); the program auto-detects it.

### Douyin / Xiaohongshu need login?
The guide auto-detects login state: no login → auto-opens the browser login page → login → auto-collects cookies → verifies.

### Where did my data go?
`知识库/{term}/{type}/{site}/00_date_title_size/` + `meta.json`, plus an HTML double-save for browsing. Override with `--out-dir`.

### Ctrl+C during a run?
Safe — downloaded items are already saved; the rest is skipped. Interrupting is fine.

---

## Troubleshooting matrix

| Symptom | Likely cause | Fix |
|---|---|---|
| `403` / empty on a site | Cookie expired | Re-login via guide, or `python app/export_cookies.py` |
| "浏览器没开" in readiness check | Debug browser not running | Guide auto-starts it (or start Chrome with `--remote-debugging-port=9222`) |
| "未登录" for a login site | Missing cookie | Run a single crawl once to complete login |
| Video downloads fail | yt-dlp missing / YouTube needs proxy | Install yt-dlp, or start local proxy |
| GitHub/Gitee rate-limited | No token | Set `GH_TOKEN` / `GITEE_TOKEN` in `.env` |
