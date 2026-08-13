"""知乎站内搜索 — Playwright 模拟(知乎无公开API)。"""
from .playwright_search import PlaywrightSearcher
from .base import register


@register
class ZhihuSearcher(PlaywrightSearcher):
    name = "zhihu"
    domain = "zhihu.com"
    search_url_template = "https://www.zhihu.com/search?type=content&q={term}"
    item_selector = ".SearchResult-content .RichContent, .SearchResult-content"
    title_selector = ".SearchResult-title a, .RichContent-inner a"
    url_selector = "a"
    summary_selector = ".RichContent-inner"
