"""GitHub 仓库站内搜索 — GitHub Search API（匿名限 60 次/时）。

策略：直接用 GitHub Search API 搜仓库关键词（q=term），
不需要 explore/topics 端点（那个会 404）。
"""
import asyncio
import json
import urllib.request
from urllib.parse import quote

from .base import BaseSearcher, register


@register
class GitHubTopicsSearcher(BaseSearcher):
    name = "github_topics"
    domain = "github.com"
    _headers = {
        "User-Agent": "KnowledgeCollector/1.0 (personal knowledge collection)",
        "Accept": "application/vnd.github+json",
    }

    _SORT_OPT = {"star数": "stars", "最新": "updated", "综合": ""}  # GitHub Search API 排序映射

    async def search(self, term: str, max_results: int = 50, sort: str = "") -> list[dict]:
        """GitHub Search API 搜仓库（q=term；sort 可选 star数/最新，综合不指定）。"""
        # 不重复编码：quote 一次即可
        q = term.strip()
        sort_param = self._SORT_OPT.get(sort, "")
        url = f"https://api.github.com/search/repositories?q={quote(q)}&per_page={min(max_results, 30)}"
        if sort_param:  # 有排序 → 加 sort&order=desc（默认综合=best match 不指定）
            url += f"&sort={sort_param}&order=desc"
        raw = await self._fetch(url)
        items = raw.get("items", []) if isinstance(raw, dict) else []
        results = []
        for i in items[:max_results]:
            html = i.get("html_url", "")
            full_name = i.get("full_name", "")
            desc = (i.get("description") or "").strip()[:300]
            stars = i.get("stargazers_count", 0)
            lang = i.get("language") or ""
            results.append({
                "url": html,
                "title": f"{full_name} ⭐{stars}" + (f" [{lang}]" if lang else ""),
                "type": "repo",  # 触发 git clone
                "summary": desc,
                "original_term": term,
            })
        return results

    async def _fetch(self, url: str) -> dict:
        import os as _os
        import json as _json
        loop = asyncio.get_event_loop()
        headers = dict(self._headers)
        # 尝试用 GH_TOKEN 认证（解除限流 60→5000次/时）
        token = _os.environ.get("GH_TOKEN", "")
        if not token:
            try:
                for line in open(_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))), ".env"),
                                 encoding="utf-8", errors="replace"):
                    line = line.strip()
                    if line.startswith("GH_TOKEN="):
                        token = line.split("=", 1)[1].strip()
                        break
            except Exception:  # noqa: BLE001
                pass
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = urllib.request.Request(url, headers=headers)
        resp = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=30))
        return _json.loads(resp.read().decode("utf-8"))
