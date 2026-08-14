"""一键导出全部需登录站点的 Cookie 到统一文件（浏览器登录一次 → 全量导出）。

用法:
  python app/export_all_cookies.py              # 用默认浏览器 edge + collector.yaml 域名
  python app/export_all_cookies.py chrome        # 指定浏览器
  python app/export_all_cookies.py edge Profile 1  # 指定 profile

导出通道（自动选择）:
  1. CDP 优先：若 Edge 正以调试端口运行（start_edge_debug_mode.bat）→ 附加读取
     （绕过 Edge App-Bound 加密：浏览器关闭后第三方工具读不到 Cookie）
  2. 回退：export_cookies.py 从浏览器 profile 直接导出（需浏览器已关闭）

导出后设置 KC_COOKIES_FILE=data/cookies_all.txt（或复制到 .env），采集自动复用。
"""
import os
import re
import subprocess
import sys

if not sys.stdout.isatty():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 仓库根
CRAWL4AI_PY = os.environ.get("CRAWL4AI_PY", "").strip()


def _cdp_alive(port: int) -> bool:
    try:
        import urllib.request
        urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2)
        return True
    except Exception:  # noqa: BLE001
        return False

DEFAULT_DOMAINS = [    "36kr.com",
    "51cto.com",
    "ai.51cto.com",
    "aistudio.baidu.com",
    "alignmentforum.org",
    "bbs.kanxue.com",
    "bilibili.com",
    "changelog.com",
    "cnblogs.com",
    "cnodejs.org",
    "codebuddy.cn",
    "connectedpapers.com",
    "coursera.org",
    "csdn.net",
    "datawhale.cn",
    "dev.to",
    "developer.aliyun.com",
    "docs.google.com",
    "douyin.com",
    "edx.org",
    "flaticon.com",
    "gitee.com",
    "github.com",
    "hackernoon.com",
    "hub.baai.ac.cn",
    "huggingface.co",
    "huxiu.com",
    "iconfont.cn",
    "icourse163.com",
    "icourse163.org",
    "imooc.com",
    "infoq.cn",
    "jikexueyuan.com",
    "jiqizhixin.com",
    "juejin.cn",
    "kaggle.com",
    "khanacademy.org",
    "leetcode.cn",
    "liblib.art",
    "lmarena.ai",
    "lobste.rs",
    "medium.com",
    "modelscope.cn",
    "moonshot.cn",
    "mp.weixin.qq.com",
    "news.ycombinator.com",
    "open.bigmodel.cn",
    "openrouter.ai",
    "oschina.net",
    "overleaf.com",
    "qbitai.com",
    "qoder.com.cn",
    "segmentfault.com",
    "semanticscholar.org",
    "soundcloud.com",
    "sspai.com",
    "stackoverflow.com",
    "study.163.com",
    "thenounproject.com",
    "tianchi.aliyun.com",
    "time.geekbang.org",
    "tmtpost.com",
    "tongyi.aliyun.com",
    "tryhackme.com",
    "universe.roboflow.com",
    "v2ex.com",
    "wandb.ai",
    "weixin.qq.com",
    "xhslink.com",
    "xiaohongshu.com",
    "xuetangx.com",
    "youtube.com",
    "zhihu.com",
]


def _load_yaml_domains():
    try:
        import yaml
        with open(os.path.join(BASE, "config", "collector.yaml"), encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        d = ((cfg.get("cookies") or {}).get("domains") or [])
        return [x.strip() for x in d if x and x.strip()]
    except Exception:  # noqa: BLE001
        return []


def main():
    args = sys.argv[1:]
    browser = "edge"
    profile = os.environ.get("KC_COOKIE_PROFILE", "").strip()
    if args:
        browser = args[0]
    if len(args) > 1:
        profile = args[1]

    # 域名：env 覆盖 > yaml > 默认
    env_d = [x.strip() for x in os.environ.get("KC_COOKIE_DOMAINS", "").split(",") if x.strip()]
    domains = env_d or _load_yaml_domains() or DEFAULT_DOMAINS
    domains = [f"https://{d}" if "://" not in d else d for d in domains]

    py = CRAWL4AI_PY or sys.executable
    if CRAWL4AI_PY and not os.path.exists(CRAWL4AI_PY):
        print(f"[错误] CRAWL4AI_PY 不存在: {CRAWL4AI_PY}（请检查 .env）")
        return 1

    out = os.path.join(BASE, "data", "cookies_all.txt")
    os.makedirs(os.path.dirname(out), exist_ok=True)

    print(f"导出 {browser} 浏览器 Cookie → {out}（{len(domains)} 个域名）")
    if profile:
        print(f"使用 profile: {profile}")
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    if profile:
        env["KC_COOKIE_PROFILE"] = profile

    # 通道1：CDP 附加（Edge 调试模式运行中 → 绕过 App-Bound 加密）
    port = 9222
    try:
        port = int(os.environ.get("KC_CDP_PORT", "").strip() or "9222")
    except Exception:  # noqa: BLE001
        port = 9222
    if _cdp_alive(port):
        print(f"[CDP] 附加调试端口 {port} 导出全部域名 …")
        cdp_out = os.path.join(BASE, "data", "cookies_all.txt")
        cmd = [py, os.path.join(BASE, "app", "get_cookie", "_cdp.py"), cdp_out,
               *[d.split("://")[-1] for d in domains], "--port", str(port)]
        r = subprocess.run(cmd, env=env, capture_output=True, timeout=300,
                           encoding="utf-8", errors="replace")
        if r.returncode == 0:
            n = sum(1 for l in open(cdp_out, encoding="utf-8", errors="replace")
                    if l.strip() and not l.startswith("#"))
            print(f"✅ 已导出 {n} 条 Cookie → {cdp_out}")
            return 0
        print(f"[CDP] 失败，回退 profile 导出: {r.stderr or r.stdout}")

    # 通道2：export_cookies.py（浏览器已关闭 → profile 直接导出）
    cmd = [py, os.path.join(BASE, "tools", "export_cookies.py"), browser, out] + domains
    r = subprocess.run(cmd, env=env, capture_output=True, timeout=300,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"[失败] {r.stderr or r.stdout}")
        return 1
    n = sum(1 for l in open(out, encoding="utf-8", errors="replace")
            if l.strip() and not l.startswith("#"))
    print(f"✅ 已导出 {n} 条 Cookie → {out}")
    print(f"下一步：在 .env 设 KC_COOKIES_FILE={os.path.relpath(out, BASE)}（或复制到仓库根 .env）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
