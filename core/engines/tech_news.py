"""36氪/虎嗅/钛媒体/机器之心/量子位 科技资讯站内搜索 — Playwright模拟。"""
from urllib.parse import quote
from .playwright_search import PlaywrightSearcher
from .base import register


@register
class _36krSearcher(PlaywrightSearcher):
    """36氪搜索 — Playwright模拟。"""
    name = "36kr"
    domain = "36kr.com"
    search_url_template = "https://so.36kr.com/agogo/search?q={term}"
    item_selector = ".result-item"
    title_selector = ".title a"
    url_selector = ".title a"
    summary_selector = ".summary, p"
    wait_timeout = 10000


@register
class HuxiuSearcher(PlaywrightSearcher):
    """虎嗅搜索 — Playwright模拟。"""
    name = "huxiu"
    domain = "huxiu.com"
    search_url_template = "https://www.huxiu.com/search?q={term}"
    item_selector = ".article-card"
    title_selector = ".title a"
    url_selector = ".title a"
    summary_selector = ".abstract"
    wait_timeout = 10000


@register
class TmtpostSearcher(PlaywrightSearcher):
    """钛媒体搜索 — Playwright模拟。"""
    name = "tmtpost"
    domain = "tmtpost.com"
    search_url_template = "https://search.tmtpost.com/search?q={term}"
    item_selector = ".article-item"
    title_selector = ".title a"
    url_selector = ".title a"
    summary_selector = ".excerpt"
    wait_timeout = 10000


@register
class JiqizhixinSearcher(PlaywrightSearcher):
    """机器之心搜索 — Playwright模拟。"""
    name = "jiqizhixin"
    domain = "jiqizhixin.com"
    search_url_template = "https://www.jiqizhixin.com/search?q={term}"
    item_selector = ".article-card"
    title_selector = ".title a"
    url_selector = ".title a"
    summary_selector = ".excerpt"
    wait_timeout = 10000


@register
class QbitaiSearcher(PlaywrightSearcher):
    """量子位搜索 — Playwright模拟。"""
    name = "qbitai"
    domain = "qbitai.com"
    search_url_template = "https://www.qbitai.com/search/?q={term}"
    item_selector = ".post-item"
    title_selector = "h3 a"
    url_selector = "h3 a"
    summary_selector = ".excerpt"
    wait_timeout = 10000


@register
class InfoqSearcher(PlaywrightSearcher):
    """InfoQ中文搜索 — Playwright模拟。"""
    name = "infoq"
    domain = "infoq.cn"
    search_url_template = "https://www.infoq.cn/search?q={term}"
    item_selector = ".article-item"
    title_selector = ".title a"
    url_selector = ".title a"
    summary_selector = ".abstract"
    wait_timeout = 10000


@register
class SspaiSearcher(PlaywrightSearcher):
    """少数派搜索 — Playwright模拟。"""
    name = "sspai"
    domain = "sspai.com"
    search_url_template = "https://sspai.com/search?q={term}"
    item_selector = ".article-item"
    title_selector = ".title a"
    url_selector = ".title a"
    summary_selector = ".abstract"
    wait_timeout = 10000
