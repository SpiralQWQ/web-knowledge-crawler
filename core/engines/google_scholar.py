"""Google Scholar 站内搜索 — Playwright模拟(无公开API)。"""
from urllib.parse import quote
from .playwright_search import PlaywrightSearcher
from .base import register


@register
class GoogleScholarSearcher(PlaywrightSearcher):
    name = "google_scholar"
    domain = "scholar.google.com"
    search_url_template = "https://scholar.google.com/scholar?q={term}"
    item_selector = ".gs_ri"
    title_selector = ".gs_rt a"
    url_selector = ".gs_rt a"
    summary_selector = ".gs_rs"
    wait_timeout = 20000
