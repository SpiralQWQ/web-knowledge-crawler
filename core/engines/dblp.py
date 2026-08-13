"""DBLP 站内搜索 — DBLP Search API (无需登录)。

实际通过 dblp JSON API: https://dblp.org/search/publ/api?format=json&q=<query>&h=50
"""
import asyncio
import json
import ssl
import time
from urllib.request import urlopen
from urllib.parse import quote

from .base import BaseSearcher, register

# DBLP 的 SSL 证书链不完整，禁用校验（仅对 dblp 域，安全可接受）
_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE


@register
class DBLPSearcher(BaseSearcher):
    name = "dblp"
    domain = "dblp.org"

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        url = f"https://dblp.org/search/publ/api?q={quote(term)}&format=json&h={max_results}"
        # DBLP 服务偶发 500/超时，重试 3 次（带退避）
        for attempt in range(3):
            try:
                data = await self._fetch(url)
                return self._parse(data, term)
            except Exception:
                if attempt < 2:
                    await asyncio.sleep(1.5 * (attempt + 1))
                else:
                    return []

    async def _fetch(self, url: str) -> dict:
        loop = asyncio.get_event_loop()
        req = urlopen(url, timeout=30, context=_CTX)
        return json.loads(req.read().decode("utf-8"))

    def _parse(self, data: dict, original_term: str, limit: int = 50) -> list[dict]:
        hits = data.get("result", {}).get("hits", {}).get("hit", [])
        results = []
        for hit in hits[:limit]:
            info = hit.get("info", {}) or {}
            title = info.get("title", "") or ""
            url_ = info.get("url", "") or ""
            ft = "pdf" if (url_.endswith(".pdf") or ".pdf" in url_) else "html"
            results.append({
                "url": url_,
                "title": title,
                "type": ft,
                "summary": "",
                "original_term": original_term,
            })
        return results
