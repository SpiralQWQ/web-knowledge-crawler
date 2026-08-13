"""Hugging Face 站内搜索 — HF 有公开 Search API。

资源类型（举一反三）：
  模型   → 模型真实文件：config.json(json 配置) + README.md(markdown 模型卡)
  数据集 → README.md(markdown 数据集卡)，gated 数据集才兜底 html 页
不返回裸页面 html，让下载器按扩展名走真实文件下载。
"""
import asyncio
from urllib.request import urlopen
from urllib.parse import quote
from .base import BaseSearcher, register


@register
class HuggingFaceSearcher(BaseSearcher):
    name = "huggingface"
    domain = "huggingface.co"

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        """使用 HF Models/Datasets Search API。"""
        try:
            models = await self._search_models(term, max_results // 2)
            datasets = await self._search_datasets(term, max_results // 3)
            return models + datasets[:max_results]
        except Exception:
            return []

    async def _search_models(self, term: str, max_results: int) -> list[dict]:
        url = f"https://huggingface.co/api/models?search={quote(term)}&limit={max_results}&sort=downloads&direction=-1"
        return await self._fetch(url, term, "model")

    async def _search_datasets(self, term: str, max_results: int) -> list[dict]:
        url = f"https://huggingface.co/api/datasets?search={quote(term)}&limit={max_results}&sort=downloads&direction=-1"
        return await self._fetch(url, term, "dataset")

    async def _fetch(self, url: str, original_term: str, kind: str) -> list[dict]:
        loop = asyncio.get_event_loop()
        req = urlopen(url, timeout=30)
        import json
        items = json.loads(req.read().decode("utf-8"))
        return self._parse(items, original_term, kind)

    def _parse(self, items: list, original_term: str, kind: str) -> list[dict]:
        results = []
        for item in items:
            model_id = (item.get("modelId") or item.get("id") or "").strip()
            if not model_id:
                continue
            name = model_id.rsplit("/", 1)[-1] or model_id
            abstract = (item.get("description") or "").strip()[:300]
            if kind == "model":
                # 模型 → 真实文件：config.json(json) + README.md(markdown)
                results.append({
                    "url": f"https://huggingface.co/{model_id}/resolve/main/config.json",
                    "title": f"[{name}] config.json",
                    "type": "json",
                    "summary": abstract,
                    "original_term": original_term,
                })
                results.append({
                    "url": f"https://huggingface.co/{model_id}/resolve/main/README.md",
                    "title": f"[{name}] 模型卡",
                    "type": "markdown",
                    "summary": abstract,
                    "original_term": original_term,
                })
            else:
                # 数据集 → README.md(数据集卡)；gated 才兜底页面
                if item.get("gated"):
                    results.append({
                        "url": f"https://huggingface.co/datasets/{model_id}",
                        "title": f"[{name}] 数据集(gated)",
                        "type": "html",
                        "summary": abstract,
                        "original_term": original_term,
                    })
                else:
                    results.append({
                        "url": f"https://huggingface.co/datasets/{model_id}/resolve/main/README.md",
                        "title": f"[{name}] 数据集卡",
                        "type": "markdown",
                        "summary": abstract,
                        "original_term": original_term,
                    })
        return results
