# Output Spec · web-knowledge-crawler

> Output root is fixed as **`知识库/`** (Chinese for "knowledge base"). Behavior follows `core/download/preserver.py` (the persist implementation).

---

## 1. Output Root

| Entry | Default root | Override |
|---|---|---|
| Mass crawl | `知识库/{term}/` | `crawl_all --out-dir <path>` |
| Single crawl | `知识库/指定爬取/` | pick a custom path in the guide |
| Whole-site crawl | `知识库/{site}/` | — |

## 2. Directory Structure (3-level spec)

```
知识库/
└── {term or "指定爬取"}/
    └── {type}/                  # video / page / paper / code / dataset / doc / course / Q&A / audio...
        └── {site}/
            └── 00_20260812_title_2.1M/   # ★ sequence_date_title_size
                ├── raw_file.mp4/.pdf/.html
                ├── title_正文.txt        # for HTML sites: denoised text (trafilatura) — double-save
                └── meta.json             # metadata
```

## 3. Naming Rules (`preserver.py`)

- **Item folder**: `{seq:02d}_{dateYYYYMMDD}_{short_title}_{size}` (e.g. `00_20260812_Attention_is_all_you_need_2.1M`)
  - sequence: auto-increment within the directory (`00`, `01`, `02`...); resumes without duplicating
  - title: first 30 chars, illegal chars `\/:*?"<>|` → `_`, empty → `untitled`
  - size: ≥1MB `X.XM`, ≥1KB `X.XK`, else `X.B`
- **Filename cleaning**: `_safe_filename`, max 120 chars, illegal chars replaced
- **Term / site names**: spaces → `_`, cleaned, max 60/40 chars

## 4. meta.json Fields

Written once per saved item:

| Field | Meaning |
|---|---|
| url | Original source URL |
| title | Title |
| original_term | The term that triggered the crawl |
| file_type | Type (pdf/video/html/repo...) |
| size | Bytes |
| saved_path | Saved path |
| site | Site name |
| timestamp | Crawl time |

(Exact fields per `preserver.save_metadata`; slight variation by type)

## 5. Type Routing (download strategy)

```
repo→git clone | video→yt-dlp(mp4) | pdf→direct | archive→zip
html→Crawl4AI/Scrapling render (markdown/text) | audio→RSS+yt-dlp
json/md→real file | page→raw .html + denoised .txt double-save
```

## 6. Related Code

- `core/download/preserver.py`: persist (naming / meta / double-save)
- `core/download/deduper.py`: SQLite dedup (URL×term unique key)
- `core/download/downloader.py`: download strategy routing
