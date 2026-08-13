"""代码平台站内搜索 — Gitee/GitLab/LeetCode。"""
from urllib.parse import quote
from .playwright_search import PlaywrightSearcher
from .base import register


@register
class GiteeSearcher(PlaywrightSearcher):
    name = "gitee"
    domain = "gitee.com"
    search_url_template = "https://search.gitee.com/?type=code&q={term}"
    item_selector = ".repo-search-item"
    title_selector = ".name a"
    url_selector = ".name a"
    summary_selector = ".desc"
    wait_timeout = 15000


@register
class GitLabSearcher(PlaywrightSearcher):
    """GitLab 代码搜索 — Playwright模拟。"""
    name = "gitlab"
    domain = "about.gitlab.com"
    search_url_template = "https://about.gitlab.com/search/?q={term}"
    item_selector = ".search-result"
    title_selector = ".result-title a"
    url_selector = ".result-title a"
    summary_selector = ".result-excerpt"
    wait_timeout = 10000


@register
class LeetCodeSearcher(PlaywrightSearcher):
    """LeetCode 题库搜索 — Playwright模拟。"""
    name = "leetcode"
    domain = "leetcode.cn"
    search_url_template = "https://leetcode.cn/search/?q={term}"
    item_selector = ".table-list问题"
    title_selector = ".question-title a"
    url_selector = ".question-title a"
    summary_selector = ".description, .stats"
    wait_timeout = 10000
