"""YouTube/抖音/小红书 视频站内搜索 — Playwright模拟。"""
from urllib.parse import quote
from .playwright_search import PlaywrightSearcher
from .base import register


@register
class YouTubeSearcher(PlaywrightSearcher):
    name = "youtube"
    domain = "youtube.com"
    search_url_template = "https://www.youtube.com/results?search_query={term}"
    item_selector = ".yt-lockup:not(.show-more)"
    title_selector = ".yt-lockup-title a"
    url_selector = ".yt-lockup-title a"
    summary_selector = ".yt-lockup-description"
    wait_timeout = 20000
    result_type = "video"


@register
class DouyinSearcher(PlaywrightSearcher):
    """抖音网页版站内搜索 — Playwright模拟。"""
    name = "douyin"
    domain = "douyin.com"
    search_url_template = "https://www.douyin.com/search/{term}?type=video"
    item_selector = ".douyin-search-room"
    title_selector = ".search-video-title"
    url_selector = 'a[href*="/video/"]'
    summary_selector = ".search-video-desc"
    wait_timeout = 15000
    result_type = "video"


@register
class XhsSearcher(PlaywrightSearcher):
    """小红书站内搜索 — Playwright模拟。"""
    name = "xiaohongshu"
    domain = "xiaohongshu.com"
    search_url_template = "https://www.xiaohongshu.com/search_result?keyword={term}"
    item_selector = ".note-item"
    title_selector = ".title h4"
    url_selector = 'a[href*="/explore/"], a[href*="/discovery/item/"]'
    summary_selector = ".desc, .abstract"
    wait_timeout = 15000
    result_type = "video"
