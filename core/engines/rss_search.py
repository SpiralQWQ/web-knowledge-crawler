"""RSS 搜索器 — medium / oschina 用 RSS 通道（零反爬）。

medium：`medium.com/feed/tag/{词}` 已按标签过滤
oschina：`oschina.net/news/rss` 通用资讯，需按词过滤标题
"""
import asyncio
import xml.etree.ElementTree as ET

from .base import BaseSearcher, register


class RssSearcher(BaseSearcher):
    """抓 RSS 的搜索器基类。子类定义 rss_url_template。"""

    rss_url_template = ""
    domain = ""
    _filter_term = True  # 是否按词过滤（medium 标签流可关）

    @property
    def name(self) -> str:
        return self.__class__.__dict__.get("name", "")

    @property
    def domain_(self) -> str:
        return self.domain

    async def _fetch(self, url: str) -> str:
        def _get():
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": "KnowledgeCollector/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(None, _get)
        except Exception:  # noqa: BLE001
            return ""

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        from urllib.parse import quote
        url = self.rss_url_template.replace("{term}", quote(term))
        body = await self._fetch(url)
        if not body:
            return []
        results = []
        try:
            root = ET.fromstring(body)
        except Exception:  # noqa: BLE001
            return []
        term_l = term.lower()
        for item in root.iter("item"):
            title = ""
            link = ""
            for child in item:
                if child.tag.endswith("title"):
                    title = (child.text or "").strip()
                elif child.tag.endswith("link"):
                    link = (child.text or "").strip()
            if not link:
                continue
            if self._filter_term and term_l and term_l not in title.lower():
                continue
            results.append({
                "url": link,
                "title": title[:200],
                "type": "html",
                "summary": "",
                "original_term": term,
            })
            if len(results) >= max_results:
                break
        return results


@register
class MediumRssSearcher(RssSearcher):
    name = "medium"
    rss_url_template = "https://medium.com/feed/tag/{term}"
    domain = "medium.com"
    _filter_term = False  # medium 标签流已按标签过滤


@register
class OschinaRssSearcher(RssSearcher):
    name = "oschina"
    rss_url_template = "https://www.oschina.net/news/rss"
    domain = "oschina.net"
    _filter_term = True  # 通用资讯，需按词过滤
