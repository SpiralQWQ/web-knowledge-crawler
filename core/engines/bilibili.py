"""Bilibili 站内搜索 — B站搜索 API（挂 cookie 更完整）。"""
import asyncio
import json
import urllib.request
from urllib.parse import quote

from .base import BaseSearcher, register
from core.auth.cookie_util import add_cookie


@register
class BilibiliSearcher(BaseSearcher):
    name = "bilibili"
    domain = "bilibili.com"

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        """B站搜索 API，带 cookie 返回完整结果。"""
        url = (f"https://api.bilibili.com/x/web-interface/search/type"
               f"?search_type=videokeyword&keyword={quote(term)}&page=1&pagesize={max_results}")
        try:
            raw = await self._fetch(url)
            return self._parse(raw, term)
        except Exception:
            return []

    async def _fetch(self, url: str) -> dict:
        loop = asyncio.get_event_loop()
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        add_cookie(req, "bilibili.com")
        resp = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=30))
        return json.loads(resp.read().decode("utf-8"))

    def _parse(self, data: dict, original_term: str, limit: int = 50) -> list[dict]:
        results = []
        result_data = data.get("data", {}) or {}
        videos = (result_data.get("result") or [])[:limit]
        for v in videos:
            bvid = v.get("bvid", "")
            if not bvid:
                continue
            title = (v.get("title") or "").strip()
            url_ = f"https://www.bilibili.com/video/{bvid}"
            abstract = (v.get("description") or v.get("desc") or "").strip()[:500]
            results.append({
                "url": url_,
                "title": title,
                "type": "video",
                "summary": abstract,
                "original_term": original_term,
            })
        return results
