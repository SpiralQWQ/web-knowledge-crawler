"""通用 SitemapSearcher — 不逐站配搜索规则，抓 `{站}/sitemap.xml` 拿全站内容 URL。

用途：搜索页被反爬/JS 挡住的站（huxiu/tmtpost/cursor/opencode 等），用 sitemap 兜底，
符合"全量爬取"定位。处理：sitemap index（子 sitemap）递归、gzip 自动解压。
"""
import asyncio
import re

from .base import BaseSearcher, register


class SitemapSearcher(BaseSearcher):
    """抓 sitemap.xml 拿内容 URL 的搜索器基类。子类定义 content_pattern + domain。"""

    domain = ""
    sitemap_path = "/sitemap.xml"   # 部分站 docs 在独立 sitemap
    content_pattern = ""   # 内容 URL 正则（如 r"huxiu\.com/article/\d+\.html"）
    _MAX_SUBS = 12         # 最多跟随的子 sitemap 数
    _TIMEOUT = 20

    @property
    def name(self) -> str:
        return self.__class__.__dict__.get("name", "")

    @property
    def domain_(self) -> str:
        return self.domain

    async def _fetch(self, url: str) -> str:
        """用 requests 抓取（自动解压 gzip），走 executor。"""
        def _get():
            import requests
            r = requests.get(url, timeout=self._TIMEOUT,
                             headers={"User-Agent": "Mozilla/5.0"},
                             verify=False)
            r.raise_for_status()
            return r.text
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get)

    async def _collect_urls(self, url: str, depth: int = 0, seen: set | None = None) -> list[str]:
        """递归收集 sitemap 里的全部 URL（处理 index + gzip）。"""
        seen = seen or set()
        if depth > 2 or url in seen:
            return []
        seen.add(url)
        try:
            body = await self._fetch(url)
        except Exception:  # noqa: BLE001
            return []
        # 若是 sitemap index（含 <sitemap><loc>）→ 跟随子 sitemap
        subs = re.findall(r"<sitemap>\s*<loc>(.*?)</loc>", body, re.S)
        if subs:
            out = []
            for sub in subs[: self._MAX_SUBS]:
                out += await self._collect_urls(sub.strip(), depth + 1, seen)
            return out
        # 否则是 urlset → 提取 loc
        return [u.strip() for u in re.findall(r"<loc>(.*?)</loc>", body, re.S)]

    @staticmethod
    def _tokenize(text: str) -> list:
        """URL slug / 标题 → 词元（按 URL 分隔符 + 空格切分，去数字/短词）。"""
        segs = re.split(r"[/\-_?.=&#]", str(text).lower())
        words = []
        for s in segs:
            words.extend(s.split())
        return [w for w in words if w and len(w) > 2 and not w.isdigit()]

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        all_urls = await self._collect_urls(f"https://{self.domain}{self.sitemap_path}")
        if not all_urls:
            return []
        # 过滤内容 URL（匹配 content_pattern）
        if self.content_pattern:
            content = [u for u in all_urls if re.search(self.content_pattern, u)]
        else:
            content = all_urls
        # 去重
        seen, dedup = set(), []
        for u in content:
            if u not in seen:
                seen.add(u)
                dedup.append(u)
        # BM25 按词打分（URL slug 分词）→ 有词重叠才返回，不再兜底全量（避免 0% 相关）
        try:
            from rank_bm25 import BM25Okapi
            docs = [self._tokenize(u) for u in dedup]
            bm25 = BM25Okapi(docs)
            scores = bm25.get_scores(self._tokenize(term))
            ranked = sorted(zip(dedup, scores), key=lambda x: -x[1])
            selected = [u for u, s in ranked if s > 0][:max_results]
        except Exception:  # noqa: BLE001
            # 兜底：原词法匹配
            selected = [u for u in dedup if term.lower() in u.lower()][:max_results]
        if not selected:
            return []  # 无相关文档，诚实返回空（不假装）
        return [{
            "url": u,
            "title": u.rstrip("/").rsplit("/", 1)[-1].replace("-", " ").replace("_", " ")[:200] or u,
            "type": "html",
            "summary": "",
            "original_term": term,
        } for u in selected]


@register
class HuxiuSitemapSearcher(SitemapSearcher):
    name = "huxiu"
    domain = "www.huxiu.com"
    content_pattern = r"huxiu\.com/article/\d+\.html"


@register
class TmtpostSitemapSearcher(SitemapSearcher):
    name = "tmtpost"
    domain = "www.tmtpost.com"
    content_pattern = r"tmtpost\.com/\d+\.html"


@register
class CursorSitemapSearcher(SitemapSearcher):
    name = "cursor"
    domain = "cursor.com"
    sitemap_path = "/docs/sitemap.xml"
    content_pattern = r"cursor\.com/docs/"


@register
class ClaudeCodeDocsSitemapSearcher(SitemapSearcher):
    """Claude 官方文档 — code.claude.com 已失效→platform.claude.com，搜索页改版无 URL 参数 → sitemap 兜底。"""
    name = "claude_code_docs"
    domain = "platform.claude.com"
    sitemap_path = "/docs/sitemap.xml"
    content_pattern = r"platform\.claude\.com/docs/en/"


@register
class OpencodeSitemapSearcher(SitemapSearcher):
    name = "opencode"
    domain = "opencode.ai"
    content_pattern = r"opencode\.ai/docs/"


@register
class QoderSitemapSearcher(SitemapSearcher):
    name = "qoder_docs"
    domain = "qoder.com.cn"
    content_pattern = r"qoder\.com\.cn/docs/"
