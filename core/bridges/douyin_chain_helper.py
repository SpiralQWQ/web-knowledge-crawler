# -*- coding: utf-8 -*-
"""借用户已登录的调试浏览器(9222)收集"作者系列"内容链接（抖音/小红书/微博）。

链路：内容页 → 提取作者真实主页 → 打开主页滚动 → 收集内容链接。
抖音/小红书/微博 yt-dlp 都不支持作者主页；真实浏览器最可靠。

用法（由 crawl_guide._browser_collect_author 调用）:
    T.Playwright.../python.exe douyin_chain_helper.py <内容URL> <N> <site>
site ∈ douyin | xiaohongshu | weibo
输出: {"content_urls": [...], "author_url": "...", "error": "..."}
"""
import asyncio
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 各站：作者主页正则 + 内容链接正则（URL 完整保留，缺少前缀时补全）
_SITE_CONF = {
    "douyin": {
        "author": r"(?:https?://www\.douyin\.com)?/user/(?!self|me)[A-Za-z0-9_\-]+",
        "content": r"(?:https?://www\.douyin\.com)?/(?:video|note)/\d+",
        "domain": "https://www.douyin.com",
    },
    "xiaohongshu": {
        "author": r"(?:https?://www\.xiaohongshu\.com)?/user/profile/[A-Za-z0-9]+",
        "content": r"(?:https?://www\.xiaohongshu\.com)?/(?:explore|discovery/item)/[a-f0-9]{24}",
        "domain": "https://www.xiaohongshu.com",
    },
    "weibo": {
        "author": r"(?:https?://weibo\.com)?/u/\d+",
        "content": r"(?:https?://weibo\.com)?/\d+/[A-Za-z0-9]{8,}",
        "domain": "https://weibo.com",
    },
}


def _abs(url: str, domain: str) -> str:
    return url if url.startswith("http") else domain + url


async def collect(content_url: str, n: int, site: str) -> dict:
    conf = _SITE_CONF.get(site) or _SITE_CONF["douyin"]
    result = {"content_urls": [], "author_url": "", "error": ""}
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = next((c for c in b.contexts if c.pages), None)
        if ctx is None:
            result["error"] = "调试浏览器没有可用页面"
            return result
        pg = await ctx.new_page()
        try:
            # 1) 打开内容页，找作者主页
            await pg.goto(content_url, timeout=30000)
            await pg.wait_for_timeout(5000)
            html = await pg.content()
            m = re.search(conf["author"], html)
            if not m:
                result["error"] = "内容页里没找到作者主页链接"
                return result
            result["author_url"] = _abs(m.group(0), conf["domain"])
            # 2) 打开作者主页，滚动加载
            await pg.goto(result["author_url"], timeout=30000)
            await pg.wait_for_timeout(5000)
            for _ in range(4):
                await pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await pg.wait_for_timeout(1500)
            html = await pg.content()
        except Exception as e:  # noqa: BLE001
            result["error"] = str(e)
        finally:
            try:
                await pg.close()
            except Exception:  # noqa: BLE001
                pass
    seen, links = set(), []
    for m in re.finditer(conf["content"], html or ""):
        u = _abs(m.group(0), conf["domain"])
        if u not in seen:
            seen.add(u)
            links.append(u)
        if len(links) >= n:
            break
    result["content_urls"] = links
    return result


def main() -> None:
    if len(sys.argv) < 3:
        print(json.dumps({"content_urls": [], "author_url": ""}))
        return
    url = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    site = sys.argv[3] if len(sys.argv) > 3 else "douyin"
    try:
        result = asyncio.run(collect(url, n, site))
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"content_urls": [], "author_url": "", "error": str(e)}, ensure_ascii=False))
        return
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
