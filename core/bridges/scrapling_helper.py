"""Scrapling 子进程桥 — 在 AAATool 的 Scrapling venv 中运行，供主进程调用。

用法:
    python scrapling_helper.py <url> [--mode fetch|dynamic|stealth] [--timeout N]
    --mode fetch     轻量 HTTP（Fetcher，免浏览器）
    --mode dynamic   全渲染（DynamicFetcher，Playwright 执行 JS，默认）
    --mode stealth   隐形浏览器（StealthyFetcher，过 Cloudflare）

输出: stdout 一行 JSON {url, success, status, title, html, text, xhr_urls, error}

为什么用它：JS 动态站（CSDN/知乎/掘金/B站/小红书）的真实内容靠浏览器执行 JS 才"长出来"，
Crawl4AI 抓到的是导航壳。Scrapling 的 DynamicFetcher 全渲染后页面 DOM 即含真实内容；
capture_xhr 可顺带抓到后台接口 URL（xhr_urls）。
"""
import argparse
import json
import sys


def _emit(data: dict):
    print(json.dumps(data, ensure_ascii=False, default=str))


def _load_netscape_cookies(path: str) -> list[dict]:
    """Netscape cookies.txt → Playwright SetCookieParam dict 列表。"""
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
            domain, _, cpath, secure, expiry, name, value = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]
            try:
                exp = int(float(expiry))
            except ValueError:
                exp = -1
            cookie = {"name": name, "value": value, "domain": domain, "path": cpath}
            if http_only:
                cookie["httpOnly"] = True
            if secure.strip().lower() == "true":
                cookie["secure"] = True
            if exp > 0:
                cookie["expires"] = exp
            cookies.append(cookie)
    return cookies


def _collect_xhr_urls(node, out: list, depth: int = 0):
    """递归收集 captured_xhr 树里的 URL（去重，截断防爆）。"""
    if depth > 3 or not node:
        return
    if isinstance(node, list):
        for x in node:
            _collect_xhr_urls(x, out, depth + 1)
        return
    if hasattr(node, "url") and node.url:
        u = str(node.url)
        if u not in out and not any(skip in u for skip in (".png", ".jpg", ".gif", ".css", ".avis")):
            out.append(u)
    child = getattr(node, "captured_xhr", None)
    if child:
        _collect_xhr_urls(child, out, depth + 1)


def main():
    parser = argparse.ArgumentParser(description="Scrapling 子进程桥")
    parser.add_argument("url", help="要抓取的 URL")
    parser.add_argument("--mode", default="dynamic", choices=["fetch", "dynamic", "stealth"])
    parser.add_argument("--timeout", type=int, default=40)
    parser.add_argument("--cookie", default="", help="Netscape cookies.txt，注入登录态")
    args = parser.parse_args()

    try:
        cookies = _load_netscape_cookies(args.cookie) if args.cookie else None
        if args.mode == "fetch":
            from scrapling import Fetcher
            page = Fetcher().get(args.url, timeout=args.timeout)
        else:
            kwargs = dict(headless=True, network_idle=True, timeout=args.timeout * 1000,
                          capture_xhr='.*')
            if cookies:
                kwargs["cookies"] = cookies
            if args.mode == "stealth":
                from scrapling import StealthyFetcher
                page = StealthyFetcher().fetch(args.url, **kwargs)
            else:
                from scrapling import DynamicFetcher
                page = DynamicFetcher().fetch(args.url, **kwargs)

        status = getattr(page, "status", 0)
        # 标题
        title = ""
        t = page.css("title")
        if t:
            title = (t[0].text or "").strip()
        # 正文：动态渲染后的 HTML 与文本
        html = getattr(page, "body", b"")
        if isinstance(html, bytes):
            html = html.decode("utf-8", errors="replace")
        text = getattr(page, "text", "") or ""
        # 后台接口 URL（capture_xhr 树）
        xhr_urls = []
        _collect_xhr_urls(getattr(page, "captured_xhr", None), xhr_urls)
        # 只保留同域 API/接口链接，截断到 30 条
        from urllib.parse import urlparse
        base_domain = urlparse(args.url).netloc
        xhr_urls = [u for u in xhr_urls if base_domain in u][:30]

        _emit({
            "url": args.url, "success": True, "status": status,
            "title": title, "html": html, "text": text,
            "xhr_urls": xhr_urls, "error": "",
        })
    except Exception as e:  # noqa: BLE001
        _emit({"url": args.url, "success": False, "status": 0,
               "title": "", "html": "", "text": "", "xhr_urls": [],
               "error": str(e)[:300]})


if __name__ == "__main__":
    main()
