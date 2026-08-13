# Contributing to web-knowledge-crawler

Thanks for your interest in contributing! Whether it's a bug report, a new searcher, a docs improvement, or a feature — every contribution is welcome.

## Development Setup

```bash
git clone https://github.com/SpiralQWQ/web-knowledge-crawler
cd web-knowledge-crawler
pip install -r requirements.txt
python setup.py    # optional: one-command config wizard
```

## Code Style

- **Python 3.10+**, follows the existing code style (read the surrounding code first)
- Keep functions small and focused; no business logic in `core/`
- Docstrings for new public functions (Chinese or English, matching the file)
- No hard-coded paths / keys — read from `config/` or env variables
- Follow `docs/目录契约.md` for where new code goes

## Before Submitting a PR

1. **Run the test suite** — must be green:
   ```bash
   python tests/post_refactor_smoke.py    # structure smoke
   python tests/exhaustive_guide_test.py  # interactive exhaustive
   python tests/task_audit.py             # task audit
   python tests/fresh_exhaustive.py       # full exhaustive
   ```
2. **No regressions** — if you touch `core/` code, confirm existing features still work
3. **Update docs** — if you change behavior, update README / CHANGELOG accordingly

## How to Contribute

### Report a bug
- Open an [Issue](https://github.com/SpiralQWQ/web-knowledge-crawler/issues) with:
  - Steps to reproduce
  - Expected vs actual behavior
  - Python version / OS / tool versions
  - Any relevant log output

### Add a new searcher
1. Create `core/engines/your_site.py` following an existing searcher's pattern
2. Register it via the `@register` decorator
3. Add the site to `core/domain/__init__.py` `SITE_TYPE_MAP`
4. Test with a real query; add it to a smoke check

### Submit a PR
1. Fork the repo, create a feature branch: `git checkout -b feat/your-feature`
2. Make your changes, run the tests above
3. Commit with a clear message (e.g. `feat(engines): add X site searcher`)
4. Open a PR describing what & why, plus test results

## Licensing

By contributing, you agree that your contributions will be licensed under the [AGPL-3.0](LICENSE).
