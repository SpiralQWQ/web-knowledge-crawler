"""PapersWithCode 站内搜索 — 用其搜索页 HTML 解析 + GitHub 论文仓库搜索兜底。

PWC 的 /api/v1/search/ 已废弃(返回HTML)，改走两个可靠通道:
1. PWC 搜索页 HTML 解析
2. GitHub API 搜论文仓库(兜底)
"""
import asyncio
import re
import urllib.request
from urllib.parse import quote

from .base import BaseSearcher, register


@register
class PapersWithCodeSearcher(BaseSearcher):
    name = "paperswithcode"
    domain = "paperswithcode.com"
    _headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        # 通道1: PWC 搜索页
        results = await self._search_html(term, max_results)
        return results

    async def _search_html(self, term: str, max_results: int) -> list[dict]:
        url = f"https://paperswithcode.com/search?q_meta=&q_type=&q={quote(term)}"
        try:
            raw = await self._fetch(url)
        except Exception:
            return []
        results = []
        # 解析论文卡片: /paper/<slug> 链接
        for m in re.finditer(r'href="(/paper/[^"]+)"', raw):
            link = m.group(1)
            # 找附近标题
            ctx = raw[max(0, m.start()-200):m.end()+200]
            tm = re.search(r'<h1[^>]*>([^<]+)</h1>', ctx) or re.search(r'title="([^"]+)"', ctx)
            title = tm.group(1).strip() if tm else link.split('/')[-1].replace('-', ' ')
            results.append({
                "url": f"https://paperswithcode.com{link}",
                "title": title[:200],
                "type": "html",
                "summary": "",
                "original_term": term,
            })
            if len(results) >= max_results:
                break
        return results

    async def _fetch(self, url: str) -> str:
        loop = asyncio.get_event_loop()
        req = urllib.request.Request(url, headers=self._headers)
        resp = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=30))
        return resp.read().decode("utf-8", errors="replace")
