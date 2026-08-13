# -*- coding: utf-8 -*-
"""认证/登录层：登录态检测、调试浏览器启动、登录引导。

从 tools/crawl_guide.py 抽离（架构重构 T12，见 docs/目录契约.md）。
依赖：core.domain（登录判定）+ shared.cookie_util。
"""
import os
import sys
import time

from core.domain import NEED_LOGIN, _has_login_cookie

# 仓库根
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _browser_alive() -> bool:
    import urllib.request
    try:
        urllib.request.urlopen("http://127.0.0.1:9222/json/version", timeout=2)
        return True
    except Exception:  # noqa: BLE001
        return False


def _cdp_open_login(url: str) -> bool:
    """CDP 原生接口在调试浏览器(9222)开新标签并导航到登录页。

    免 playwright 依赖（系统 Python 可能没装 playwright，此前打开登录页静默失败）。
    """
    import json as _json
    import urllib.request, urllib.parse
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:9222/json/new?" + urllib.parse.quote(url, safe=""),
            method="PUT")
        with urllib.request.urlopen(req, timeout=5) as r:
            data = _json.loads(r.read().decode("utf-8", errors="replace"))
            return bool(data.get("id"))
    except Exception:  # noqa: BLE001
        return False


def ensure_browser_open() -> bool:
    """确保调试浏览器(9222)开着；没开自动启动 Edge 调试模式。

    两级启动：
      ① 默认 profile（保留用户登录态）
      ② 若 9222 仍不起（普通 Edge 实例会吞掉 --remote-debugging-port 参数）
         → 用独立 profile 强制新实例（CDP 站搜索仍可用，登录态可能缺）
    """
    import subprocess
    import time
    if _browser_alive():
        return True
    edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge):
        edge = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    print("  🌐 检测到浏览器没开，自动启动调试模式...")
    profile_dir = os.path.join(BASE, "temp", "edge_debug_profile")
    launches = [
        [edge, "--remote-debugging-port=9222"],
        [edge, "--remote-debugging-port=9222", f"--user-data-dir={profile_dir}"],
    ]
    for launch in launches:
        try:
            subprocess.Popen(launch)
        except Exception as e:  # noqa: BLE001
            print(f"  ⚠ 自动启动失败：{e}")
            continue
        for _ in range(15):
            time.sleep(1)
            if _browser_alive():
                print("  ✓ 浏览器已启动")
                return True
    print("  ⚠ 浏览器启动失败。请手动运行「启动Edge调试模式.bat」保持浏览器打开")
    return False


def ensure_login(site: str) -> bool:
    """确保某站有登录 cookie：检测→启浏览器→开登录页→用户登录→自动收集 cookie。"""
    if site not in NEED_LOGIN:
        return True  # 不需要登录
    url, domain, keys = NEED_LOGIN[site]
    if _has_login_cookie(site):
        print(f"  ✓ {site} 已有登录态，直接使用")
        return True
    if not ensure_browser_open():
        print(f"  ⚠ {site} 需要登录，但无法自动开浏览器，请手动开调试模式")
        return False
    # CDP 打开登录页（三层兜底）：①原生 /json/new（免 playwright）→ ②playwright → ③直接调 Edge
    opened = _cdp_open_login(url)
    if not opened:
        try:
            import asyncio
            from playwright.async_api import async_playwright
            async def _open():
                async with async_playwright() as p:
                    b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
                    ctx = [c for c in b.contexts if c.pages][0]
                    pg = await ctx.new_page()
                    await pg.goto(url)
            asyncio.run(_open())
            opened = True
        except Exception:  # noqa: BLE001
            opened = False
    if not opened:
        # ③ 直接调 Edge（新窗口/标签）
        import subprocess
        edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        if not os.path.exists(edge):
            edge = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        if os.path.exists(edge):
            subprocess.Popen([edge, "--remote-debugging-port=9222", url])
            import time
            time.sleep(3)
            opened = True
    if not opened:
        print(f"  ⚠ 自动打开登录页失败，请手动在浏览器打开：{url}")
    print(f"\n  ⚠ {site} 需要登录。已自动打开浏览器登录页，请登录 {site}")
    print("  登录完成后按回车，我会自动收集 cookie...")
    input("  （登录好按回车）")
    # 自动导出 cookie（复用 export_all_cookies.py）
    try:
        import subprocess
        r = subprocess.run([sys.executable, os.path.join(BASE, "tools", "export_all_cookies.py")],
                           capture_output=True, timeout=120, encoding="utf-8", errors="replace")
        if "已导出" in (r.stdout or ""):
            print("  ✓ cookie 已收集")
        else:
            err = (r.stderr or "").strip() or (r.stdout or "").strip() or "(无输出)"
            print(f"  ⚠ cookie 导出没成功：{err[:200]}")
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ cookie 导出异常：{e}")
    # 二次校验：真拿到登录态了吗？（防"没登录就回车"）
    if _has_login_cookie(site):
        return True
    print(f"  ⚠ 好像还没登录成功（没检测到 {site} 的登录凭证）")
    print("    请确认浏览器里真的登录了 {site}，再重新运行指定爬取，会再次引导登录")
    return False
