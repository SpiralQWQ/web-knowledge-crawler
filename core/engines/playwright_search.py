"""Playwright 通用站内搜索适配器 — 适用于无API但有搜索框的站点。

使用方式: 每个站点定义一个子类，指定搜索URL模板和结果提取CSS选择器。
支持自动降级: API失败 → Playwright模拟 → 返回空。
"""
import asyncio
from urllib.parse import quote
from .base import BaseSearcher


class PlaywrightSearcher(BaseSearcher):
    """通用 Playwright 站内搜索基类。子类只需定义 search_url_template 和 extract_selectors。"""

    # URL 模板 - {term} 会被替换为搜索词
    search_url_template = ""

    # CSS 选择器 - 如何找到搜索结果项
    item_selector = "a.result-link"

    # 标题、摘要、链接的提取路径 (相对于 item)
    title_selector = ".title"
    url_selector = "a"
    summary_selector = ".summary"

    # 最大等待加载时间(毫秒)
    wait_timeout = 15000

    # 结果资源类型：html/video/repo/pdf...
    result_type = "html"

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        from playwright.async_api import async_playwright
        results = []
        search_url = self.search_url_template.replace("{term}", quote(term))

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await page.goto(search_url, wait_until="domcontentloaded", timeout=self.wait_timeout)
                await page.wait_for_load_state("networkidle", timeout=5000)

                items = await page.query_selector_all(self.item_selector)
                for item in items[:max_results]:
                    result = await self._extract_item(item, page)
                    if result and result.get("url"):
                        result["original_term"] = term
                        results.append(result)
            except Exception:
                pass  # 任何异常都回退到空结果，不阻塞
            finally:
                await browser.close()
        return results[:max_results]

    async def _extract_item(self, item, page) -> dict | None:
        """从单个搜索结果项中提取数据。"""
        # 优先用 item 自身的 selector，回退到 page 级查找
        try:
            url_el = await item.query_selector(self.url_selector)
            href = await url_el.get_attribute("href") if url_el else None
            if not href or not href.startswith("http"):
                full_link = await item.get_attribute("href")
                href = full_link if full_link and full_link.startswith("http") else None
                if not href:
                    parent_link = await item.query_selector("a[href]")
                    if parent_link:
                        href = await parent_link.get_attribute("href")

            title_el = await item.query_selector(self.title_selector)
            title = (await title_el.inner_text()).strip()[:300] if title_el else ""

            summary_el = await item.query_selector(self.summary_selector)
            summary = (await summary_el.inner_text()).strip()[:500] if summary_el else ""

            return {"url": href, "title": title, "type": self.result_type, "summary": summary}
        except Exception:
            return None
