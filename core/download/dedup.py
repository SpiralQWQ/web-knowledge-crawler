"""去重：URL 哈希 + 文件指纹（md5/sha256）。"""
import hashlib
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

_TRACKING_KEYS = ("from", "spm", "ref", "spm_id_from", "vd_source", "si",
                  "previous_page")  # P3：B站/YouTube/抖音 分享追踪参数
_VIDEO_HOSTS = ("bilibili.com", "www.bilibili.com", "b23.tv",
                "youtube.com", "www.youtube.com", "youtu.be",
                "douyin.com", "www.douyin.com", "v.douyin.com",
                "iesdouyin.com", "ixigua.com")  # P3：抖音/西瓜 分享链接也剥离跟踪参数


def url_hash(url: str) -> str:
    """URL 规范化后 SHA256（P5：去 utm_/from/spm/ref 追踪参数；P6：t 参数仅限 B站/YouTube；
    P3：fragment 仅视频站剥（锚点/播放参数），SPA/哈希路由页 fragment 是内容，保留防误判重复）。"""
    u = (url or "").strip()
    try:
        parts0 = urlparse(u)
        host = (parts0.hostname or "").lower()
        if host in _VIDEO_HOSTS:
            u = u.split("#", 1)[0]
            parts0 = urlparse(u)
        parts = parts0
        blocked = set(_TRACKING_KEYS)
        if host in _VIDEO_HOSTS:
            blocked.add("t")  # P6：仅视频站剥 t（分享参数），其他站 t 可能是合法 token/时间戳
        qs = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
              if not k.lower().startswith("utm_") and k.lower() not in blocked]
        parts = parts._replace(query=urlencode(qs))
        u = urlunparse(parts)
    except Exception:  # noqa: BLE001
        pass
    return hashlib.sha256(u.encode("utf-8")).hexdigest()


def file_md5(path: str) -> str:
    """文件 MD5，用于下载后防同内容多版本。"""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
