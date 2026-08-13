<p align="center">
  <kbd>English</kbd> · <kbd><a href="README_zh.md">简体中文</a></kbd>
</p>

<p align="center">
  <a href="https://github.com/SpiralQWQ/web-knowledge-crawler"><img src="https://img.shields.io/github/stars/SpiralQWQ/web-knowledge-crawler" alt="GitHub stars"></a>
  <a href="https://github.com/SpiralQWQ/web-knowledge-crawler/releases"><img src="https://img.shields.io/github/v/release/SpiralQWQ/web-knowledge-crawler" alt="release"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-3776AB" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-AGPL%203.0-blue" alt="license"></a>
  <a href="#"><img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey" alt="platform"></a>
  <a href="https://github.com/SpiralQWQ/web-knowledge-crawler/commits"><img src="https://img.shields.io/github/last-commit/SpiralQWQ/web-knowledge-crawler" alt="last commit"></a>
  <a href="https://github.com/SpiralQWQ/web-knowledge-crawler/issues"><img src="https://img.shields.io/github/issues/SpiralQWQ/web-knowledge-crawler" alt="issues"></a>
</p>

<h1 align="center">web-knowledge-crawler</h1>

<p align="center">Systematically crawl the web for domain knowledge by vocabulary — papers, videos, articles, code, datasets, courses and more.</p>
<p align="center">Give it a term or a link. It searches 51 websites, downloads raw files, and organizes them into a browsable knowledge base.</p>
<p align="center"><b>Raw data only — no parsing/OCR. Downstream (MinerU / ASR / RAG) is up to you.</b></p>

## 💛 Support / Tip

If this project has helped you in any way, you're welcome to buy me a coffee. It's completely voluntary — the project stays free and open-source regardless. For an independent developer, every small token of appreciation matters.

<p align="center">
  <img src="assets/donate_wechat.jpg" alt="WeChat Pay" width="200">
  <img src="assets/donate_alipay.jpg" alt="Alipay" width="200">
</p>

<p align="center"><i>Thanks for reading all the way down here. 🙏</i></p>

## What It Does

web-knowledge-crawler is a **domain knowledge crawler**. You feed it professional vocabulary (2740 terms built-in) or a share link, and it:

- Searches **51 websites** across 8 content types (papers / videos / articles / code / datasets / courses / docs / Q&A)
- **Downloads raw files** of every type — PDF, MP4, code repos, images, audio, archives
- **Organizes** them into a `知识库/` (knowledge base) directory: `{term}/{site}/{type}/00_date_title_size/` + `meta.json`
- Filters noise, deduplicates (SQLite), and produces clean text for HTML pages

**Raw data only.** No parsing, no OCR, no AI note generation — that's a separate pipeline (e.g. MinerU / ASR / RAG).

### Pipeline

```
term/link → smart guide (recommend types/sites) → searchers (51 sites) → filter + dedup (SQLite)
        → type-routed download (yt-dlp / direct / render) → knowledge base + meta.json
```

## 🌐 Supported Sites (51 / 8 types)

| Type | Sites |
|---|---|
| 📄 **Papers (10)** | arXiv · dblp · Semantic Scholar · PapersWithCode · ACL Anthology · OpenReview · NeurIPS · ICML · ICLR · Google Scholar |
| 🎬 **Video (3)** | Bilibili · YouTube · Douyin |
| 📝 **Articles (13)** | Juejin · CSDN · Zhihu · SegmentFault · InfoQ · SSPai · 36Kr · Medium · OSChina · Hacker News · Weibo · Alignment Forum · Xiaohongshu |
| 💻 **Code (2)** | GitHub Topics · Gitee |
| 📊 **Datasets (2)** | Hugging Face · Kaggle |
| 🎓 **Courses (3)** | Coursera · edX · Khan Academy |
| 📚 **Docs (3)** | Cursor · Claude Code Docs · OpenCode |
| ❓ **Q&A (1)** | LeetCode |

> Some sites require login state or a debug browser (see Configuration); a few disabled sites are explicitly skipped with a warning — never silently fake success.

## 🧭 How the Smart Guide Works (point-and-ask)

`python app/crawl_guide.py` — the guide asks in plain language; you just pick a number / press Enter.

### ① Single crawl (paste a link)

```
1. Paste a link (video/article/page/share-copy — the real URL is auto-extracted)
2. Site is auto-recognized (Douyin/Bilibili/YouTube/Weibo/Xiaohongshu...)
3. Asked whether to chain-crawl (download the author's series)
4. Pick speed (fast / standard / full)
5. Pick save location (default or custom)
6. Plain-language confirm → download (with progress bar) → saved
```

### ② Mass crawl (pick terms & sites)

