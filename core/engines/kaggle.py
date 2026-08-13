"""Kaggle 数据集站内搜索 — Kaggle 公开 API。"""
import asyncio
from urllib.request import urlopen
from urllib.parse import quote
from .base import BaseSearcher, register


@register
class KaggleSearcher(BaseSearcher):
    name = "kaggle"
    domain = "kaggle.com"

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        """使用 Kaggle /api/v1/datasets/list 端点（公开，无需登录）。"""
        url = f"https://www.kaggle.com/api/v1/datasets/list?search={quote(term)}&pageSize={max_results}"
        try:
            data = await self._fetch(url)
            return self._parse(data, term)
        except Exception:
            return []

    async def _fetch(self, url: str) -> dict:
        loop = asyncio.get_event_loop()
        req = urlopen(url, timeout=30)
        import json
        return json.loads(req.read().decode("utf-8"))

    def _parse(self, data, original_term: str, limit: int = 50) -> list[dict]:
        results = []
        datasets = data if isinstance(data, list) else (data.get("datasets") or []) or []
        for ds in datasets[:limit]:
            title = (ds.get("title") or ds.get("titleNullable") or "").strip()
            ref = ds.get("ref") or ""  # 格式: owner/name
            if not ref:
                continue
            # 数据集下载直链（zip 归档）
            url_ = f"https://www.kaggle.com/api/v1/datasets/download/{ref}"
            abstract = (ds.get("subtitle") or ds.get("subtitleNullable") or "").strip()[:500]
            results.append({
                "url": url_,
                "title": title or ref,
                "type": "archive",  # zip 数据集 → 下载归档
                "summary": abstract,
                "original_term": original_term,
            })
        return results
