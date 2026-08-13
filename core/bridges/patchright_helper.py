"""patchright 独立隐形渲染器 — 在 AAATool 的 patchright venv 中运行。

用法:
    python patchright_helper.py <url> [cookie文件(Netscape)] [--wait N]
→ stdout 一行 JSON {url, success, title, html, error}

为什么用它：patchright 是源码级隐形 Chromium（undetected Playwright），
比 Crawl4AI 更难被反爬检测，适合高反爬/需登录站（配合 cookie 注入）。
"""
import argparse
import json
import sys


def _emit(data: dict):
    print(json.dumps(data, ensure_ascii=False, default=str))


def _load_netscape_cookies(path: str) -> list[dict]:
    """Netscape cookies.txt → Playwright cookie dict 列表。"""
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


def main():
    parser = argparse.ArgumentParser(description="patchright 隐形渲染器")
    parser.add_argument("url")
    parser.add_argument("cookie_file", nargs="?", default="", help="Netscape cookies.txt")
    parser.add_argument("--wait", type=int, default=3, help="加载后等待秒数")
    args = parser.parse_args()

    try:
        from patchright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(
                locale="zh-CN",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
            )
            if args.cookie_file:
                cookies = _load_netscape_cookies(args.cookie_file)
                if cookies:
                    context.add_cookies(cookies)
            page = context.new_page()
            page.goto(args.url, wait_until="load", timeout=45000)
            if args.wait > 0:
                page.wait_for_timeout(args.wait * 1000)
            title = page.title()
            html = page.content()
            browser.close()
            _emit({"url": args.url, "success": True, "title": title,
                   "html": html, "error": ""})
    except Exception as e:  # noqa: BLE001
        _emit({"url": args.url, "success": False, "title": "", "html": "", "error": str(e)[:300]})


if __name__ == "__main__":
    main()
