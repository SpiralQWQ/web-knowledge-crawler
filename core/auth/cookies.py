"""Cookie 工具：集中 Cookie 文件解析/导出/路径打码/Windows 安全命名。"""
import os
import time

_WIN_RESERVED = ("con", "aux", "nul", "prn", "com1", "com2", "com3", "com4", "com5",
                 "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4",
                 "lpt5", "lpt6", "lpt7", "lpt8", "lpt9")


# P8：已删除死代码 cookie_header/_SHORT_MAP——web 走 crawl_helper storage_state，doc 走 requests Session，统一不再用 Cookie 头


def mask_path(p) -> str:
    """路径打码（P3）：遮蔽 BASE；P2：遮蔽 URL userinfo 凭据，防日志分享泄露。"""
    try:
        import re as _re
        from . import config
        s = str(p)
        s = s.replace(config.BASE, "<repo>").replace(config.BASE.replace("\\", "/"), "<repo>")
        # M2：也遮蔽用户主目录（KC_COOKIES_FILE 指向 BASE 外绝对路径时防泄漏用户名/盘符布局）
        _home = os.path.expanduser("~")
        s = s.replace(_home, "<home>").replace(_home.replace("\\", "/"), "<home>")
        s = _re.sub(r"(?i)([a-z][a-z0-9+.-]*://)[^/@\s]+@", r"\1<cred>@", s)
        # P2：查询串敏感参数值打码（token/signature/api_key/secret 等），防私有签名链接泄漏
        s = _re.sub(r"(?i)([?&](?:access_token|token|signature|sig|api_key|apikey|key|secret|password|passwd|auth|code)=)[^&\s]+",
                    r"\1<masked>", s)
        return s
    except Exception:  # noqa: BLE001
        return str(p)


def _browser_locked(browser: str) -> bool:
    """P4：检测浏览器 profile 锁（运行中则无法自动导出 Cookie）。"""
    home = os.path.expanduser("~")
    low = browser.lower()
    if low == "edge":
        profile = os.path.join(home, "AppData", "Local", "Microsoft", "Edge", "User Data")
    elif low == "firefox":
        import glob
        for pr in glob.glob(os.path.join(home, ".mozilla", "firefox", "*.default*")):
            for lock in (".parentlock", "lock", ".parent.lock"):  # P9：与 media_collect 锁检测一致
                if os.path.exists(os.path.join(pr, lock)):
                    return True
        return False
    else:
        profile = os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data")
    for lock in ("SingletonLock", "lockfile", "lock"):
        if os.path.exists(os.path.join(profile, lock)):
            return True
    return False


class CookieBlocked(Exception):
    """P4：浏览器配置了但运行中（profile 锁）无法取 Cookie 时抛出，供 web/doc 硬阻断（与视频通道一致）。"""


def allow_anonymous() -> bool:
    """M1：是否允许匿名（KC_ALLOW_ANONYMOUS=1 env 优先 → yaml cookies.allow_anonymous 兜底），与视频通道一致。"""
    v = os.environ.get("KC_ALLOW_ANONYMOUS", "").strip().lower()
    if v:
        return v in ("1", "true", "yes")
    try:
        from . import config
        return bool(config.COOKIES.get("allow_anonymous", False))
    except Exception:  # noqa: BLE001
        return False


def cookie_configured() -> bool:
    """M1：是否配置了任一 Cookie 通道（KC_COOKIES_FILE 或 KC_COOKIE_BROWSER），供 web/doc 判『配置了但不可用→拒匿名』。"""
    try:
        from . import config
        return bool((os.environ.get("KC_COOKIES_FILE", "").strip()
                     or (config.COOKIES.get("cookies_file") or "")).strip()
                    or (os.environ.get("KC_COOKIE_BROWSER", "").strip()
                        or (config.COOKIES.get("browser") or "")).strip())
    except Exception:  # noqa: BLE001
        return False


