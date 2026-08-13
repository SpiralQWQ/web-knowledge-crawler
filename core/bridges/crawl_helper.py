"""被 web_crawler.py 以 subprocess 调用的 Crawl4AI 抓取助手（在 Crawl4AI venv 中运行）。

用法: python crawl_helper.py "<url>" [cookie文件(Netscape)]
→ stdout 输出一行 JSON {url,success,title,markdown,error}

P2：Cookie 用 Playwright storage_state（域名作用域）注入，而非 extra_http_headers 全局注入，
避免会话 Cookie 随第三方子资源/重定向/XHR 泄漏到其他域名。
"""
import asyncio
import json
import time
import os
import sys

# 强制 UTF-8 输出，防 GBK 控制台崩溃（markdown 含 ​ 等特殊字符时 print 会炸）
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

from crawl4ai import AsyncWebCrawler


def _build_storage_state(path: str):
    """Netscape cookies.txt → Playwright storage_state（含 #HttpOnly_、secure、expires）。"""
    cookies = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            http_only = False
            if line.startswith("#HttpOnly_"):
                http_only = True
                line = line[len("#HttpOnly_"):]
            elif line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 7:
                continue
            domain, include_sub, cpath, secure, expiry, name, value = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]
            # P3：includeSubdomains=TRUE → 前导点，使 www./m. 子域也带上登录态
            if include_sub.strip().lower() == "true" and not domain.startswith("."):
                domain = "." + domain
            exp = float(expiry) if expiry.isdigit() and int(expiry) > 0 else -1
            # P5：跳过真过期 Cookie（expires>0 且早于当前时间），与 doc_collector._build_session 策略一致
            if exp > 0 and exp < time.time():
                continue
            cookies.append({
                "name": name, "value": value, "domain": domain, "path": cpath or "/",
                "expires": exp, "httpOnly": http_only,
                "secure": secure.strip().lower() == "true", "sameSite": "Lax",
            })
    return {"cookies": cookies, "origins": []}


async def main(url, cookie_file=""):
    out = {"url": url, "success": False, "title": "", "markdown": ""}
    state = None
    if cookie_file and os.path.exists(cookie_file):
        try:
            state = _build_storage_state(cookie_file)
        except Exception as e:  # noqa: BLE001
            out["error"] = f"cookie 解析失败: {e}"
    try:
        # 知乎反爬特殊处理：Playwright + Edge通道 + 反检测指纹 + cookie
        if "zhihu.com" in url.lower():
            result = await _fetch_zhihu_playwright(url, state)
            if result:
                out.update(result)
                print(json.dumps(out, ensure_ascii=False))
                return
        # 默认：Crawl4AI
        kwargs = {"browser_context": {"storage_state": state}} if state else {}
        async with AsyncWebCrawler(**kwargs) as crawler:
            # 注意：Crawl4AI 0.9.2 传 verbose=False 会触发内部 'verbose' 参数冲突，故不传
            result = await crawler.arun(url=url, magic=True)  # magic=True 渲染 SPA
        out["success"] = bool(result and result.success)
        out["title"] = ((result.metadata or {}).get("title", "") if result else "")
        out["markdown"] = (result.markdown or "") if result else ""
        # P7：序列化前截断巨型 markdown，避免整页 JSON 经 stdout 传回耗尽内存/管道缓冲
        if len(out["markdown"]) > 20 * 1024 * 1024:
            out["markdown"] = out["markdown"][:20 * 1024 * 1024]
            out["truncated"] = True
    except Exception as e:  # noqa: BLE001
        out["error"] = str(e)[:300]
    print(json.dumps(out, ensure_ascii=False))


async def _fetch_zhihu_playwright(url, storage_state):
    """知乎专用：Playwright + Edge真实通道 + 反自动化指纹 + cookie，绕过反爬。

    知乎检测 headless Chromium，必须用 channel='msedge' 的真实 Edge，
    并注入 navigator.webdriver=undefined 等反检测脚本。
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                channel="msedge", headless=True,
                args=["--disable-blink-features=AutomationControlled"])
            ctx = await browser.new_context(
                user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/126.0.0.0 Safari/537.36"),
                locale="zh-CN",
                viewport={"width": 1366, "height": 768},
                storage_state=storage_state if storage_state else None)
            await ctx.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            """)
            page = await ctx.new_page()
            await page.goto(url, wait_until="networkidle", timeout=45000)
            await page.wait_for_timeout(2500)
            # 滚动加载
            for _ in range(3):
                await page.mouse.wheel(0, 1500)
                await page.wait_for_timeout(800)
            title = await page.title()
            body = await page.evaluate("document.body.innerText")
            await browser.close()
            return {"success": len(body) > 300, "title": title, "markdown": body,
                    "error": "" if len(body) > 300 else "内容过少(可能被拦截)"}
    except Exception as e:  # noqa: BLE001
        return {"success": False, "title": "", "markdown": "",
                "error": f"zhihu playwright: {str(e)[:200]}"}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"url": "", "success": False, "error": "缺少 URL 参数"}, ensure_ascii=False))
        sys.exit(2)
    asyncio.run(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ""))
