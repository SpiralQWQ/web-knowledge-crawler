"""aclanthology 本地 XML 搜索 — 零反爬。

官方仓库 `acl-org/acl-anthology`（已入 data/acl-anthology，245MB）含全量论文 XML。
直接本地解析搜索，无网络请求、无反爬风险。URL 字段 → https://aclanthology.org/{url}/
"""
import asyncio
import glob
import os
import xml.etree.ElementTree as ET

from .base import BaseSearcher, register
from core.config import tool


@register
class AclAnthologyLocalSearcher(BaseSearcher):
    name = "aclanthology"
    domain = "aclanthology.org"

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        root = tool("acl_anthology_dir") or ""
        xml_dir = os.path.join(root, "data", "xml")
        if not os.path.isdir(xml_dir):
            return []
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._search_sync, xml_dir, term, max_results)

    def _search_sync(self, xml_dir: str, term: str, max_results: int) -> list[dict]:
        """同步解析全部 XML，按词过滤 title/abstract。"""
        term_l = term.lower()
        results = []
        for f in glob.glob(os.path.join(xml_dir, "*.xml")):
            try:
                tree = ET.parse(f)
            except Exception:  # noqa: BLE001
                continue
            root = tree.getroot()
            for paper in root.iter("paper"):
                title_el = paper.find("title")
                abs_el = paper.find("abstract")
                title = (title_el.text or "") if title_el is not None else ""
                abstract = (abs_el.text or "") if abs_el is not None else ""
                if term_l in (title + abstract).lower():
                    url_el = paper.find("url")
                    paper_url = (url_el.text or "").strip() if url_el is not None else ""
                    if not paper_url:
                        continue  # 无 URL 的论文（旧数据）无法下载，跳过
                    full = f"https://aclanthology.org/{paper_url}/"
                    results.append({
                        "url": full,
                        "title": title.strip()[:200],
                        "type": "html",
                        "summary": abstract.strip()[:200],
                        "original_term": term,
                    })
                    if len(results) >= max_results:
                        return results
        return results
