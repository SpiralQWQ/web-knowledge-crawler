"""Scrapling 引擎站内搜索 — JS 动态站攻坚层。

替换 Crawl4AI 搜索器（只抓到导航壳），用 Scrapling DynamicFetcher 渲染搜索页，
从渲染后的真实 DOM 提取文章链接。覆盖：CSDN / 掘金 / 知乎 / B站 / 小红书。

为什么用渲染后 DOM 而非接口逆向：
  Scrapling 渲染后页面即含真实文章卡片（实测掘金搜索页解析出 80 条 /post/ 链接），
  免去逐站逆向 x-s/x-zse 签名；capture_xhr 命中的后台接口 URL 已由 helper 带回，
  可作后续正文兜底。
"""
import asyncio
import json
import os
import re

from .base import BaseSearcher, register
from core.config import tool, BASE

# 导航/噪音链接过滤（沿用 crawl4ai_search 的 NAV 思路）
_NAV = ("/anime", "/live.", "show.bilibili", "/game.bilibili", "/platform",
        "/download", "/course", "/pins", "lf-web-assets", "csdnimg",
        "/#/msg", "utm_source", "utm_medium", "logo", "/static/", "/login",
        "account.bilibili", "manga.", "/match/", "app.bilibili", "/search",
        "/settings", "/notification", "/following", "/recommend",
        # 媒体 CDN/资产（medium 等）
        "miro.medium.com", "cdn-client.medium.com", "cdn-static.medium.com",
        ".png", ".jpg", ".jpeg", ".gif", ".webp", ".css", ".js", ".svg", ".ico")


class ScraplingSearcher(BaseSearcher):
    """Scrapling 渲染搜索页的搜索器基类。子类定义 search_url_template/link_pattern/link_prefix。"""

    search_url_template = ""
    link_pattern = ""   # 从渲染 HTML 提取文章链接的正则（group(1) 为链接）
    link_prefix = ""    # 相对链接补全前缀（如 https://juejin.cn）
    link_domain = ""    # 只保留该域名链接
    link_exclude = ()   # 额外排除的 URL 子串（如 devto 的 /t/ 标签页）
    result_type = "html"

    @property
    def name(self) -> str:
        return self.__class__.__dict__.get("name", "")

    @property
    def domain(self) -> str:
        return self.link_domain

    async def _render(self, url: str) -> dict:
        """渲染页面：先 dynamic，若被反爬拦(403/无标题)则自动换 stealth 隐形浏览器。"""
        data = await self._render_once(url, "dynamic")
        if self._looks_blocked(data):
            data = await self._render_once(url, "stealth")
        return data

    @staticmethod
    def _looks_blocked(data: dict) -> bool:
        if not data or not data.get("success"):
            return True
        if data.get("status") in (403, 429, 503):
            return True
        if not data.get("title"):
            return True
        return False

    async def _render_once(self, url: str, mode: str) -> dict:
        """调 scrapling_helper 渲染页面（指定 mode），自动注入登录 cookie。"""
        py = tool("scrapling_py")
        if not py or not os.path.exists(py):
            return {}
        # 🔴 硬性规则：需登录站（小红书/知乎等）cookie 缺失时明确报错，不匿名降级
        from core.auth.cookie_util import REQUIRED_COOKIE_SITES, cookie_header
        if self.name in REQUIRED_COOKIE_SITES:
            domains = REQUIRED_COOKIE_SITES[self.name]
            if not any(cookie_header(d) for d in domains):
                raise RuntimeError(
                    f"{self.name} 需登录 cookie（硬性规则：有 cookie 必须用）。"
                    f"请先在浏览器登录后用「一键导出全部Cookie.bat」导出 {','.join(domains)}")
        helper = os.path.join(BASE, "core", "bridges", "scrapling_helper.py")
        cmd = [py, helper, url, "--mode", mode, "--timeout", "45"]
        # 注入 cookies_all.txt 登录态（zhihu/oschina 等需登录站靠它解锁）
        from core.auth.cookie_util import _cookie_file
        cookie_file = _cookie_file()
        if cookie_file and os.path.exists(cookie_file):
            cmd += ["--cookie", cookie_file]
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env)
        try:
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=90)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:  # noqa: BLE001
                pass
            return {}
        for line in reversed(out.decode("utf-8", errors="replace").strip().split("\n")):
            if line.strip().startswith("{"):
                try:
                    return json.loads(line)
                except Exception:  # noqa: BLE001
                    continue
        return {}

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        url = self.search_url_template.replace("{term}", term)
        data = await self._render(url)
        if not data or not data.get("success") or not data.get("html"):
            return []
        html = data["html"]
        # 锚文本标题映射：href(标准化后) → 真实标题
        titles = self._extract_titles(html)
        results = []
        seen = set()
        for m in re.finditer(self.link_pattern, html):
            link = m.group(1)
            # 剥掉 #fragment（如 /t/123#reply1 → /t/123）
            if "#" in link:
                link = link.split("#", 1)[0]
            if link.startswith("//"):
                link = "https:" + link
            elif link.startswith("/") and self.link_prefix:
                link = self.link_prefix + link
            if self.link_domain and self.link_domain not in link:
                continue
            if any(n in link for n in _NAV):
                continue
            if any(n in link for n in self.link_exclude):
                continue
            if len(link) > 300:
                continue
            if link in seen:
                continue
            seen.add(link)
            # 标题：优先锚文本真实标题，其次 URL 末段
            title = titles.get(link) or titles.get(m.group(1)) or \
                link.rstrip("/").rsplit("/", 1)[-1].split("?")[0].replace("-", " ")
            title = title.strip()[:200] or link
            results.append({
                "url": link,
                "title": title,
                "type": self.result_type,
                "summary": "",
                "original_term": term,
            })
            if len(results) >= max_results:
                break
        return results

    def _extract_titles(self, html: str) -> dict:
        """从渲染 HTML 提取 <a> 锚文本 → 标题映射（标准化 href 与 link_pattern 一致）。"""
        titles = {}
        for m in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.S):
            href = m.group(1).strip()
            text = re.sub(r"<[^>]+>", " ", m.group(2))
            text = re.sub(r"\s+", " ", text).strip()
            if not href or not text or len(text) < 3:
                continue
            if href.startswith("//"):
                href = "https:" + href
            elif href.startswith("/") and self.link_prefix:
                href = self.link_prefix + href
            if "#" in href:
                href = href.split("#", 1)[0]
            if href not in titles or len(text) > len(titles[href]):
                titles[href] = text
        return titles


