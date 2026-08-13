"""OpenAlex 学术搜索 — 替代 Google Scholar。

Google Scholar 反爬极强（scholarly 库实测被封 "Cannot Fetch"），
改用 OpenAlex 免费学术 API（全球论文数据库，无反爬、免登录）。
实测：search 返回真实论文 + DOI。
用法：注册为 google_scholar 名，覆盖原 Playwright 版。
"""
import asyncio
import json
import os

from .base import BaseSearcher, register


@register
class OpenAlexSearcher(BaseSearcher):
    name = "google_scholar"
    domain = "openalex.org"
    base_url = "https://api.openalex.org/works"

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        n = min(max_results, 25)
        url = f"{self.base_url}?search={term.replace(' ', '+')}&per-page={n}"
        # OpenAlex 建议带 mailto（公平使用池），可配 .env OPENALEX_MAILTO，无则空
        mailto = os.environ.get("OPENALEX_MAILTO", "").strip()
        if mailto:
            url += f"&mailto={mailto}"
        data = await self._fetch(url)
        results = []
        for w in (data or {}).get("results", []):
            title = w.get("title", "") or ""
            doi = w.get("doi", "") or ""
            oid = w.get("id", "") or ""
            # URL：OpenAlex 的 doi 字段已含 https://doi.org/，直接用；否则拼 OpenAlex 页
            if doi.startswith("http"):
                page_url = doi
            elif doi:
                page_url = f"https://doi.org/{doi}"
            else:
                page_url = oid
            results.append({
                "url": page_url,
                "title": title,
                "type": "html",
                "summary": (w.get("publication_year") or "") and f"year={w.get('publication_year')}" or "",
                "original_term": term,
            })
            if len(results) >= max_results:
                break
        return results

    async def _fetch(self, url: str) -> dict:
        loop = asyncio.get_event_loop()

        def _get():
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": "KnowledgeCollector/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))

        try:
            return await loop.run_in_executor(None, _get)
        except Exception:  # noqa: BLE001
            return {}
