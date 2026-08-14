# Directory Contract · web-knowledge-crawler

> Role: the single standard for how files are organized in this project. Any new code should follow it.
> Model: Paradigm C variant (layered + domain mix), a Python crawler project.

---

## 1. Target Structure

```
web-knowledge-crawler/
├── app/                  # ★ Entry layer: command entry points
│   ├── crawl_guide.py    #   Smart crawl guide
│   ├── crawl_all.py      #   Mass crawl
│   ├── crawl_sites.py    #   Whole-site crawl
│   └── export_all_cookies.py / export_cookies.py
├── core/                 # ★ Engine layer
│   ├── engines/          #   Site searchers
│   ├── bridges/          #   Renderer/browser subprocess bridges
│   ├── download/         #   Download / persist / dedupe / scheduler
│   ├── auth/             #   Cookie / login
│   ├── filter/           #   Relevance / noise filtering
│   ├── interaction/      #   Interactive prompts & preferences
│   └── domain/           #   Vocabulary / personality / site mapping / login rules
├── config/               # Static config (collector.yaml / seeds/)
├── data/                 # Runtime data (cookies / db / acl data)
├── 知识库/               # Crawl output (knowledge base)
├── tests/                # Tests (exhaustive / task-audit / smoke)
├── docs/                 # Docs (this contract / output spec)
└── root: README.md / CHANGELOG.md / LICENSE / requirements.txt
```

## 2. Responsibility Boundaries (high cohesion · low coupling)

| Directory | Only | Never |
|---|---|---|
| app/ | entry orchestration, arg parsing, calls core | business logic |
| core/engines/ | site searchers | download / persist |
| core/bridges/ | subprocess bridges (renderer/browser wrappers) | business logic |
| core/download/ | download / persist / dedupe / scheduler | searchers |
| core/auth/ | cookie reading / login | download |
| core/filter/ | relevance / noise filtering | download |
| core/interaction/ | interactive prompts (ask user) | download implementation |
| core/domain/ | pure vocabulary/personality/mapping logic | network / IO |
| config/ | static config | runtime-generated state |
| data/ | runtime data | code |
| 知识库/ | crawl output | code |
| tests/ | test scripts | temp files |

## 3. One-Way Dependency Rules

```
app → core.{engines,bridges,download,auth,filter,interaction,domain}
                    ↑
       (inside core: interaction/domain → download → bridges/engines)
```

- **No reverse dependency**: core must not import app; app/core must not depend on runtime dirs (data/)
- **Inside core**: logic layers (interaction/domain) may call execution layers (download/auth/engines/bridges); execution layers must not call interaction
- Cross-directory calls go through public entry points (`__init__.py` or explicit functions) — never private internals

## 4. Hard Rules

- ❌ No suffix-named directories (`*.py`, flat `helpers/` scattering)
- ❌ No business logic scattered into `utils/` (pure functions live in the matching `core/` module)
- ❌ No nesting deeper than 3 levels
- ❌ No tests / config / deployment files inside `core/`
- ❌ No real `.env` committed (only `.env.example`)
- ❌ No cross-directory import of internals (use public API)
- ❌ No runtime state (prefs/cache) mixed into `config/`

## 5. Adding New Code

- New searcher → `core/engines/`
- New download type → `core/download/`
- New interaction → `core/interaction/`
- New pure utility → the matching module inside `core/` (no top-level `shared/`)
- **Never change the existing structure — add within the matching domain.**
