"""Google Scholar / Connected Papers / Scirate 学术论文搜索。"""
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


@register
class ConnectedPapersSearcher(PlaywrightSearcher):
    """Connected Papers 论文图谱 — Playwright模拟。"""
    name = "connectedpapers"
    domain = "connectedpapers.com"
    search_url_template = "https://www.connectedpapers.com/search/{term}"
    item_selector = ".paper-card"
    title_selector = ".paper-title h3, .paper-title a"
    url_selector = 'a[href*="/graph/"]'
    summary_selector = ".paper-meta"
    wait_timeout = 15000


@register
class ScirateSearcher(PlaywrightSearcher):
    """Scirate arXiv评论 — Playwright模拟。"""
    name = "scirate"
    domain = "scirate.com"
    search_url_template = "https://scirate.com/search?q={term}"
    item_selector = ".search-result, .result-item"
    title_selector = "h4 a, .title a"
    url_selector = ".title a"
    summary_selector = ".comments, .excerpt"
    wait_timeout = 10000
