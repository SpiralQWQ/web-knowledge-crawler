"""Crawl4AI 通用站内搜索 — 直接抓取各站搜索页，提取结果链接。

为什么用这个：
  很多站的 Playwright 模拟搜索在这个环境跑不动（浏览器启动失败/选择器失效），
  但 Crawl4AI（AsyncWebCrawler + magic=True）能稳定抓取搜索页 HTML。

策略：给定搜索 URL 模板 + cookie → Crawl4AI 抓取 → 正则提取站内链接。
"""
import asyncio
import json
import os
import re
import subprocess

from .base import BaseSearcher, register


class Crawl4AISearcher(BaseSearcher):
    """通用 Crawl4AI 抓取搜索页的搜索器。

    子类只需定义 search_url_template（含 {term}）和 domain。
    """

    # 子类覆盖
    search_url_template = ""
    link_pattern = r'href="(https?://[^"#]+)"'  # 默认提取所有绝对链接
    link_domain = ""  # 只保留该域名的链接，空=不过滤
    result_type = "html"  # 结果类型：html/video/repo/pdf

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        from core.config import tool
        py = tool("crawl4ai_py")
        if not py or not os.path.exists(py):
            return []
        from core.auth.cookie_util import _cookie_file
        cookie_file = _cookie_file()

        url = self.search_url_template.replace("{term}", term)
        cmd = [py, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "crawl_helper.py"), url]
        if cookie_file:
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
            return []

        # 解析最后一行 JSON
        data = None
        for line in reversed(out.decode("utf-8", errors="replace").strip().split("\n")):
            if line.strip().startswith("{"):
                try:
                    data = json.loads(line)
                    break
                except Exception:  # noqa: BLE001
                    continue
        if not data or not data.get("success") or not data.get("markdown"):
            return []

        md = data["markdown"]
        # 提取链接（子类可 override extract_links 定制过滤）
        from urllib.parse import urlparse
        base_domain = urlparse(self.search_url_template).netloc or self.link_domain
        links = self.extract_links(md, base_domain, max_results)
        # 导航噪音：排除常见导航/无关链接
        NAV = ("/anime", "/live.", "show.bilibili", "/game.bilibili", "/platform",
               "/download", "/course", "/pins", "lf-web-assets", "csdnimg",
               "/#/msg", "utm_source", "utm_medium", "logo", "/static/", "/login",
               "account.bilibili", "manga.", "/match/", "app.bilibili")
        results = []
        seen = set()
        for link in links:
            if link.startswith("#") or "javascript:" in link:
                continue
            if link.startswith("/"):
                link = self.domain + link
            if self.link_domain and self.link_domain not in link:
                continue
            # 过滤导航/无关
            if any(n in link for n in NAV):
                continue
            # 过滤超长链接
            if len(link) > 300:
                continue
            if link in seen:
                continue
            seen.add(link)
            title = link.rsplit("/", 1)[-1].replace("-", " ")[:200] if not link.rstrip("/").endswith("/") else link.rstrip("/").split("/")[-1]
            results.append({
                "url": link,
                "title": title[:200],
                "type": self.result_type,
                "summary": "",
                "original_term": term,
            })
            if len(results) >= max_results:
                break
        return results

    def extract_links(self, markdown: str, base_domain: str, max_links: int = 50) -> list[str]:
        """默认链接提取：全部 markdown 链接（子类可 override 定制）。"""
        import re
        links = []
        seen = set()
        for m in re.finditer(r"\[([^\]]*)\]\(([^)]+)\)", markdown):
            link = m.group(2)
            if link.startswith("#") or "javascript:" in link:
                continue
            if link.startswith("/"):
                link = "https://" + base_domain + link
            if self.link_domain and self.link_domain not in link:
                continue
            if link in seen:
                continue
            seen.add(link)
            links.append(link)
            if len(links) >= max_links:
                break
        return links


@register
class BilibiliCrawlSearcher(Crawl4AISearcher):
    name = "bilibili"
    domain = "https://search.bilibili.com"
    search_url_template = "https://search.bilibili.com/all?keyword={term}"
    link_domain = "bilibili.com"
    result_type = "video"  # B站结果 → 视频下载(yt-dlp)

    # B站：只保留真实视频页链接(/video/BVxxx)，过滤导航
    def extract_links(self, markdown, base_domain, max_links=50):
        import re
        links = []
        seen = set()
        for m in re.finditer(r"\[([^\]]*)\]\(([^)]+)\)", markdown):
            link = m.group(2)
            if link.startswith("/"):
                link = "https://" + base_domain + link
            if "bilibili.com/video/" not in link:  # 只保留视频页
                continue
            if link in seen:
                continue
            seen.add(link)
            links.append(link)
            if len(links) >= max_links:
                break
        return links


@register
class CSDNCrawlSearcher(Crawl4AISearcher):
    name = "csdn"
    domain = "https://so.csdn.net"
    search_url_template = "https://so.csdn.net/so/search?q={term}"
    link_domain = "csdn.net"


@register
class JuejinCrawlSearcher(Crawl4AISearcher):
    name = "juejin"
    domain = "https://juejin.cn"
    search_url_template = "https://juejin.cn/search?query={term}"
    link_domain = "juejin.cn"


@register
class ZhihuCrawlSearcher(Crawl4AISearcher):
    name = "zhihu"
    domain = "https://www.zhihu.com"
    search_url_template = "https://www.zhihu.com/search?type=content&q={term}"
    link_domain = "zhihu.com"


@register
class XhsCrawlSearcher(Crawl4AISearcher):
    name = "xiaohongshu"
    domain = "https://www.xiaohongshu.com"
    search_url_template = "https://www.xiaohongshu.com/search_result?keyword={term}"
    link_domain = "xiaohongshu.com"
    result_type = "video"  # 小红书笔记 → 视频/图文下载
