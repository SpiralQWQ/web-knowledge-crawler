"""逐站 Cookie 获取公共基类。

每个站点一个独立脚本（tools/get_cookie/get_<site>.py）共享本基类：
定位仓库根 → 读 .env（CRAWL4AI_PY / KC_COOKIE_BROWSER / KC_COOKIE_PROFILE）→
导出该站 Cookie → data/cookies/<site>.txt。

导出通道（自动选择）:
  1. CDP 优先：若 Edge/Chrome 正以调试端口运行（如「启动Edge调试模式.bat」），
     附加读取 —— 能绕过 Edge App-Bound 加密（浏览器关闭后第三方读不到 Cookie）。
  2. 回退：调用 tools/export_cookies.py 从浏览器 profile 直接导出（需浏览器已关闭）。

用法:
  python tools/get_cookie/_base.py <站点名> <域名> [域名...] [--browser <chrome|edge|firefox>] [--profile <名>] [--port <端口>]

示例:
  python tools/get_cookie/_base.py bilibili bilibili.com www.bilibili.com
"""
import os
import subprocess
import sys

if not sys.stdout.isatty():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 仓库根
OUT_DIR = os.path.join(BASE, "data", "cookies")


def _parse_env() -> dict:
    """从仓库根 .env 读取关键配置（系统环境变量优先）。"""
    env = {}
    env_file = os.path.join(BASE, ".env")
    if os.path.isfile(env_file):
        try:
            for line in open(env_file, encoding="utf-8", errors="replace"):
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
        except Exception:  # noqa: BLE001
            pass
    return env


def _pick(key: str, env: dict) -> str:
    return (os.environ.get(key, "").strip() or env.get(key, "")).strip()


def _mask(p: str) -> str:
    """打码路径：替换仓库根与用户主目录。"""
    try:
        s = str(p)
        s = s.replace(BASE, "<repo>").replace(BASE.replace("\\", "/"), "<repo>")
        home = os.path.expanduser("~")
        s = s.replace(home, "<home>").replace(home.replace("\\", "/"), "<home>")
        return s
    except Exception:  # noqa: BLE001
        return str(p)


def _cdp_alive(port: int) -> bool:
    """探测调试端口是否可附加（Edge/Chrome 运行中）。"""
    try:
        import urllib.request
        urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2)
        return True
    except Exception:  # noqa: BLE001
        return False


def export_site(site: str, domains: list, browser: str = "", profile: str = "",
                port: int = 0) -> int:
    """导出指定站点 Cookie 到 data/cookies/<site>.txt。

    port: CDP 调试端口；默认从 KC_CDP_PORT 读，再回退 9222。0 = 探测默认端口。
    """
    env = _parse_env()
    py = _pick("CRAWL4AI_PY", env) or sys.executable
    if _pick("CRAWL4AI_PY", env) and not os.path.exists(py):
        print(f"[错误] CRAWL4AI_PY 不存在: {_mask(py)}（请检查 .env）")
        return 1
    browser = browser or _pick("KC_COOKIE_BROWSER", env) or "edge"
    profile = profile or _pick("KC_COOKIE_PROFILE", env)
    if not port:
        try:
            port = int(os.environ.get("KC_CDP_PORT", "").strip() or "9222")
        except Exception:  # noqa: BLE001
            port = 9222

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, f"{site}.txt")

    domains = [f"https://{d}" if "://" not in d else d for d in domains]
    print(f"═══ 导出 {site} Cookie ═══")
    print(f"  域名: {', '.join(d.split('://')[-1] for d in domains)}")
    print(f"  浏览器: {browser}" + (f"  profile: {profile}" if profile else ""))

    # 通道1：CDP 附加（浏览器运行中 → 绕过 App-Bound 加密）
    if _cdp_alive(port):
        print(f"  [CDP] 附加调试端口 {port} …")
        cmd = [py, os.path.join(BASE, "tools", "get_cookie", "_cdp.py"), out,
               *[d.split("://")[-1] for d in domains], "--port", str(port)]
        sub_env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        r = subprocess.run(cmd, env=sub_env, capture_output=True, timeout=300,
                           encoding="utf-8", errors="replace")
        if r.returncode == 0:
            n = _count(out)
            print(f"✅ {site} 已导出 {n} 条 Cookie → {_mask(out)}")
            return 0
        print(f"  [CDP] 失败，回退 profile 导出: {r.stderr or r.stdout}")

    # 通道2：export_cookies.py（浏览器已关闭 → profile 直接导出）
    cmd = [py, os.path.join(BASE, "tools", "export_cookies.py"), browser, out] + domains
    if profile:
        cmd += ["--profile", profile]
    sub_env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    if profile:
        sub_env["KC_COOKIE_PROFILE"] = profile
    r = subprocess.run(cmd, env=sub_env, capture_output=True, timeout=300,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"[失败] {r.stderr or r.stdout}")
        return 1

    n = _count(out)
    print(f"✅ {site} 已导出 {n} 条 Cookie → {_mask(out)}")
    return 0


def _count(path: str) -> int:
    """统计 Netscape 文件有效 Cookie 行数。"""
    n = 0
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#HttpOnly_"):
                    line = line[len("#HttpOnly_"):]
                if line and not line.startswith("#"):
                    n += 1
    except Exception:  # noqa: BLE001
        pass
    return n


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(2)
    site = args[0]
    domains = [a for a in args[1:] if not a.startswith("--")]
    browser = ""
    profile = ""
    port = 0
    if "--browser" in args:
        i = args.index("--browser")
        if i + 1 < len(args):
            browser = args[i + 1]
    if "--profile" in args:
        i = args.index("--profile")
        if i + 1 < len(args):
            profile = args[i + 1]
    if "--port" in args:
        i = args.index("--port")
        if i + 1 < len(args):
            try:
                port = int(args[i + 1])
            except Exception:  # noqa: BLE001
                pass
    sys.exit(export_site(site, domains, browser, profile, port))
