"""资源扩展器 — 一个页面/结果 → 多种类型的资源候选。

核心思想：**不要局限单一类型**。一个网页里嵌着什么就挖什么：
  markdown 图片  ![alt](url)     → type=image
  markdown 链接  [text](url.pdf) → type=pdf/doc/ppt/audio/archive/code/text

配合 yt-dlp --write-thumbnail/--write-description 的视频侧扩展，
实现"一个结果 → 图片+视频+文本+文档+音频"的全类型采集。
"""
import os
import re
from urllib.parse import urljoin, urlparse

# URL 扩展名 → 资源类型（与 downloader._EXT_STRATEGY 对齐）
_EXT_TYPE = {
    ".pdf": "pdf", ".epub": "doc", ".mobi": "doc",
    ".doc": "doc", ".docx": "doc", ".xls": "doc", ".xlsx": "doc",
    ".ppt": "ppt", ".pptx": "ppt",
    ".mp3": "audio", ".wav": "audio", ".ogg": "audio", ".flac": "audio",
    ".m4a": "audio", ".aac": "audio",
    ".png": "image", ".jpg": "image", ".jpeg": "image", ".gif": "image",
    ".webp": "image", ".bmp": "image", ".ico": "image", ".svg": "image",
    ".zip": "archive", ".tar": "archive", ".gz": "archive", ".tgz": "archive",
    ".7z": "archive", ".rar": "archive",
    ".mp4": "video", ".mkv": "video", ".webm": "video", ".mov": "video",
    ".flv": "video", ".m3u8": "video", ".ts": "video",
    ".csv": "text", ".json": "text", ".xml": "text", ".txt": "text", ".log": "text",
    ".md": "markdown",
    ".py": "code", ".js": "code", ".ts": "code", ".java": "code",
    ".c": "code", ".cpp": "code", ".h": "code", ".go": "code", ".rs": "code",
    ".ipynb": "code",
}

# 图片噪音：图标/logo/占位/广告等不下载
_IMG_NOISE = (
    "logo", "icon", "avatar", "emoji", "spacer", "pixel", "1x1",
    "favicon", "loading", "placeholder", "sprite", "ad-", "ad_",
    "banner-", "banner_",
)
# 链接噪音：登录/评论区/标签等非资源路径
_LINK_NOISE = (
    "javascript:", "mailto:", "tel:", "#comment", "#reply", "/tags/",
    "/authors/", "/category/", "/login", "/signin", "/register",
    "/search?", "utm_source", "utm_medium",
)


def _ext_of(url: str) -> str:
    """URL 扩展名（硬依据）。"""
    path = url.split("?")[0].split("#")[0].lower()
    fname = path.rstrip("/").rsplit("/", 1)[-1]
    if "." in fname and len(fname) < 80:
        return os.path.splitext(fname)[1]
    return ""


def _abs(url: str, base: str) -> str:
    """相对/协议相对 URL → 绝对 URL。"""
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/"):
        return "https://" + (urlparse(base).netloc or "") + url
    if url.startswith("http"):
        return url
    return urljoin(base, url)


def _mk(url: str, title: str, rtype: str, term: str) -> dict:
    return {"url": url, "title": title, "type": rtype,
            "summary": "", "original_term": term}


def image_resources_from_markdown(md: str, base_url: str, term: str,
                                  max_n: int = 6) -> list[dict]:
    """挖出 markdown 里的图片 → type=image。"""
    results, seen = [], set()
    idx = 0
    for m in re.finditer(r"!\[[^\]]*\]\(([^)\s]+)", md or ""):
        raw = m.group(1).strip()
        url = _abs(raw, base_url)
        low = url.lower()
        if not url.startswith("http") or low.startswith("data:"):
            continue
        if any(n in low for n in _IMG_NOISE):
            continue
        ext = _ext_of(url)
        if ext and ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif",
                               ".bmp", ".svg", ".ico"):
            continue  # 扩展名明确不是图片 → 跳过
        if url in seen:
            continue
        seen.add(url)
        idx += 1
        results.append(_mk(url, f"图片{idx:02d}", "image", term))
        if len(results) >= max_n:
            break
    return results


def file_resources_from_markdown(md: str, base_url: str, term: str,
                                 max_n: int = 6) -> list[dict]:
    """挖出 markdown 里指向真实文件的链接 → pdf/doc/ppt/audio/archive/code/text。"""
    results, seen = [], set()
    idx = 0
    for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)", md or ""):
        raw = m.group(1).strip()
        url = _abs(raw, base_url)
        low = url.lower()
        if not url.startswith("http"):
            continue
        if any(n in low for n in _LINK_NOISE):
            continue
        ext = _ext_of(url)
        rtype = _EXT_TYPE.get(ext)
        # 图片走 image 通道，视频走搜索层 yt-dlp，md 即网页正文本身
        if not rtype or rtype in ("image", "video", "markdown"):
            continue
        if url in seen:
            continue
        seen.add(url)
        idx += 1
        results.append(_mk(url, f"{rtype}资源{idx:02d}", rtype, term))
        if len(results) >= max_n:
            break
    return results


def extract_multi(md: str, base_url: str, term: str,
                  max_images: int = 6, max_files: int = 6) -> list[dict]:
    """综合扩展：图片 + 文件。"""
    out = image_resources_from_markdown(md, base_url, term, max_images)
    out += file_resources_from_markdown(md, base_url, term, max_files)
    # 全局去重（同 URL 可能在两通道都出现）
    seen, deduped = set(), []
    for r in out:
        if r["url"] in seen:
            continue
        seen.add(r["url"])
        deduped.append(r)
    return deduped
