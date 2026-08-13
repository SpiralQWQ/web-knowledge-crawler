"""学术会议站内搜索 — NeurIPS/ICML/ICLR 均有公开 PDF 列表。无需登录。

注意: ConferencePaperSearcher 是抽象基类，不被 @register 装饰（它不注册）。
子类 NeurIPSConferenceSearcher / ICMLConferenceSearcher / ICLRConferenceSearcher 各自注册。
"""
import asyncio
import re
from urllib.request import urlopen
from .base import BaseSearcher, register


class ConferencePaperSearcher(BaseSearcher):
    """通用学术会议论文搜索适配器(抽象基类)。"""

    async def _fetch(self, url: str):
        """HTTP GET (同步包装到事件循环 executor)。"""
        loop = asyncio.get_event_loop()
        from urllib.request import urlopen
        req = urlopen(url, timeout=30)
        return req.read().decode("utf-8", errors="replace")

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        """站内搜索学术论文 PDF。"""
        url = self.url_template.replace("{term}", term)
        try:
            raw = await self._fetch(url)
            return self._parse_html(raw, term)
        except Exception:
            return []

    def _parse_html(self, html: str, original_term: str, limit: int = 50) -> list[dict]:
        """从 HTML 中提取所有 pdf 链接和标题。"""
        results = []
        # 找所有 pdf 链接 (/papers/YEAR/XXXX.pdf)
        pdf_links = re.findall(r'href="(/papers/\d+/[^"]+\.pdf)"', html)
        # 尝试标题配对
        title_matches = re.findall(
            r'<h\d[^>]*>([^<]+)</h\d>.*?href="(/papers/\d+/[^"]+\.pdf)"',
            html, re.DOTALL
        )
        for i, link in enumerate(pdf_links[:limit]):
            title = ""
            if i < len(title_matches):
                title = title_matches[i][0].strip()
            elif link:
                title = link.split("/")[-1].replace(".pdf", "").replace("-", " ")
            full_url = f"https://{self.domain}{link}" if link.startswith("/") else link
            results.append({
                "url": full_url,
                "title": title,
                "type": "pdf",
                "summary": "",
                "original_term": original_term,
            })
        return results[:limit]


class _OpenReviewApiSearcher(BaseSearcher):
    """走 OpenReview API 的会议搜索基类（iclr/icml/neurips 论文都在 openreview）。"""

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        import json
        from urllib.parse import quote
        url = f"https://api2.openreview.net/notes/search?term={quote(term)}&limit={max_results}"
        try:
            loop = asyncio.get_event_loop()
            req = urllib_request(loop, url, {"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception:  # noqa: BLE001
            return []
        notes = data.get("notes", []) if isinstance(data, dict) else []
        results = []
        for p in notes[:max_results]:
            content = p.get("content", {}) or {}
            title = ""
            if isinstance(content, dict):
                t = content.get("title")
                title = t.get("value", "") if isinstance(t, dict) else str(t or "")
            results.append({
                "url": f"https://openreview.net/forum?id={p.get('id', '')}",
                "title": title,
                "type": "html",
                "summary": "",
                "original_term": term,
            })
        return results


@register
class NeurIPSConferenceSearcher(_OpenReviewApiSearcher):
    name = "neurips"
    domain = "neurips.cc"


@register
class ICMLConferenceSearcher(_OpenReviewApiSearcher):
    name = "icml"
    domain = "icml.cc"


@register
class ICLRConferenceSearcher(_OpenReviewApiSearcher):
    name = "iclr"
    domain = "iclr.cc"


@register
class ACLAnthologySearcher(BaseSearcher):
    """ACL Anthology 搜索 — 有公开 API。"""
    name = "aclanthology"
    domain = "aclanthology.org"
    _headers = {"User-Agent": "Mozilla/5.0"}

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        import json
        from urllib.parse import quote
        url = f"https://aclanthology.org/api/v1/search?q={quote(term)}&limit={max_results}"
        loop = asyncio.get_event_loop()
        req = urlopen(urllib_request(loop, url, self._headers), timeout=30)
        data = json.loads(req.read().decode("utf-8"))
        papers = data if isinstance(data, list) else (data.get("results") or [])
        return [{
            "url": p.get("pdf") or f"https://aclanthology.org/volume/{p.get('volume_id', '')}",
            "title": p.get("title", ""),
            "type": "pdf" if p.get("pdf") else "html",
            "summary": (p.get("abstract") or "")[:500],
            "original_term": term,
        } for p in papers[:max_results]]


@register
class OpenReviewSearcher(BaseSearcher):
    """OpenReview 搜索 — 用 api2.openreview.net/notes/search。"""
    name = "openreview"
    domain = "openreview.net"
    _headers = {"User-Agent": "Mozilla/5.0"}

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        import json
        from urllib.parse import quote
        url = f"https://api2.openreview.net/notes/search?term={quote(term)}&limit={max_results}"
        loop = asyncio.get_event_loop()
        req = urlopen(urllib_request(loop, url, self._headers), timeout=30)
        data = json.loads(req.read().decode("utf-8"))
        papers = data.get("notes", []) if isinstance(data, dict) else []
        return [{
            # /pdf 被 WAF 挡(403)，forum 页可抓 → Crawl4AI 渲染为 markdown
            "url": f"https://openreview.net/forum?id={p.get('id', '')}",
            "title": (p.get("content", {}) or {}).get("title", {}).get("value", "") or str(p.get("title", "") or ""),
            "type": "html",
            "summary": ((p.get("content", {}) or {}).get("abstract", {}).get("value", "") or "")[:500],
            "original_term": term,
        } for p in papers[:max_results]]


def urllib_request(loop, url, headers=None):
    """构造 urllib Request（在事件循环 executor 里执行）。"""
    from urllib.request import Request
    return Request(url, headers=headers or {"User-Agent": "Mozilla/5.0"})
