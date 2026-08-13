"""arXiv 站内搜索 — arXiv API (XML) 无需登录。

P8：限定计算机/AI 相关领域分类（cs.*/eess.*/stat.ML/stat.AP 等），
排除天文(astro-ph)/物理(physics.*)/数学(math.*) 等无关领域，避免噪音论文。
"""
import asyncio
import xml.etree.ElementTree as ET
from urllib.parse import quote
from urllib.request import urlopen

from .base import BaseSearcher, register

_NS = {"atom": "http://www.w3.org/2005/Atom"}

# arXiv 计算机/AI 相关分类前缀（arXiv 分类体系）
_CS_CATS = (
    "cs.",          # 计算机科学全部
    "eess.",        # 电气工程与系统
    "stat.ML", "stat.AP", "stat.CO", "stat.TH",  # 统计(ML/应用/计算/理论)
    "q-bio.QM",     # 定量生物学(定量方法)
    "q-fin.CP",     # 量化金融(计算金融)
)


def _build_query(term: str) -> str:
    """构建限定领域的 arXiv 查询。"""
    # 搜索词 + 限定计算机相关分类
    cat_part = " OR ".join(f"cat:{c}*" if c.endswith(".") else f"cat:{c}" for c in _CS_CATS)
    return f'all:"{term}" AND ({cat_part})'


@register
class ArxivSearcher(BaseSearcher):
    name = "arxiv"
    domain = "arxiv.org"
    base_url = "https://export.arxiv.org/api/query"

    _SORT_OPT = {"最新": "submittedDate", "相关": "relevance", "综合": ""}  # arXiv API 排序映射

    async def search(self, term: str, max_results: int = 50, sort: str = "") -> list[dict]:
        query = _build_query(term)
        url = f"{self.base_url}?search_query={quote(query)}&start=0&max_results={max_results}"
        sort_by = self._SORT_OPT.get(sort, "")
        if sort_by:  # 有排序 → 加 sortBy/sortOrder（综合不指定=arXiv默认）
            url += f"&sortBy={sort_by}&sortOrder=descending"
        raw = await self._fetch(url)
        return self._parse(raw, term)

    async def _fetch(self, url: str) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: urlopen(url, timeout=30).read().decode("utf-8"))

    def _parse(self, xml: str, original_term: str) -> list[dict]:
        results = []
        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            return results
        ns = {"a": "http://www.w3.org/2005/Atom"}
        # 天文/物理/数学 噪音信号（二次过滤，双保险）
        NON_CS = (
            "galaxy", "stellar", "star formation", "astronom", "cosmolog", "supernova",
            "quasar", "nebula", "gravitation", "solar", "planetary", "redshift",
            "magnetic field", "plasma", "particle physics", "hadron", "neutrino",
            "algebra", "topolog", "manifold", "theorem", "homology", "differential geometry",
            "quantum field", "condensed matter", "crystallograph", "molecule",
            "gene expression", "protein", "molecular", "biochem", "neuro science",
            "meteorolog", "atmospheric", "oceanograph", "earthquake", "geolog",
        )
        for entry in root.findall("a:entry", ns):
            title = (entry.findtext("a:title", "", ns) or "").strip().replace("\n", " ")
            summary = (entry.findtext("a:summary", "", ns) or "").strip().replace("\n", " ")
            # 领域二次过滤：标题/摘要含明显非CS信号 → 跳过
            combined = (title + " " + summary).lower()
            if any(k in combined for k in NON_CS):
                continue
            # arXiv 的 abs 链接: <a:id>http://arxiv.org/abs/XXXX.XXXXX</a:id>
            id_el = entry.find("a:id", ns)
            id_ = id_el.text.strip() if id_el is not None and id_el.text else ""
            pdf_url = ""
            if id_:
                pdf_url = id_.replace("/abs/", "/pdf/") + ".pdf"
            results.append({
                "url": pdf_url,
                "title": title,
                "type": "pdf",
                "summary": summary[:500],
                "original_term": original_term,
            })
        return results
