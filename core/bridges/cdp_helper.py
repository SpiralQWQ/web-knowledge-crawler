"""CDP 子进程桥 — 附加用户已登录的真实浏览器（调试端口），执行站内搜索。

为什么用它：抖音/微博/B站等反爬强的站，独立浏览器（Scrapling/Playwright 新建）
一搜就弹验证码或崩页。而附加**用户已登录的真实浏览器窗口**（--remote-debugging-port 启动），
指纹/登录态全是真人，抖音分不出来 → 不弹验证码，直接出真实内容。

用法:
    python cdp_helper.py <url> [--wait N] [--link-pattern <正则>] [--title-sel <CSS>]
                          [--max-links N] [--port 9222] [--scroll N]

输出: stdout 一行 JSON {url, success, title, items:[{url,title}], html_len, error}

前置: 用户已用「start_edge_debug_mode.bat」启动浏览器并保持打开（默认端口 9222）。
"""
import argparse
import json
import re
import sys

if not sys.stdout.isatty():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_PORT = 9222


def _emit(data: dict):
    print(json.dumps(data, ensure_ascii=False, default=str))


def _port_alive(port: int) -> bool:
    import urllib.request
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2)
        return True
    except Exception:  # noqa: BLE001
        return False


def _looks_captcha(title: str, html_len: int) -> bool:
    """验证码中间页特征：标题含验证码/安全校验，或页面异常小。"""
    if not title:
        return True
    tl = title.lower()
    if any(k in tl for k in ("验证码", "captcha", "安全验证", "verify", "滑动")):
        return True
    # 正常搜索页通常 >30KB；验证码中间页往往只有几 KB
    if html_len < 20000 and any(k in tl for k in ("发现更多", "搜索", "抖音", "weibo", "微博")):
        return True
    return False


def _home_url(url: str) -> str:
    """取站点首页用于预热（先进首页建立正常会话，再进搜索页过验证码）。"""
    import urllib.parse
    parts = urllib.parse.urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"


async def _extract(page, link_pattern: str, title_sel: str, max_links: int):
    """从已渲染页面提取匹配链接的 {url,title}，去重。"""
    pat = re.compile(link_pattern) if link_pattern else None
    js = """
    (titleSel) => {
        const out = [];
        const seen = new Set();
        for (const a of document.querySelectorAll('a[href]')) {
            const href = a.href || '';
            if (!href.startsWith('http')) continue;
            const key = href.split('#')[0];   // 去 fragment 去重（#citing-papers 等）
            if (seen.has(key)) continue;
            let text = (a.getAttribute('title') || '').trim() || (a.innerText || '').trim()
                    || (a.getAttribute('aria-label') || '');
            if (titleSel) {
                // 向上最多 5 层找目标元素（微博正文 p.txt 在链接的祖先卡片里）
                let node = a;
                for (let i = 0; i < 5 && node; i++) {
                    const t = node.querySelector(titleSel);
                    if (t && t.innerText) { text = t.innerText.trim(); break; }
                    node = node.parentElement;
                }
            }
            if (!text && a.parentElement) {
                const pt = a.parentElement.querySelector('span, p, h1, h2, h3, h4');
                if (pt && pt.innerText) text = pt.innerText.trim();
            }
            seen.add(key);
            out.push({url: href, title: text.slice(0, 300)});
        }
        return out;
    }
    """
    all_items = await page.evaluate(js, title_sel or None)
    items = []
    seen = set()
    for it in all_items:
        if pat and not pat.search(it["url"]):
            continue
        if it["url"] in seen:
            continue
        seen.add(it["url"])
        items.append(it)
        if len(items) >= max_links:
            break
    return items


async def cdp_fetch(url: str, wait_ms: int, link_pattern: str, title_sel: str,
                    max_links: int, port: int, scroll_rounds: int = 0,
                    retry: int = 2) -> dict:
    from playwright.async_api import async_playwright

    result = {"url": url, "success": False, "title": "", "items": [],
              "html_len": 0, "error": ""}
    if not _port_alive(port):
        result["error"] = (f"CDP 调试端口 {port} 不可用 —— 请先运行"
                           f"「start_edge_debug_mode.bat」并保持浏览器打开")
        return result

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:  # noqa: BLE001
            result["error"] = f"CDP 附加失败: {e}"
            return result
        ctx = None
        for c in browser.contexts:
            if c.pages:
                ctx = c
                break
        if ctx is None and browser.contexts:
            ctx = browser.contexts[0]
        if ctx is None:
            result["error"] = "浏览器无可用 context"
            try:
                await browser.close()
            except Exception:  # noqa: BLE001
                pass
            return result

        page = None
        try:
            page = await ctx.new_page()
            # 验证码重试：被验证码中间页拦截时，先进首页预热建立正常会话，再进搜索页
            for attempt in range(retry + 1):
                await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                if scroll_rounds > 0:
                    await page.wait_for_timeout(3000)
                    for _ in range(scroll_rounds):
                        await page.evaluate("window.scrollBy(0, window.innerHeight * 1.5)")
                        await page.wait_for_timeout(1500)
                else:
                    await page.wait_for_timeout(wait_ms)
                result["title"] = await page.title()
                try:
                    html = await page.content()
                    result["html_len"] = len(html)
                except Exception:  # noqa: BLE001
                    pass
                if not _looks_captcha(result["title"], result["html_len"]) or attempt >= retry:
                    break
                # 预热：回首页等几秒，再进搜索页
                try:
                    await page.goto(_home_url(url), timeout=60000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(4000)
                except Exception:  # noqa: BLE001
                    pass
            result["items"] = await _extract(page, link_pattern, title_sel, max_links)
            result["success"] = True
        except Exception as e:  # noqa: BLE001
            result["error"] = f"页面异常: {repr(e)[:200]}"
        finally:
            try:
                if page is not None:
                    await page.close()  # 只关临时标签，不影响用户其他页面
            except Exception:  # noqa: BLE001
                pass
            try:
                await browser.close()  # CDP 附加仅断开连接，不关闭用户浏览器
            except Exception:  # noqa: BLE001
                pass
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="CDP 子进程桥")
    ap.add_argument("url")
    ap.add_argument("--wait", type=int, default=12000, help="渲染等待毫秒")
    ap.add_argument("--link-pattern", default="", help="链接正则过滤")
    ap.add_argument("--title-sel", default="", help="标题 CSS 选择器")
    ap.add_argument("--max-links", type=int, default=30)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--scroll", type=int, default=0, help="额外滚动轮数(懒加载)")
    ap.add_argument("--retry", type=int, default=2, help="验证码拦截重试次数")
    args = ap.parse_args()

    import asyncio
    data = asyncio.run(cdp_fetch(args.url, args.wait, args.link_pattern,
                                  args.title_sel, args.max_links, args.port,
                                  args.scroll, args.retry))
    _emit(data)
    return 0 if data["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