```
1. Pick vocabulary source: type / import a messy vocab file (auto-cleaned) / built-in 2740 terms
2. Type terms → "term personality" detected (academic/tutorial/hot/code) → content types recommended
3. Pick content types (papers/video/articles/... add or remove)
4. Pick sites (skip → use recommendations)
5. Details: time range / results per site / multi-episode / attachments
6. Pick speed (🐇 fast=safe-but-quick / 🚶 standard / 🐢 full)
7. Pick save location
8. Plain-language confirm (with readiness check: browser/login state per site) → run → per-item progress logs
```

> Ctrl+C / Ctrl+D won't crash; invalid input falls back to defaults; your last choices are remembered as defaults.

## Feature Overview

| | Feature | Description |
|---|---|---|
| 🔗 | Single crawl | Paste a link → recognize site → download, with optional chain crawl |
| 🌳 | Chain crawl | Douyin/Xiaohongshu/Weibo via debug browser; Bilibili/YouTube via yt-dlp |
| 📚 | Mass crawl | Terms → types → sites → details → speed → batch run |
| 🔐 | Auto-login | Detect login-required sites, open login page, auto-collect cookies, verify |
| 🧠 | Term intelligence | Auto-clean messy vocab, detect term personality, recommend types |
| 📊 | Sorting | GitHub by stars, arXiv by latest/relevance (`--sort`) |
| 🗂️ | Organized output | `知识库/{term}/{site}/{type}/00_date_title_size/` + meta.json + HTML double-save |
| 🛡️ | Anti-block | Multi-engine fallback, cookie injection, stealth browsers, rate limiting, progress logs |

## 🧪 Usage Examples

### Example 1: Crawl reinforcement-learning papers from arXiv

```bash
python app/crawl_all.py --terms "reinforcement learning" --sites arxiv --max-results 5
```

Expected output (per-item progress):
```
📦 开始爬取词汇[1/1]: reinforcement learning
  • [arxiv] 搜索到 5 条 → 过滤后 5 条
  ⏳ 下载 [1/5] A Deep Reinforcement Learning Approach...
  ✔ [arxiv] 完成: 5/5 下载
✅ 爬取完成
Saved: 知识库/reinforcement_learning/arxiv/论文/00_20260812_.../xxx.pdf
```

### Example 2: Crawl a single Douyin video (smart guide)

```bash
python app/crawl_guide.py
# Choose 1 (single crawl) → paste a Douyin share copy → confirm → auto-downloads to 知识库/指定爬取/
```

### Example 3: Mass crawl (guided)

```bash
python app/crawl_guide.py
# Choose 2 (mass crawl) → type "transformer" → accept recommended types → pick sites → pick speed → confirm
```

## Requirements

- **Python 3.10+** (Windows / Linux)
- Base deps: `pip install -r requirements.txt`
- Optional external tools (graceful degradation if missing, see Configuration):
  - **yt-dlp** (video/audio download)
  - **Crawl4AI / Scrapling / patchright / Playwright** (HTML rendering / anti-bot)

## Quick Start

```bash
# 1. Clone
git clone https://github.com/SpiralQWQ/web-knowledge-crawler
cd web-knowledge-crawler

# 2. One-command setup wizard (recommended):
#    Answer a few questions → installs dependencies + generates .env, no docs needed
python setup.py

# 3. Run
python app/crawl_guide.py      # 🧭 Smart guide (recommended)
python app/crawl_all.py        # Mass crawl (advanced)
python app/crawl_all.py --sites arxiv,bilibili --max-results 5 --out-dir /path/to/output
python app/crawl_sites.py      # Whole-site crawl
```

> Manual install is also fine: `pip install -r requirements.txt`, then copy `.env.example` to `.env` and fill in paths.
> First run: the guide will check site dependencies (browser / login state) and walk you through.

## Configuration

### Environment (`.env`, copy from `.env.example`)

| Variable | Purpose |
|---|---|
| `CRAWL4AI_PY` | Python interpreter of the Crawl4AI environment |
| `DD_YTDLP` | yt-dlp executable (video/audio) |
| `KC_COOKIE_BROWSER` | Browser for cookie injection (`edge` / `chrome` / `firefox`) |
| `GH_TOKEN` / `GITEE_TOKEN` | (optional) GitHub/Gitee API tokens to raise search rate limits |

### External tools (`config/collector.yaml`)

| Tool | Used for | If missing |
|---|---|---|
| Crawl4AI | HTML rendering | that site skipped with a warning |
| Scrapling / patchright | JS-heavy / anti-bot sites | same |
| Playwright | CDP automation / login | auto-login unavailable |
| yt-dlp | Video / audio download | video sites skipped |
| MediaCrawler / Spider_XHS | Login-required social sites | that site skipped |

> Most tools are optional. If a tool is missing, the crawler logs a clear warning and skips that site — **it degrades gracefully, never silently.**

## Directory Structure

