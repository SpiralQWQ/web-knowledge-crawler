"""Cookie 工具 — 供搜索器 API 请求复用。

从 data/cookies_all.txt（或 KC_COOKIES_FILE）读取 Netscape 格式 cookie。
关键：按目标域名过滤，只取该域（及子域）的 cookie，避免 431 头过大。

🔴 硬性规则（用户明确要求）：有 cookie 必须注入使用，严禁匿名降级。
REQUIRED_COOKIE_SITES 里的站无 cookie 时搜索必须明确报错，不得静默匿名爬。
"""
import os


# 必须 cookie 才能搜索的站（Scrapling/API 注入类）→ 其 cookie 域名
# 硬性规则：这些站 cookie 缺失时搜索直接报错（见 scrapling_search._render_once），不匿名降级
REQUIRED_COOKIE_SITES = {
    "xiaohongshu": ("xiaohongshu.com", "xhslink.com"),
    "zhihu": ("zhihu.com",),
}
# CDP 站（douyin/weibo/leetcode/gitee 等）由真实浏览器自带登录态，无需 cookies_all.txt 强制注入


def _cookie_file() -> str:
    """定位 cookie 文件路径。"""
    try:
        import core.config as config
    except Exception:  # noqa: BLE001
        return ""
    cf = os.environ.get("KC_COOKIES_FILE", "").strip()
    if not cf:
        cf = (config.COOKIES.get("cookies_file") or "").strip()
    if not cf:
        default = os.path.join(config.BASE, "data", "cookies_all.txt")
        if os.path.exists(default):
            cf = default
    return cf if (cf and os.path.exists(cf)) else ""


def check_required_cookies() -> list[str]:
    """自检：返回缺少登录 cookie 的需登录站清单（违反硬性规则时非空）。

    用于搜索器搜索前校验 + 回归测试门禁。缺 cookie 的站必须明确提示补登录，
    绝不静默匿名降级。
    """
    missing = []
    for site, domains in REQUIRED_COOKIE_SITES.items():
        has = any(cookie_header(d) for d in domains)
        if not has:
            missing.append(site)
    return missing


def check_all_cookie_sites() -> dict[str, int]:
    """诊断：返回 cookie 文件里所有有登录态的域名（域名→cookie 数）。

    用于核查"有 cookie 的站是否都注入使用"（硬性规则）。Scrapling 站由
    `_render_once` 统一注入 cookies_all.txt，CDP 站由真实浏览器自带；
    此函数暴露全量登录态供诊断/报告。
    """
    cf = _cookie_file()
    counts: dict[str, int] = {}
    if not cf:
        return counts
    with open(cf, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("# Netscape") or line.startswith("# "):
                continue
            parts = line.replace("#HttpOnly_", "").split("\t")
            if len(parts) >= 7:
                d = parts[0].lstrip(".")
                counts[d] = counts.get(d, 0) + 1
    return counts


def cookie_header(domain: str = "") -> str:
    """返回某域名适用的 Cookie 头。

    Args:
        domain: 目标域名（如 github.com）。空 = 取全部（可能过大）。

    Returns:
        "name=value; name2=value2" 或空串。
    """
    cf = _cookie_file()
    if not cf:
        return ""
    domain = domain.strip().lower()
    pairs = []
    with open(cf, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#HttpOnly_"):
                line = line[len("#HttpOnly_"):]
            if not line or line.startswith("#"):
                continue
            parts = line.split("	")
            if len(parts) < 7:
                continue
            cdomain = parts[0].lstrip(".")
            name, value = parts[5], parts[6]
            if not name or not value:
                continue
            if domain:
                # 只取匹配域或子域的 cookie
                if not (cdomain == domain or cdomain.endswith("." + domain)):
                    continue
            pairs.append(f"{name}={value}")
    return "; ".join(pairs)


def add_cookie(req, domain: str = "") -> None:
    """给 urllib Request 添加目标域的 Cookie 头（若可用）。"""
    try:
        h = cookie_header(domain)
        if h:
            req.add_header("Cookie", h)
    except Exception:  # noqa: BLE001
        pass
