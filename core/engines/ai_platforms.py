"""ModelScope 社区站内搜索 — Playwright模拟。

说明：HuggingFace / Kaggle 的完整实现见 huggingface.py / kaggle.py，
本文件只保留 ModelScope（避免同名类覆盖冲突）。
"""
from .playwright_search import PlaywrightSearcher
from .base import register


@register
class ModelscopeSearcher(PlaywrightSearcher):
    """魔搭 ModelScope 社区搜索 — Playwright模拟。"""
    name = "modelscope"
    domain = "modelscope.cn"
    search_url_template = "https://modelscope.cn/search?query={term}"
    item_selector = ".result-item"
    title_selector = ".title a"
    url_selector = ".title a"
    summary_selector = ".desc"
    wait_timeout = 10000