```
app/                Entry points (crawl_guide / crawl_all / crawl_sites / export_cookies)
core/               Engine
  ├─ domain/        Vocabulary / personality / site mapping / login rules
  ├─ interaction/   Interactive prompts & preferences
  ├─ auth/          Login automation / cookies
  ├─ download/      Download / persist / dedupe / scheduler
  ├─ engines/       51 site searchers
  ├─ filter/        Relevance & noise filtering
  └─ bridges/       Renderer subprocess bridges
config/             Static config (collector.yaml / seeds/ 2740 terms)
tests/              Exhaustive / task-audit / smoke tests
docs/               Directory contract / output spec
```

## 🏗 Architecture

```
app/        Entry layer (crawl_guide smart guide / crawl_all mass / crawl_sites whole-site)
   │
   ▼
core/       Engine layer (layered, one-way dependency)
   ├─ interaction → domain (logic: vocabulary/personality/site mapping)
   ├─ download / engines / filter (execution: download/search/filter)
   ├─ auth (login/cookie)  └─ bridges (renderer bridges)
   │
   ▼
config/ → data/ (cookie/db) → 知识库/ (crawl output)
```

Dependency direction: `app → core.* → shared`, no circular imports, ≤3 directory levels (see `docs/目录契约.md`).

## 🧰 Tech Stack

- **Python 3.10+** / asyncio / SQLite (dedup)
- **yt-dlp**: video/audio download
- **Crawl4AI / Scrapling / patchright / Playwright**: HTML rendering, JS-heavy sites, stealth browsers
- **trafilatura**: text denoise (HTML double-save)
- **rank_bm25 / yake**: relevance & keyword filtering
- **text2vec**: semantic expansion (optional)

## 🙏 Acknowledgements

This project depends on the following open-source projects:

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) · [Crawl4AI](https://github.com/unclecode/crawl4ai) · [Scrapling](https://github.com/D4Vinci/Scrapling) · [patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) · [Playwright](https://github.com/microsoft/playwright) · [trafilatura](https://github.com/adbar/trafilatura) · [rank-bm25](https://github.com/dorianbrown/rank_bm25) · [yake](https://github.com/LIAAD/yake)

## 📌 Roadmap

- [ ] Polished chain-crawl for Xiaohongshu / Weibo (browser-based)
- [ ] Full 2740-term batch run validation
- [ ] Finer content-type crawling (Douyin image albums / Xiaohongshu notes, etc.)
- [ ] GUI (web/desktop guide)

## 📮 Feedback & Contributing

Contributions of all kinds are welcome — bug reports, new searchers, docs, features.

- Found a bug? Open an [Issue](https://github.com/SpiralQWQ/web-knowledge-crawler/issues)
- PRs welcome — please read [CONTRIBUTING.md](CONTRIBUTING.md) first
- Security issue? See [SECURITY.md](SECURITY.md)
- Community rules: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Changes history: [CHANGELOG.md](CHANGELOG.md)
- Deeper docs: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/GUIDE.md](docs/GUIDE.md) · [docs/目录契约.md](docs/目录契约.md) · [docs/输出规范.md](docs/输出规范.md)

Before submitting, run the exhaustive/smoke tests under `tests/` to confirm no regression.

## ❓ FAQ

**Q: Why does a site return 0 results?**
Possible reasons: ① the site requires login (the guide auto-opens the login page); ② an external tool is missing (a clear warning is logged); ③ the site is on the disabled list (very aggressive anti-bot); ④ rate-limited (auto-skip & retry).

**Q: Do I need to install yt-dlp / Crawl4AI?**
No. Missing tools cause graceful degradation (a clear warning + that site skipped); the rest works normally.

**Q: Where and how is data stored?**
Default `知识库/{term}/{site}/{type}/00_date_title_size/` + `meta.json`. Override with `--out-dir`. See `docs/输出规范.md`.

**Q: Will mass crawling get me banned?**
Built-in safety: low concurrency (default 3 terms) + inter-site delay + timeout retry — never touches anti-bot red lines.

**Q: YouTube won't download?**
YouTube needs a local proxy (e.g. Clash, port 7897); the program auto-detects it.

**Q: Douyin/Xiaohongshu need login?**
The guide auto-detects login state: no login → auto-open browser login page → login → auto-collect cookies → verify.

**Q: Can I use it commercially?**
Yes, under AGPL-3.0 (derivatives must be open-sourced); for closed-source commercial use see `COMMERCIAL.md`.

## Disclaimer

This tool is for **personal research and study** of public content. You are responsible for:
- Respecting each website's terms of service and `robots.txt`
- Complying with local laws and copyright regulations
- Not using it for mass scraping, DDoS, or any illegal purpose

The project does not bundle any crawled content; you crawl at your own responsibility.

## License

AGPL-3.0 — see [LICENSE](LICENSE). Commercial use is possible, see [COMMERCIAL.md](COMMERCIAL.md).
