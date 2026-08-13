"""通过 CDP（Chrome DevTools Protocol）附加正在运行的 Edge/Chrome，导出 Cookie。

为什么需要 CDP：
  Edge 113+ 启用了 App-Bound 加密，浏览器**关闭后**第三方工具（playwright
  launch_persistent_context / yt-dlp --cookies-from-browser）无法解密 Cookie 库
  （读出 0 条）。但浏览器**运行时**自己持有解密密钥——通过调试端口附加，
  由浏览器进程解密后经 CDP 协议返回 Cookie，即可正常导出。

前置：
  用户先用「启动Edge调试模式.bat」以 --remote-debugging-port 启动 Edge，
  登录各站点后保持 Edge 开着，再运行逐站获取脚本。

用法（供 _base.py 调用）:
  python tools/get_cookie/_cdp.py <输出.txt> <域名...> [--port <端口>]

实现要点：
  - 附加后取默认 context（真实 profile 加载的那个）读 Cookie
  - 附加结束时只断开 CDP 连接，**不关闭用户的浏览器**（browser.close() 对 CDP 附加仅断开）
"""
import asyncio
import os
import sys
import urllib.request

if not sys.stdout.isatty():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_PORT = 9222


def _port_alive(port: int) -> bool:
    """探测调试端口是否可附加。"""
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2)
        return True
    except Exception:  # noqa: BLE001
        return False


async def cdp_export(domains: list, out_path: str, port: int = DEFAULT_PORT) -> int:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("[错误] 需要 playwright（用 CRAWL4AI_PY 环境运行）", file=sys.stderr)
        return 1

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        except Exception as e:  # noqa: BLE001
            print(f"[错误] CDP 附加失败（{port}）: {e}", file=sys.stderr)
            return 1
        # 取默认 context：优先第一个有页面的（真实 profile 加载的那个）
        ctx = None
        for c in browser.contexts:
            if c.pages:
                ctx = c
                break
        if ctx is None and browser.contexts:
            ctx = browser.contexts[0]
        if ctx is None:
            ctx = await browser.new_context()

        # 读取全部 cookie，再按目标域名过滤。
        # 注意：ctx.cookies("裸域名") 会报 Invalid URL（playwright 要求完整 URL），
        # 且子域 cookie（.xxx.com）不会被裸域名匹配到 → 直接用无参读取全量再过滤最稳。
        all_cookies = []
        try:
            all_cookies = await ctx.cookies()
        except Exception:  # noqa: BLE001
            all_cookies = []

        # 归一化目标域名集合（去协议、去 www.）
        target_hosts = set()
        for d in domains or []:
            host = d.split("://")[-1].strip().lower()
            if not host:
                continue
            target_hosts.add(host)
            if host.startswith("www."):
                target_hosts.add(host[4:])

        lines = []
        for c in all_cookies:
            cd = (c.get("domain") or "").strip().lower()
            if not cd:
                continue
            cd_clean = cd[1:] if cd.startswith(".") else cd
            # 匹配：cookie 域名等于目标 或 是目标子域
            if not any(cd_clean == h or cd_clean.endswith("." + h) for h in target_hosts):
                continue
            domain = c.get("domain", "")
            include_sub = "TRUE" if domain.startswith(".") else "FALSE"
            secure = "TRUE" if c.get("secure") else "FALSE"
            http = "#HttpOnly_" if c.get("httpOnly") else ""
            exp = int(c.get("expires", 0) or 0)
            if exp <= 0:
                exp = 0
            lines.append(f"{http}{domain}\t{include_sub}\t{c.get('path', '/')}\t{secure}\t{exp}\t{c.get('name')}\t{c.get('value')}")

        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("# Netscape HTTP Cookie File (cdp_export)\n")
            f.write("\n".join(lines) + "\n")
        if os.name == "nt":
            import subprocess as _sp
            try:
                _sp.run(["icacls", out_path, "/inheritance:r",
                         f"/grant:r", f"{os.environ.get('USERNAME', '')}:F"],
                        capture_output=True, timeout=30)
            except Exception:  # noqa: BLE001
                pass
        else:
            try:
                os.chmod(out_path, 0o600)
            except Exception:  # noqa: BLE001
                pass
        print(f"已导出 {len(lines)} 条 Cookie → {out_path}")
        # CDP 附加：仅断开连接，不关闭用户的浏览器
        try:
            await browser.close()
        except Exception:  # noqa: BLE001
            pass
        return 0


def main() -> int:
    args = sys.argv[1:]
    port = DEFAULT_PORT
    if "--port" in args:
        i = args.index("--port")
        if i + 1 < len(args):
            port = int(args[i + 1])
            args = args[:i] + args[i + 2:]
        else:
            args = args[:i]
    if len(args) < 2:
        print("用法: python _cdp.py <输出.txt> <域名...> [--port <端口>]")
        return 2
    out, domains = args[0], args[1:]
    if not _port_alive(port):
        print(f"[错误] 调试端口 {port} 不可用。请先运行「启动Edge调试模式.bat」并保持 Edge 打开", file=sys.stderr)
        return 1
    return asyncio.run(cdp_export(domains, out, port))


if __name__ == "__main__":
    sys.exit(main())
