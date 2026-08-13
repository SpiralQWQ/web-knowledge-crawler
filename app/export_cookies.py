"""导出浏览器 Cookie 到 Netscape cookies.txt（供 Crawl4AI/requests/yt-dlp 共用）。

用途：--cookies-from-browser 在浏览器运行时（Windows DB 锁/DPAPI）会失败；
此工具在浏览器**关闭后**运行一次，把登录 Cookie 导出成文件，设 KC_COOKIES_FILE 即可多通道复用。

用法:
  python tools/export_cookies.py <chrome|edge> <输出.txt> [域名...] [--profile <profile名>]
  示例:
  python tools/export_cookies.py edge cookies/bilibili_youtube.txt bilibili.com youtube.com
  python tools/export_cookies.py edge cookies/work.txt bilibili.com --profile "Profile 1"

profile 选择：默认自动用 Default（或最近修改的真实 profile）；登录态在非默认
profile（如 Edge「工作」profile）时，用 --profile 指定或设环境变量 KC_COOKIE_PROFILE。

注意：必须关闭目标浏览器后再运行（否则 profile 被锁，导出失败）。
"""
import asyncio
import os
import sys

def _setup_stdout():
    """控制台用系统编码(WriteConsoleW自动处理中文)，管道用UTF-8。"""
    try:
        if not sys.stdout.isatty():
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if not sys.stderr.isatty():
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass



def _profile_dir(browser: str, profile: str = "") -> str:
    """定位真实浏览器 profile 目录。

    - profile 显式指定（--profile 或 KC_COOKIE_PROFILE）→ 用它
    - 否则枚举：优先 Default，其次最近修改的真实 profile（含 Cookies 文件）
    - firefox 用 *.default* 目录
    """
    home = os.path.expanduser("~")
    low = browser.lower()
    if low == "edge":
        root = os.path.join(home, r"AppData\Local\Microsoft\Edge\User Data")
    elif low == "firefox":
        import glob
        cands = sorted(glob.glob(os.path.join(home, ".mozilla", "firefox", "*.default*")))
        return cands[0] if cands else ""
    else:
        root = os.path.join(home, r"AppData\Local\Google\Chrome\User Data")
    if profile:
        return os.path.join(root, profile)
    if not os.path.isdir(root):
        return root
    # 枚举真实 profile 子目录（含 Cookies 文件才算真实登录 profile）
    import glob as _g
    real = [d for d in os.listdir(root)
            if os.path.isfile(os.path.join(root, d, "Cookies"))
            or os.path.isfile(os.path.join(root, d, "Network", "Cookies"))]
    if "Default" in real:
        return os.path.join(root, "Default")
    if real:
        # 取最近修改的 profile（用户最近登录的那个最可能有最新 Cookie）
        real = sorted(real, key=lambda d: os.path.getmtime(os.path.join(root, d)), reverse=True)
        return os.path.join(root, real[0])
    return root


async def main(browser, out_path, domains, profile="") -> int:
    low = browser.lower()
    channel = {"chrome": "chrome", "edge": "msedge"}.get(low, "chrome")
    profile = _profile_dir(browser, profile)
    if profile:
        print(f"[信息] 使用浏览器 profile: {profile}")
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("[错误] 需要 playwright（可用 Crawl4AI 环境的 python 运行）", file=sys.stderr)
        return 1
    if not os.path.isdir(profile):
        print(f"[错误] 未找到浏览器 profile: {profile}", file=sys.stderr)
        return 1
    async with async_playwright() as p:
        try:
            # P9：firefox 用 firefox 引擎与默认 profile；chrome/edge 用 chromium + channel
            if low == "firefox":
                ctx = await p.firefox.launch_persistent_context(profile, headless=True)
            else:
                ctx = await p.chromium.launch_persistent_context(profile, channel=channel, headless=True)
        except Exception as e:  # noqa: BLE001
            print(f"[错误] 浏览器启动失败（请关闭 {browser} 后重试）: {e}", file=sys.stderr)
            return 1
        lines = []
        for d in domains or []:
            try:
                cookies = await ctx.cookies(d)
                # P7：host-only 的 www 子域 Cookie 不会被裸域名匹配到，未命中时回退 www.{host} 再取一次
                # P5：按 host 判断（d 可能已带 https:// 前缀），避免拼出 https://www.www.xxx 畸形 URL
                host = d.split("://")[-1]
                if not cookies and not host.startswith("www."):
                    try:
                        cookies = await ctx.cookies("https://www." + host)
                    except Exception:  # noqa: BLE001
                        pass
            except Exception:  # noqa: BLE001
                continue
            for c in cookies:
                domain = c.get("domain", "")
                include_sub = "TRUE" if domain.startswith(".") else "FALSE"
                secure = "TRUE" if c.get("secure") else "FALSE"
                http = "#HttpOnly_" if c.get("httpOnly") else ""
                exp = int(c.get("expires", 0) or 0)
                if exp <= 0:
                    exp = 0  # P6：会话 Cookie 归一为 0（yt-dlp/cookies.py 视为会话）
                lines.append(f"{http}{domain}\t{include_sub}\t{c.get('path', '/')}\t{secure}\t{exp}\t{c.get('name')}\t{c.get('value')}")
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("# Netscape HTTP Cookie File (export_cookies)\n")
            f.write("\n".join(lines) + "\n")
        try:
            if os.name == "nt":  # P7：Windows os.chmod 是 no-op，用 icacls 设 ACL
                import subprocess as _sp
                _sp.run(["icacls", out_path, "/inheritance:r",
                         f"/grant:r", f"{os.environ.get('USERNAME', '')}:F"],
                        capture_output=True, timeout=30)
            else:
                os.chmod(out_path, 0o600)  # 会话令牌文件仅所有者可读
        except Exception:  # noqa: BLE001
            pass
        print(f"已导出 {len(lines)} 条 Cookie → {out_path}")
        await ctx.close()
        return 0


_setup_stdout()


if __name__ == "__main__":
    args = sys.argv[1:]
    # 可选 --profile <名>（如 Edge 的 "Profile 1" / 工作 profile），也支持 KC_COOKIE_PROFILE 环境变量
    profile = os.environ.get("KC_COOKIE_PROFILE", "").strip()
    if "--profile" in args:
        i = args.index("--profile")
        if i + 1 < len(args):
            profile = args[i + 1]
            args = args[:i] + args[i + 2:]
        else:
            # P8：--profile 是最后一个参数（无值）→ 必须移除，防被当域名传给 ctx.cookies()；无值时给出用法提示
            args = args[:i]
            print("[警告] --profile 缺少参数值，已忽略（示例: --profile \"Profile 1\"）")
    if len(args) < 2:
        print("用法: python tools/export_cookies.py <chrome|edge> <输出.txt> [域名...] [--profile <名>]")
        sys.exit(2)
    sys.exit(asyncio.run(main(args[0], args[1], args[2:], profile)))
