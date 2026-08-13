"""ACL Anthology 站内搜索 — ACL 有公开 API。"""
import asyncio
from urllib.request import urlopen
from urllib.parse import quote
from .base import BaseSearcher, register


@register
class ACLAnthologySearcher(BaseSearcher):
    name = "aclanthology"
    domain = "aclanthology.org"

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        """使用 ACL Anthology Search API。"""
        url = f"https://aclanthology.org/search/?q={quote(term)}&max_results={max_results}"
        try:
            return await self._search_api(term, max_results)
        except Exception:
            # 回退到空结果
            return []

    async def _search_api(self, term: str, max_results: int) -> list[dict]:
        loop = asyncio.get_event_loop()
        req = urlopen(f"https://aclanthology.org/api/v1/search?q={quote(term)}&limit={max_results}", timeout=30)
        import json
        data = json.loads(req.read().decode("utf-8"))
        return self._parse(data, term)

    def _parse(self, data: dict, original_term: str, limit: int = 50) -> list[dict]:
        results = []
        papers = data if isinstance(data, list) else data.get("results", []) or []
        for paper in papers[:limit]:
            title = paper.get("title", "")
            abstract = (paper.get("abstract") or "").strip().replace("\n", " ")[:500]
            url_ = paper.get("url") or f"https://aclanthology.org/volume/{paper.get('volume_id', '')}"
            pdf_url = paper.get("pdf") or ""
            ft = "pdf" if pdf_url else "html"
            results.append({
                "url": pdf_url or url_,
                "title": title,
                "type": ft,
                "summary": abstract,
                "original_term": original_term,
            })
        return results