@register
class CSDNScraplingSearcher(ScraplingSearcher):
    name = "csdn"
    search_url_template = "https://so.csdn.net/so/search?q={term}"
    link_pattern = r'href="(https?://blog\.csdn\.net/[^"]*article/details/\d+[^"]*)"'
    link_prefix = ""
    link_domain = "csdn.net"


@register
class JuejinScraplingSearcher(ScraplingSearcher):
    name = "juejin"
    search_url_template = "https://juejin.cn/search?query={term}"
    link_pattern = r'href="(/post/\d+[^"#]*)"'
    link_prefix = "https://juejin.cn"
    link_domain = "juejin.cn"


@register
class ZhihuScraplingSearcher(ScraplingSearcher):
    name = "zhihu"
    search_url_template = "https://www.zhihu.com/search?type=content&q={term}"
    # 链接为相对路径 /question/... /answer/... /zvideo/...（带 cookie 解锁登录墙）
    link_pattern = r'href="(/(?:question|answer|zvideo|pins)/[^"#]*)"'
    link_prefix = "https://www.zhihu.com"
    link_domain = "zhihu.com"


@register
class BilibiliScraplingSearcher(ScraplingSearcher):
    name = "bilibili"
    search_url_template = "https://search.bilibili.com/all?keyword={term}"
    link_pattern = r'href="(https?://www\.bilibili\.com/video/BV[^"#?]*(?:[?"][^"]*)?)"'
    link_prefix = ""
    link_domain = "bilibili.com"
    result_type = "video"  # B站结果 → yt-dlp 下载


@register
class XhsScraplingSearcher(ScraplingSearcher):
    name = "xiaohongshu"
    search_url_template = "https://www.xiaohongshu.com/search_result?keyword={term}"
    link_pattern = r'href="(/explore/[0-9a-f]+[^"#]*)"'
    link_prefix = "https://www.xiaohongshu.com"
    link_domain = "xiaohongshu.com"
    result_type = "video"  # 小红书笔记 → 视频/图文下载


@register
class SegmentfaultScraplingSearcher(ScraplingSearcher):
    name = "segmentfault"
    search_url_template = "https://segmentfault.com/search?q={term}"
    link_pattern = r'href="(/a/\d+[^"]*)"'
    link_prefix = "https://segmentfault.com"
    link_domain = "segmentfault.com"


@register
class V2exScraplingSearcher(ScraplingSearcher):
    name = "v2ex"
    search_url_template = "https://www.v2ex.com/search?q={term}"
    link_pattern = r'href="(/t/\d+[^"]*)"'
    link_prefix = "https://www.v2ex.com"
    link_domain = "v2ex.com"


@register
class DevToScraplingSearcher(ScraplingSearcher):
    name = "devto"
    search_url_template = "https://dev.to/search?q={term}"
    # 文章格式：相对 /{作者}/{slug}；排除 /t/(标签) /topics/ 等
    link_pattern = r'href="(/[^/"]+/[^/"]+[^"#]*)"'
    link_prefix = "https://dev.to"
    link_domain = "dev.to"
    link_exclude = ("/t/", "/topics/", "/tags/", "/search", "/dashboard", "/settings",
                    "/new", "/~/", "/list", "/admin", "/connect", "/feed")


@register
class AlignmentforumScraplingSearcher(ScraplingSearcher):
    name = "alignmentforum"
    search_url_template = "https://www.alignmentforum.org/search?q={term}"
    # 文章格式：相对 /posts/{哈希}/{slug}
    link_pattern = r'href="(/posts/[^/"]+/[^"#]*)"'
    link_prefix = "https://alignmentforum.org"
    link_domain = "alignmentforum.org"


@register
class ClaudeCodeDocsScraplingSearcher(ScraplingSearcher):
    name = "claude_code_docs"
    search_url_template = "https://code.claude.com/docs/search?q={term}"
    # 文档链接：相对 /docs/en/...（排除 /docs 根、/docs/search）
    link_pattern = r'href="(/docs/[^"#]*)"'
    link_prefix = "https://code.claude.com"
    link_domain = "code.claude.com"
    link_exclude = ("/docs/search", "/docs/en/overview", "/docs/glossary", "/docs/en/index",
                    "/docs/en/quickstart", "sitemap", "llms.txt", ".xml", ".txt")


@register
class CourseraScraplingSearcher(ScraplingSearcher):
    name = "coursera"
    search_url_template = "https://www.coursera.org/search?query={term}"
    link_pattern = r'href="(https://www\.coursera\.org/(?:learn|specializations|projects)/[^"#]*)"'
    link_prefix = ""
    link_domain = "coursera.org"


@register
class EdxScraplingSearcher(ScraplingSearcher):
    name = "edx"
    search_url_template = "https://www.edx.org/search?q={term}"
    link_pattern = r'href="(https://www\.edx\.org/(?:learn|course)/[^"#]*)"'
    link_prefix = ""
    link_domain = "edx.org"