def resolve_cookie_file() -> str:
    """集中 Cookie 文件路径（env 优先，其次 yaml），相对路径按 BASE 解析。"""
    try:
        from . import config
        cf = (os.environ.get("KC_COOKIES_FILE", "").strip()
              or (config.COOKIES.get("cookies_file") or "")).strip()
        if not cf:
            return ""
        return cf if os.path.isabs(cf) else os.path.join(config.BASE, cf)
    except Exception:  # noqa: BLE001
        return ""


def count_cookie_lines(path: str) -> int:
    """统计 Netscape 文件里有效 Cookie 行数（P2：先剥 #HttpOnly_ 再判注释，防 HttpOnly 会话 Cookie 被计为 0）。"""
    n = 0
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#HttpOnly_"):
                    line = line[len("#HttpOnly_"):]
                if not line or line.startswith("#"):
                    continue
                n += 1
    except Exception:  # noqa: BLE001
        pass
    return n


def ensure_cookie_file() -> str:
    """返回可用 Cookie 文件：优先 cookies_file；否则自动从浏览器导出（缓存 1 天，P3）。"""
    cf = resolve_cookie_file()
    if cf:
        if os.path.exists(cf):
            if count_cookie_lines(cf) > 0:  # P2：空文件不静默匿名
                return cf
            print(f"[警告] Cookie 文件为空: {mask_path(cf)}，尝试自动导出…")
        else:
            print(f"[警告] Cookie 文件不存在: {mask_path(cf)}，尝试自动导出…")
    try:
        import subprocess
        import sys
        from . import config
        browser = (os.environ.get("KC_COOKIE_BROWSER", "").strip()
                   or (config.COOKIES.get("browser") or "")).strip()
        if not browser:
            return ""
        # P4/P7：域名键隔离缓存（对齐 media_collect._auto_export）——先查 24h 新鲜缓存，
        # 缓存优先于锁检查：浏览器开机时 web/doc 也能复用旧导出，不被 CookieBlocked 误拦
        _env_domains = os.environ.get("KC_COOKIE_DOMAINS", "").strip()
        domains = [d.strip() for d in _env_domains.split(",") if d.strip()] if _env_domains else \
            (config.COOKIES.get("domains") or ["36kr.com", "51cto.com", "ai.51cto.com", "aistudio.baidu.com", "alignmentforum.org", "bbs.kanxue.com", "bilibili.com", "changelog.com", "cnblogs.com", "cnodejs.org", "codebuddy.cn", "connectedpapers.com", "coursera.org", "csdn.net", "datawhale.cn", "dev.to", "developer.aliyun.com", "docs.google.com", "douyin.com", "edx.org", "flaticon.com", "gitee.com", "github.com", "hackernoon.com", "hub.baai.ac.cn", "huggingface.co", "huxiu.com", "iconfont.cn", "icourse163.com", "icourse163.org", "imooc.com", "infoq.cn", "jikexueyuan.com", "jiqizhixin.com", "juejin.cn", "kaggle.com", "khanacademy.org", "leetcode.cn", "liblib.art", "lmarena.ai", "lobste.rs", "medium.com", "modelscope.cn", "moonshot.cn", "mp.weixin.qq.com", "news.ycombinator.com", "open.bigmodel.cn", "openrouter.ai", "oschina.net", "overleaf.com", "qbitai.com", "qoder.com.cn", "segmentfault.com", "semanticscholar.org", "soundcloud.com", "sspai.com", "stackoverflow.com", "study.163.com", "thenounproject.com", "tianchi.aliyun.com", "time.geekbang.org", "tmtpost.com", "tongyi.aliyun.com", "tryhackme.com", "universe.roboflow.com", "v2ex.com", "wandb.ai", "weixin.qq.com", "xhslink.com", "xiaohongshu.com", "xuetangx.com", "youtube.com", "zhihu.com"])  # P5/P9 + 小红书/技术社区
        domains = [f"https://{d}" if "://" not in d else d for d in domains]
        # P5：缓存键用完整域名哈希，避免 [:40] 截断碰撞；P6：纳入 browser；M4：纳入 profile，防 Default↔Profile1 切换用错账号
        import hashlib
        _prof = (os.environ.get("KC_COOKIE_PROFILE", "").strip()
                 or (config.COOKIES.get("profile") or "")).strip()
        key = hashlib.md5((browser + "|" + _prof + "|" +
                           ",".join(sorted(d.split("://")[-1] for d in domains))).encode("utf-8")).hexdigest()[:16]
        export = os.path.join(config.BASE, "data", f"cookies_export_{key}.txt")
        if os.path.exists(export) and (time.time() - os.path.getmtime(export)) < 86400:
            if count_cookie_lines(export) > 0:  # P8：缓存命中也要校验非空
                return export
            print("[警告] 缓存的 Cookie 文件为空，重新导出…")
        # 无新鲜缓存才需要导出——此时浏览器锁 → 硬阻断（除非显式 KC_ALLOW_ANONYMOUS=1），与视频通道一致
        if _browser_locked(browser):
            if os.environ.get("KC_ALLOW_ANONYMOUS", "").strip().lower() in ("1", "true", "yes"):
                print("[警告] 浏览器运行中（profile 锁）且已设 KC_ALLOW_ANONYMOUS=1，匿名爬取（登录页会失败）")
                return ""
            raise CookieBlocked("浏览器运行中（profile 锁），无法导出 Cookie；请关闭浏览器或设 KC_COOKIES_FILE")
        py = config.tool("crawl4ai_py") or sys.executable
        # P5：子进程强制 UTF-8 输出，防 Windows GBK 写、父进程 utf-8 读导致乱码
        _env = dict(os.environ)
        _env.setdefault("PYTHONUTF8", "1")
        _env.setdefault("PYTHONIOENCODING", "utf-8")
        if _prof:  # M5：yaml 配置的 profile 必须透传给 export_cookies.py，否则拉的是 Default 却缓存到 Profile 键
            _env["KC_COOKIE_PROFILE"] = _prof
        res = subprocess.run([py, os.path.join(config.BASE, "tools", "export_cookies.py"),
                              browser, export] + domains, capture_output=True, timeout=180, env=_env)
        if res.returncode != 0:
            err = (res.stderr or res.stdout or b"").decode("utf-8", errors="replace").strip()[-200:]
            # P5：区分「缺 playwright 依赖」与「浏览器未登录」，避免误导排查方向
            if "playwright" in err.lower() or "no module named" in err.lower():
                print(f"[警告] Cookie 导出失败：{py} 缺 playwright 依赖。"
                      f"请用带 playwright 的解释器（CRAWL4AI_PY 或 crawl4ai 环境）重试，或 pip install playwright")
            else:
                print(f"[警告] Cookie 导出失败（{py}）：{mask_path(err)}")  # M2：stderr 可能含绝对 profile 路径，打码
            return ""
        if count_cookie_lines(export) > 0:  # P4：按有效行数判定，防空导出误判
            print(f"[Cookie] 已自动导出浏览器 Cookie → {mask_path(export)}")  # P3：打码
            return export
        print(f"[警告] 自动导出浏览器 Cookie 为空（浏览器未登录/需关闭 {browser}），请检查或设 KC_COOKIES_FILE")
    except CookieBlocked:  # M3：显式硬阻断异常必须透传，不能被泛 except 吞掉（否则 web/doc 死代码+误导文案）
        raise
    except Exception as e:  # noqa: BLE001
        print(f"[警告] Cookie 导出异常: {mask_path(str(e))}")
    return ""


def win_safe_name(name: str) -> str:
    """过滤 Windows 保留设备名（CON/AUX/NUL/PRN/COM*/LPT*）与尾随点/空格（P7）。"""
    stem, ext = os.path.splitext(name or "")
    base = stem.rstrip(" .")
    if base.lower().split(".")[0] in _WIN_RESERVED:
        base = "_" + base
    return base + ext
