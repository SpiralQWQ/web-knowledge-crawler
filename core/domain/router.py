"""URL 分类路由：把种子/链接判定为 网页/视频/论文/文档/仓库。"""
import os
import re as _re
from urllib.parse import urlparse

_PAPER_HINTS = ("arxiv.org", "export.arxiv.org", "doi.org")
_VIDEO_HINTS = ("douyin.com", "iesdouyin", "bilibili.com", "b23.tv",
                "youtube.com", "youtu.be", "v.qq.com", "ixigua.com")
_DOC_EXTS = (".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".csv")


def classify(url: str) -> str:
    """返回 kind: web / video / paper / doc / repo"""
    low = (url or "").lower().strip()
    if not low:
        return "web"
    if "docs.google.com/document" in low:
        return "doc"  # Google Docs 走 export 导出，不用网页壳
    if any(s in low for s in _PAPER_HINTS):
        return "paper"
    if any(s in low for s in _VIDEO_HINTS):
        return "video"
    m = _re.match(r"https?://(?:www\.)?(github\.com|gitee\.com)/([^/]+/[^/]+)", low)
    if m:
        return "repo"
    if low.endswith(_DOC_EXTS) or ".pdf?" in low:
        return "doc"
    return "web"


def read_seeds(path: str) -> list:
    """读取种子文件：每行一个，# 开头或空行忽略。"""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", errors="replace") as f:  # P2：GBK 种子文件容错
        return [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith("#")]


def sanitize_url(url: str) -> str:
    """M3：持久化前掩 URL userinfo 与敏感查询参数（token/signature/auth...），防凭据写入知识库 .md/.json。"""
    s = str(url or "")
    try:
        s = _re.sub(r"(?i)([a-z][a-z0-9+.-]*://)[^/@\s]+@", r"\1<cred>@", s)
        s = _re.sub(r"(?i)([?&](?:access_token|token|signature|sig|api_key|apikey|key|secret|password|passwd|auth|code)=)[^&\s]+",
                    r"\1<masked>", s)
    except Exception:  # noqa: BLE001
        pass
    return s


def mask_path(p) -> str:
    """日志打码（P10）：遮蔽本地绝对路径；P2：遮蔽 URL userinfo 凭据，防日志分享泄露。"""
    s = str(p or "")
    try:
        from . import config
        for r in (config.BASE, os.path.expanduser("~")):
            s = s.replace(r, "<repo>").replace(r.replace("\\", "/"), "<repo>")
        s = _re.sub(r"(?i)([a-z][a-z0-9+.-]*://)[^/@\s]+@", r"\1<cred>@", s)
        # P2：查询串敏感参数值打码（token/signature/api_key/secret 等），防私有签名链接泄漏
        s = _re.sub(r"(?i)([?&](?:access_token|token|signature|sig|api_key|apikey|key|secret|password|passwd|auth|code)=)[^&\s]+",
                    r"\1<masked>", s)
    except Exception:  # noqa: BLE001
        pass
    return s


def sanitize_domain(url: str) -> str:
    """清洗 netloc 为安全目录名（P1/P2）：禁 .. / 分隔符 / 控制字符，并剥离 userinfo。"""
    netloc = urlparse(url).netloc or "unknown"
    if "@" in netloc:  # 剥离 user:pass@
        netloc = netloc.rsplit("@", 1)[-1]
    netloc = _re.sub(r'[\\/:"<>|\x00-\x1f]+', "_", netloc)
    netloc = netloc.replace("..", "_").strip("._ ")
    # P4：只剥开头 www.（用 ^www\. 正则，防止 mywww.example.com 被误截断）
    netloc = _re.sub(r"^www\.", "", netloc)
    return (netloc or "unknown")[:80]
