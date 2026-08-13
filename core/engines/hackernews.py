"""Hacker News 站内搜索 — HN 有公开 Search API。无需登录。"""
import asyncio
from urllib.request import urlopen
from urllib.parse import quote
from .base import BaseSearcher, register


@register
class HackerNewsSearcher(BaseSearcher):
    name = "hackernews"
    domain = "news.ycombinator.com"

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        """使用 HN Algolia Search API (公开免费)。"""
        url = f"https://hn.algolia.com/api/v1/search?tags=story&query={quote(term)}&hitsPerPage={max_results}"
        try:
            data = await self._fetch(url)
            return self._parse(data, term)
        except Exception:
            # 回退到 HN 官方 URL-based search
            return await self._search_legacy(term, max_results)

    async def _fetch(self, url: str) -> dict:
        loop = asyncio.get_event_loop()
        req = urlopen(url, timeout=30)
        import json
        return json.loads(req.read().decode("utf-8"))

    def _parse(self, data: dict, original_term: str, limit: int = 50) -> list[dict]:
        hits = data.get("hits", []) or []
        results = []
        for h in hits[:limit]:
            title = h.get("title", "")
            url_ = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID', '')}"
            abstract = ""
            if h.get("objectID"):
                abstract = f"Story #{h['objectID']} · {h.get('num_comments', 0)} comments"
            ft = "html"
            if url_.endswith((".pdf", ".doc", ".ppt")):
                ft = url_.split(".")[-1]
            results.append({
                "url": url_,
                "title": title,
                "type": ft,
                "summary": abstract,
                "original_term": original_term,
            })
        return results

    async def _search_legacy(self, term: str, max_results: int) -> list[dict]:
        """回退: 用 HN 页面搜索 URL (无 API key 时)。"""
        url = f"https://news.ycombinator.com/search?show=all&q={quote(term)}"
        try:
            data = await self._fetch(url)
            import re
            links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>', data)
            return [{
                "url": u,
                "title": t.strip(),
                "type": "html",
                "summary": "",
                "original_term": term,
            } for u, t in links[:max_results]]
        except Exception:
            return []
