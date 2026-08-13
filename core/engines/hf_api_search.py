"""HuggingFace API 搜索 — paperswithcode 替代。

paperswithcode 已并入 HuggingFace，用 HF 公开 API 搜模型/数据集。
URL → https://huggingface.co/{modelId}，正文可后续抓取。
"""
import asyncio
import json

from .base import BaseSearcher, register


@register
class HfApiSearcher(BaseSearcher):
    name = "paperswithcode"
    domain = "huggingface.co"

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        n = min(max_results, 50)
        url = f"https://huggingface.co/api/models?search={term.replace(' ', '+')}&limit={n}"
        data = await self._fetch(url)
        results = []
        for m in (data or []):
            model_id = m.get("modelId", "") or ""
            if not model_id:
                continue
            results.append({
                "url": f"https://huggingface.co/{model_id}",
                "title": model_id,
                "type": "html",
                "summary": m.get("pipeline_tag", "") or "",
                "original_term": term,
            })
            if len(results) >= max_results:
                break
        return results

    async def _fetch(self, url: str) -> list:
        def _get():
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": "KnowledgeCollector/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(None, _get)
        except Exception:  # noqa: BLE001
            return []
