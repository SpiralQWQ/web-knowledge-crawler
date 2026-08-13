"""Semantic Scholar 站内搜索 — API 优先。无需登录即可搜索。"""
import asyncio
import urllib.request
import urllib.error
from urllib.parse import quote
from .base import BaseSearcher, register


@register
class SemanticScholarSearcher(BaseSearcher):
    name = "semanticscholar"
    domain = "semanticscholar.org"
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        """使用 S2 API /search?q=<term>&limit=N&fields=title,abstract,url arxiv_id。"""
        query = f"{quote(term)}"
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={max_results}&fields=title,abstract,url,externalIds,openAccessPdf"

        # S2 限流严（无 key 约 100/5min），429 加重试退避
        for attempt in range(3):
            try:
                results = await self._fetch(url)
                return self._parse(results, term)
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 2:
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
                return await self._search_web(term, max_results)
            except Exception:
                return await self._search_web(term, max_results)
        return await self._search_web(term, max_results)

    async def _fetch(self, url: str) -> dict:
        loop = asyncio.get_event_loop()
        req = urllib.request.Request(url, headers={"User-Agent": "KnowledgeCollector/1.0"})
        async with await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=30)) as resp:
            import json
            return json.loads(await loop.run_in_executor(None, lambda: resp.read().decode("utf-8")))

    def _parse(self, data: dict, original_term: str) -> list[dict]:
        results = []
        papers = data.get("data", []) if isinstance(data, dict) else []
        for p in (papers or []):
            pdf_url = ""
            oaf = p.get("openAccessPdf")
            if oaf and isinstance(oaf, dict):
                pdf_url = oaf.get("url", "")
            abstract = (p.get("abstract") or "").strip().replace("\n", " ")[:500]
            title = (p.get("title") or "").strip()
            external_ids = p.get("externalIds", {}) or {}
            arxiv_id = external_ids.get("ArXiv", "")
            paper_url = p.get("url", "") or f"https://www.semanticscholar.org/paper/{external_ids.get('DOI', '')}"
            ft = "pdf" if pdf_url else "html"
            results.append({
                "url": pdf_url or paper_url,
                "title": title,
                "type": ft,
                "summary": abstract,
                "original_term": original_term,
            })
        return results

    async def _search_web(self, term: str, max_results: int) -> list[dict]:
        """Playwright 回退: 访问 s2 搜索页提取结果（带超时上限）。"""
        from playwright.async_api import async_playwright
        try:
            return await asyncio.wait_for(self._web_once(term, max_results), timeout=25)
        except Exception:  # noqa: BLE001
            return []

    async def _web_once(self, term: str, max_results: int) -> list[dict]:
        from playwright.async_api import async_playwright
        results = []
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                url = f"https://www.semanticscholar.org/search?q={quote(term)}&sort=relevance"
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                try:
                    await page.wait_for_selector(".paper-title", timeout=8000)
                except Exception:  # noqa: BLE001
                    pass
                links = await page.query_selector_all(".paper-title a, .result-title a")
                for link_el in links[:max_results]:
                    href = await link_el.get_attribute("href")
                    title = (await link_el.inner_text()).strip()[:200]
                    full_url = href if href and href.startswith("http") else f"https://www.semanticscholar.org{href}"
                    results.append({
                        "url": full_url,
                        "title": title,
                        "type": "html",
                        "summary": "",
                        "original_term": term,
                    })
            except Exception:  # noqa: BLE001
                pass
            finally:
                await browser.close()
        return results
