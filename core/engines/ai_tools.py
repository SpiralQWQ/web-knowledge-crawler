"""AI 产品站内搜索 — Cursor/Claude Code/Codex/OpenCode。"""
from urllib.parse import quote
from .playwright_search import PlaywrightSearcher
from .base import register


@register
class CursorSearcher(PlaywrightSearcher):
    """Cursor AI编辑器站内搜索 — Playwright模拟。"""
    name = "cursor"
    domain = "cursor.com"
    search_url_template = "https://www.cursor.com/search?q={term}"
    item_selector = ".search-result-item"
    title_selector = ".title a"
    url_selector = ".title a"
    summary_selector = ".description"
    wait_timeout = 10000


@register
class ClaudeCodeSearcher(PlaywrightSearcher):
    """Claude Code 官方文档站内搜索 — Playwright模拟。"""
    name = "claude_code_docs"
    domain = "code.claude.com"
    search_url_template = "https://code.claude.com/docs/search?q={term}"
    item_selector = ".search-result"
    title_selector = ".result-title a"
    url_selector = ".result-title a"
    summary_selector = ".result-excerpt"
    wait_timeout = 10000


@register
class OpenCodeSearcher(PlaywrightSearcher):
    """OpenCode CLI 文档搜索 — Playwright模拟。"""
    name = "opencode"
    domain = "opencode.ai"
    search_url_template = "https://opencode.ai/search?q={term}"
    item_selector = ".search-item"
    title_selector = "h3 a"
    url_selector = "a"
    summary_selector = ".excerpt"
    wait_timeout = 10000


@register
class QoderSearcher(PlaywrightSearcher):
    """Qoder通义灵码 文档搜索 — Playwright模拟。"""
    name = "qoder_docs"
    domain = "docs.qoder.cn"
    search_url_template = "https://docs.qoder.cn/search?q={term}"
    item_selector = ".doc-search-item"
    title_selector = ".title a"
    url_selector = ".title a"
    summary_selector = ".summary"
    wait_timeout = 10000
