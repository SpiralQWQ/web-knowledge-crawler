"""知乎/掘金/CSDN/V2EX/Lobsters 等社区站内搜索 — Playwright模拟。"""
from urllib.parse import quote
from .playwright_search import PlaywrightSearcher
from .base import register


@register
class ZhihuSearcher(PlaywrightSearcher):
    name = "zhihu"
    domain = "zhihu.com"
    search_url_template = "https://www.zhihu.com/search?type=content&q={term}"
    item_selector = ".SearchResult-content, .result-item"
    title_selector = ".title a, h4 a"
    url_selector = ".title a, h4 a"
    summary_selector = ".summary, .desc"
    wait_timeout = 15000


@register
class JuejinSearcher(PlaywrightSearcher):
    """掘金搜索 — Playwright模拟。"""
    name = "juejin"
    domain = "juejin.cn"
    search_url_template = "https://search.juejin.cn/query?keyword={term}&type=4"
    item_selector = ".result-item, .search-result"
    title_selector = ".result-title a"
    url_selector = ".result-title a"
    summary_selector = ".result-summary"
    wait_timeout = 15000


@register
class CSDNSearcher(PlaywrightSearcher):
    """CSDN 搜索 — Playwright模拟。"""
    name = "csdn"
    domain = "csdn.net"
    search_url_template = "https://so.csdn.net/search?q={term}"
    item_selector = ".list_item, .article-item"
    title_selector = ".title a"
    url_selector = ".title a"
    summary_selector = ".desc"
    wait_timeout = 15000


@register
class SegfaultSearcher(PlaywrightSearcher):
    """思否 SegmentFault 搜索 — Playwright模拟。"""
    name = "segmentfault"
    domain = "segmentfault.com"
    search_url_template = "https://segmentfault.com/search?q={term}"
    item_selector = ".search-result__item"
    title_selector = ".search-result__title a"
    url_selector = ".search-result__title a"
    summary_selector = ".search-result__description"
    wait_timeout = 10000


@register
class V2EXSearcher(PlaywrightSearcher):
    """V2EX 搜索 — Playwright模拟。"""
    name = "v2ex"
    domain = "v2ex.com"
    search_url_template = "https://www.v2ex.com/search?q={term}"
    item_selector = "#Main .cell.item"
    title_selector = "a[href^=/t/]"
    url_selector = "a[href^=/t/]"
    summary_selector = ".body"
    wait_timeout = 10000


@register
class OschinaSearcher(PlaywrightSearcher):
    """开源中国 Oschina 搜索 — Playwright模拟。"""
    name = "oschina"
    domain = "oschina.net"
    search_url_template = "https://my.oschina.net/search?q={term}"
    item_selector = ".search-list li"
    title_selector = "h3 a"
    url_selector = "h3 a"
    summary_selector = ".text"
    wait_timeout = 10000


@register
class DevToSearcher(PlaywrightSearcher):
    """Dev.to 搜索 — Playwright模拟。"""
    name = "devto"
    domain = "dev.to"
    search_url_template = "https://dev.to/search?q={term}"
    item_selector = ".search-item"
    title_selector = "h3 a"
    url_selector = "h3 a"
    summary_selector = ".snippet"
    wait_timeout = 10000


@register
class MediumSearcher(PlaywrightSearcher):
    """Medium 搜索 — Playwright模拟。"""
    name = "medium"
    domain = "medium.com"
    search_url_template = "https://medium.com/search/{term}?published=1"
    item_selector = ".pfKkef"
    title_selector = "h4"
    url_selector = "a"
    summary_selector = ".eofuGJ"
    wait_timeout = 10000


@register
class HackernoonSearcher(PlaywrightSearcher):
    """HackerNoon 搜索 — Playwright模拟。"""
    name = "hackernoon"
    domain = "hackernoon.com"
    search_url_template = "https://hackernoon.com/search?q={term}"
    item_selector = ".search-results article"
    title_selector = "h3 a"
    url_selector = "h3 a"
    summary_selector = ".excerpt"
    wait_timeout = 10000


@register
class LobstersSearcher(PlaywrightSearcher):
    """Lobsters 搜索 — Playwright模拟。"""
    name = "lobste.rs"
    domain = "lobste.rs"
    search_url_template = "https://lobste.rs/search?q={term}&what=submissions"
    item_selector = ".submission"
    title_selector = "a.submission-link"
    url_selector = "a.submission-link"
    summary_selector = ".domain, .summary"
    wait_timeout = 10000


@register
class DatawhaleSearcher(PlaywrightSearcher):
    """Datawhale 社区搜索 — Playwright模拟。"""
    name = "datawhale"
    domain = "datawhale.cn"
    search_url_template = "https://datawhale.cn/search?q={term}"
    item_selector = ".search-item, .result-item"
    title_selector = "h3 a"
    url_selector = "h3 a"
    summary_selector = ".summary, p"
    wait_timeout = 10000


@register
class AlignmentForumSearcher(PlaywrightSearcher):
    """AI Alignment Forum 搜索 — Playwright模拟。"""
    name = "alignmentforum"
    domain = "alignmentforum.org"
    search_url_template = "https://www.alignmentforum.org/search?q={term}"
    item_selector = ".search-item, .result"
    title_selector = "a"
    url_selector = "a"
    summary_selector = ".excerpt, p"
    wait_timeout = 10000
