"""Category 1: 站内搜索适配器 — 统一接口让不同站按关键词搜索。

每个站点一个模块，实现 BaseSearcher 定义的 search(term, max_results) 接口。
API 优先（arXiv/B站/Kaggle/HF），Playwright 模拟降级（知乎/掘金等）。
"""
from abc import ABC, abstractmethod

class BaseSearcher(ABC):
    """站内搜索适配器基类。"""

    @property
    @abstractmethod
    def name(self) -> str:
        """站点名称（用于日志和目录名）。"""
        ...

    @property
    @abstractmethod
    def domain(self) -> str:
        """域名。"""
        ...

    @abstractmethod
    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        """
        站内搜索关键词。

        Args:
            term: 搜索词（已在预处理中加了限定词）
            max_results: 最多返回结果数

        Returns:
            [{"url": "...", "title": "...", "type": "pdf|html|video|...",
              "summary": "..."}, ...]
        """
        ...

    async def close(self):
        """清理资源（如 Playwright context）。子类可重写。"""
        pass


# --- Registry: site_name -> BaseSearcher ---
_searchers: dict[str, type[BaseSearcher]] = {}


def register(cls):
    _searchers[cls.name] = cls
    return cls


def get_searcher(name: str) -> BaseSearcher | None:
    cls = _searchers.get(name)
    return cls() if cls else None


def list_searchers() -> list[str]:
    return sorted(_searchers.keys())
