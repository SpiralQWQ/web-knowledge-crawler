# Changelog

All notable changes to this project. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versioning follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [2.5.3] - 2026-08-13

### Added

- Full open-source documentation overhaul (W01-W12): bilingual README (badges / FAQs / examples), Keep-a-Changelog CHANGELOG, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, docs/ARCHITECTURE, docs/GUIDE, GitHub issue & PR templates

## [2.5.2] - 2026-08-12

### Added

- `setup.py` one-command config wizard: answer a few questions → installs dependencies + generates `.env`

### Changed

- Released under AGPL-3.0 with bilingual (EN + 中文) docs and donation badges
- Privacy scrubbed: no `.env` / `data/` / `知识库/`; config paths are placeholder-only

## [2.5.1] - 2026-08-12

### Added

- `docs/输出规范.md` — crawl output format standard (directory structure / naming / meta.json / HTML double-save)

### Changed

- `知识库/` finalized as the output directory name (the planned `output/` was dropped)
- README / CHANGELOG / docs aligned to the app/core structure, bilingual (EN + 中文)

## [2.5.0] - 2026-08-12

### Added

- `tests/fresh_exhaustive.py` — full exhaustive suite (T01-T19, 102 assertions) with prompt-completeness checks, written from scratch (no reuse)

## [2.4.1] - 2026-08-12

### Added

- `tests/post_refactor_smoke.py` — post-refactor structure smoke tests (146 files compile / entries+modules import / 51 searchers instantiate / zero broken imports)

## [2.4.0] - 2026-08-12

### Changed

- Architecture refactored to `app/` + `core/` (directory contract): `crawl_guide.py` split into `core/{domain,interaction,auth,download}`; helpers → `core/bridges`; `shared` → `core/{download,auth,filter,domain}`; `search_engine` → `core/engines`; `tools` → `app`

## [2.3.1] - 2026-08-12

### Fixed

- 26 defects from real-world testing: Douyin chain-crawl via browser collection, login-state anti-mismatch (key-cookie column matching), YouTube proxy, anti-foolproofing (EOF/Ctrl+C), plain-language plan + readiness check, per-item download logs, mass-crawl `--out-dir`

## [2.3.0] - 2026-08-11

### Added

- Smart crawl guide (`crawl_guide.py`): point-and-ask interactive guide — vocabulary cleaning, term personality, 37-site mapping, auto-login, download progress, chain crawl

## [2.2.0] - 2026-08-10

### Changed

- Patch refactor (based on 100-repo research): Sitemap keyword search (rank_bm25), text denoise (trafilatura), auto keywords (yake), pipeline filter, semantic expansion (text2vec) — relevance 76% → 80%

## [2.0.0] - 2026-08-10

### Added

- CDP real-browser anti-block (debug browser port 9222) — rescued 10 sites (Douyin/Weibo/Bilibili/LeetCode/Gitee/Khan/InfoQ/36Kr/SSPai/TMTPost), 27 → 34 real-content sites

## [1.5.0] - 2026-08-09

### Added

- JS dynamic-site layer (Scrapling bridge), downloader fallback chain, login-site adapters

## [1.0.0] - 2026-08-07

### Added

- Initial release: three-category collection system, 50 site searchers, cookie export, SQLite dedup, organized persistence
