# Architecture

> Overview of `web-knowledge-crawler`'s internal structure, data flow, and extension points. For where files live, see `docs/directory-contract.md`; for output format, see `docs/output-spec.md`.

## High-Level Layout

```
app/                 Entry layer — thin, no business logic
  ├─ crawl_guide.py      🧭 Smart interactive guide (single crawl / mass crawl)
  ├─ crawl_all.py        Mass crawl CLI (terms / sites / filters)
  ├─ crawl_sites.py      Whole-site crawl
  ├─ cli.py              Shared CLI helpers
  └─ export_cookies.py / export_all_cookies.py   Cookie export
      │
      ▼  (one-way dependency: app → core.*)
core/                Engine layer — layered, no circular imports
  ├─ domain/           Vocabulary / term personality / site mapping / login rules
  ├─ interaction/      Interactive prompts & user preferences (remembered)
  ├─ auth/             Login automation & cookie collection/verification
  ├─ download/         Download / persist / dedupe (SQLite) / scheduler
  ├─ engines/          Site searchers (one file per site, @register)
  ├─ filter/           Relevance & noise filtering
  ├─ bridges/          Renderer / CDP / subprocess bridges (Crawl4AI, Playwright…)
  ├─ get_cookie/       Browser cookie harvest helpers
  └─ config.py         Central config loader (.env + config/collector.yaml)
      │
      ▼
config/ → data/ (cookie/db) → 知识库/ (crawl output)
```

Dependency rule: `app → core.*`, **≤3 directory levels**, no circular imports. `core/config.py` is the single config entry; `core/engines/base.py` is the single searcher base. New modules must respect this (enforced by `tests/post_refactor_smoke.py`).

## Pipeline / Data Flow

```
term / link
   │
   ▼
[app] smart guide → picks content types & sites
   │
   ▼
[core/domain]   term personality → recommended types; site mapping → engine registry
   │
   ▼
[core/engines]  search N sites in parallel (asyncio), each engine returns structured results
   │
   ▼
[core/filter]   relevance score (BM25 / keywords / URL heuristics), noise removal
   │
   ▼
[core/download] SQLite dedupe → type-routed downloader
   │                ├─ direct (HTTP)
   │                ├─ yt-dlp (video / audio)
   │                └─ renderer bridge (JS-heavy / anti-bot pages)
   ▼
知识库/{term}/{type}/{site}/00_date_title_size/  +  meta.json
```

Each stage is an asyncio coroutine; the whole pipeline is orchestrated in `core/download` (scheduler) with low default concurrency (3 terms) + inter-site delay + timeout retry.

## Searcher Engines (`core/engines/`)

Every site has one file that implements the base searcher pattern and registers itself:

```python
from core.engines.base import BaseSearcher, register

@register
class ArxivSearcher(BaseSearcher):
    name = "arxiv"
    ...
```

Engines are grouped by transport strategy:

| Family | Files (examples) | Technique |
|---|---|---|
| **Academic** | `arxiv.py`, `dblp.py`, `semanticscholar.py`, `openalex_search.py`, `paperswithcode.py`, `acl_anthology.py`, `conferences.py` | REST APIs / OAI-PMH / feed |
| **Web / RSS** | `rss_search.py`, `sitemap_search.py`, `hackernews.py`, `tech_news.py` | RSS / sitemap / HTML |
| **Video** | `bilibili.py`, `video_search.py` (YouTube/Douyin) | yt-dlp extractor / CDP |
| **Community** | `zhihu.py`, `community_search.py`, `ai_platforms.py`, `code_platform.py` | HTML / API |
| **JS-heavy / anti-bot** | `crawl4ai_search.py`, `playwright_search.py`, `scrapling_search.py`, `cdp_search.py` | renderer bridge or CDP real browser |

A searcher may also depend on external tools (Crawl4AI, Playwright, yt-dlp, MediaCrawler). When a tool is missing, the engine **skips with a clear warning** — never silently fakes success.

## Key Cross-Cutting Concepts

### Term Intelligence (`core/domain`)
- Auto-cleans messy vocabulary input.
- Detects "term personality" (academic / tutorial / hot / code) to recommend content types.
- Maps terms → recommended sites via `SITE_TYPE_MAP`.

### Login & Cookies (`core/auth` + `core/get_cookie`)
- Detects login-required sites; opens the login page; harvests cookies from the configured browser (`KC_COOKIE_BROWSER`); verifies login state.
- Login-required sites must match **key cookie columns** to avoid false-positive login state.

### Anti-Block Strategy
Multi-engine fallback → cookie injection → stealth renderer (Crawl4AI / Scrapling / patchright / Playwright) → CDP real-browser → low concurrency + delays.

### Output (`知识库/`)
Each item is saved under `知识库/{term}/{type}/{site}/00_日期_标题_大小/` with a `meta.json`, plus an HTML double-save (raw + denoised body) for browsability. See `docs/output-spec.md`.

## Extension Points

| Want to… | Touch |
|---|---|
| Add a site | New file in `core/engines/` + `@register` + `SITE_TYPE_MAP` (see `CONTRIBUTING.md`) |
| Add a content type | `core/domain` mapping + download routing in `core/download` |
| Add a filter rule | `core/filter` |
| Add an entry command | New file in `app/` calling `core.*` |
| Change output format | `core/download/preserver.py` + `docs/output-spec.md` |

## Tests

| Suite | Purpose |
|---|---|
| `tests/post_refactor_smoke.py` | Structure smoke: all files compile, imports resolve, engines instantiate, zero broken links |
| `tests/exhaustive_guide_test.py` | Interactive-guide exhaustive (200+ variants) |
| `tests/fresh_exhaustive.py` | Full exhaustive suite (T01–T19, 102 assertions) |
| `tests/task_audit.py` | Task-by-task audit (67 items) |

Run all of them before opening a PR.
