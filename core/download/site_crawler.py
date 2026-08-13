"""整站抓取器 — 对官方文档/教程/博客站，抓入口页 → 提取站内链接 → 逐页抓取。

用于 crawl_all 的 static/整站 类别：从 config/site_entries.txt 读入口，
用 Crawl4AI 抓入口页，提取同域链接，再逐页抓取正文存 markdown。

注意：这类站没有"搜索"功能，抓取的是整站内容（而非按词搜索）。
"""
import asyncio
import json
import os
import re
import subprocess

from core.domain.site_category import normalize_category


class SiteCrawler:
    """整站抓取器。"""

    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or ""

    def load_entries(self) -> list[dict]:
        """读取 config/site_entries.txt 入口清单。"""
        path = os.path.join(self.config_dir, "config", "site_entries.txt")
        if not os.path.exists(path):
            return []
        entries = []
        for line in open(path, encoding="utf-8", errors="replace"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2:
                entries.append({
                    "url": parts[0],
                    "name": parts[1],
                    "category": normalize_category(parts[2] if len(parts) > 2 else "网页"),
                    "need_cookie": parts[3].lower() == "yes" if len(parts) > 3 else False,
                })
        return entries

    async def fetch_page(self, url: str, cookie_file: str = "") -> str:
        """Crawl4AI 抓单个页面，返回 markdown。"""
        from core.config import tool
        py = tool("crawl4ai_py")
        if not py or not os.path.exists(py):
            return ""
        helper = os.path.join(self.config_dir, "core", "bridges", "crawl_helper.py")
        cmd = [py, helper, url]
        if cookie_file and os.path.exists(cookie_file):
            cmd.append(cookie_file)
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env)
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout=90)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:  # noqa: BLE001
                pass
            return ""
        for line in reversed(out.decode("utf-8", errors="replace").strip().split("\n")):
            if line.strip().startswith("{"):
                try:
                    data = json.loads(line)
                    if data.get("success"):
                        return data.get("markdown", "")
                except Exception:  # noqa: BLE001
                    continue
        return ""

    def extract_links(self, markdown: str, base_domain: str, max_links: int = 50) -> list[str]:
        """从 markdown 提取同域链接。"""
        links = []
        seen = set()
        for m in re.finditer(r"\[([^\]]*)\]\(([^)]+)\)", markdown):
            link = m.group(2)
            if link.startswith("#") or "javascript:" in link:
                continue
            if link.startswith("/"):
                link = "https://" + base_domain + link
            if base_domain not in link:
                continue
            # 过滤常见导航/资产
            if any(x in link for x in [".css", ".js", ".png", ".jpg", ".svg",
                                        "logo", "/static/", "mailto:", "#"]):
                continue
            if link in seen:
                continue
            seen.add(link)
            links.append(link)
            if len(links) >= max_links:
                break
        return links

    async def crawl_site(self, entry: dict, max_pages: int = 30,
                         cookie_file: str = "") -> list[dict]:
        """抓取一个站：入口页 → 提取链接 → 逐页抓取。

        Returns:
            [{"url", "title", "markdown", "category"}, ...]
        """
        from urllib.parse import urlparse
        base_domain = urlparse(entry["url"]).netloc
        cf = cookie_file if entry.get("need_cookie") else ""

        results = []
        # 1. 抓入口页
        entry_md = await self.fetch_page(entry["url"], cf)
        if not entry_md:
            return []
        results.append({
            "url": entry["url"],
            "title": entry["name"],
            "markdown": entry_md,
            "category": entry["category"],
        })

        # 2. 提取链接
        links = self.extract_links(entry_md, base_domain, max_pages)
        # 3. 逐页抓取（限速）
        for i, link in enumerate(links):
            if len(results) >= max_pages:
                break
            md = await self.fetch_page(link, cf)
            if md and len(md) > 300:
                results.append({
                    "url": link,
                    "title": link.rsplit("/", 1)[-1].replace("-", " ")[:60],
                    "markdown": md,
                    "category": entry["category"],
                })
            await asyncio.sleep(1.0)  # 限速防反爬
        return results
