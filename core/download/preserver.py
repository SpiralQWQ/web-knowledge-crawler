"""原始文件落盘器 — 按 词/类别/站点/序号子文件夹 保存原始数据。

目录结构:
    知识库/
    └── {词汇}/
        ├── {类别}/                      # 论文/视频/网页/文档/数据集/仓库/课程
        │   └── {站点}/
        │       ├── 00_20260808_标题_2.1M/    # 序号_日期_标题_大小
        │       │   ├── meta.json            # URL/标题/原词等元数据
        │       │   └── 数据文件.pdf         # 实际内容
        │       ├── 01_20260808_标题2_45.2K/
        │       │   ├── meta.json
        │       │   └── 数据文件.html
        │       └── ...
        └── ...

命名规则:
  子文件夹名 = {序号:02d}_{日期YYYYMMDD}_{关键标题}_{大小MB}
  标题: 清洗非法字符 + 提取关键概要(截断)
  大小: MB保留1位小数(如 2.1M)，不足1MB用KB(如 45.2K)
"""
import hashlib
import json
import os
import re
import time

from core.domain.site_category import category_of

# Windows 文件名非法字符替换
_ILLEGAL_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WIN_RESERVED = {"con", "prn", "aux", "nul", "com1", "com2", "com3", "com4",
                 "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3",
                 "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9"}

# URL 扩展名集合（与 downloader._EXT_STRATEGY 对齐，硬依据）
_URL_EXT = {
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".epub", ".mobi",
    ".mp4", ".avi", ".mkv", ".webm", ".mov", ".flv", ".m3u8", ".ts",
    ".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".ico",
    ".zip", ".tar", ".gz", ".tgz", ".7z", ".rar",
    ".html", ".htm", ".shtml",
    ".txt", ".md", ".csv", ".json", ".xml", ".yaml", ".yml", ".log",
    ".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".go", ".rs", ".ipynb",
}


def _safe_filename(name: str, max_len: int = 120) -> str:
    """清理 Windows 非法字符并限制长度。"""
    name = _ILLEGAL_CHARS.sub("_", name or "").strip()
    name = name.replace("  ", " ").strip()
    base, ext = os.path.splitext(name)
    if base.lower() in _WIN_RESERVED:
        base = "_" + base
    if len(base) > max_len:
        base = base[:max_len]
    return base + ext if ext else base


def _short_title(title: str, max_len: int = 30) -> str:
    """提取标题关键概要：去非法字符、压缩空白、截断。"""
    t = _ILLEGAL_CHARS.sub("_", title or "").strip()
    t = re.sub(r'\s+', ' ', t)
    if len(t) > max_len:
        t = t[:max_len]
    return t or "untitled"


def _human_size(size_bytes: int) -> str:
    """字节 → 人类可读大小（MB保留1位，不足1MB用KB）。"""
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024*1024):.1f}M"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f}K"
    return f"{size_bytes}B"


class FilePreserver:
    """原始文件落盘器：词/类别/站点/序号子文件夹。"""

    def __init__(self, root_dir: str = None):
        self.root = root_dir or os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "知识库"))

    def _base_dir(self, term: str, site_name: str, category: str = "") -> str:
        """词/类别/站点 目录。category 为空时按 site_name 推导。"""
        term_safe = _safe_filename(term.replace(" ", "_"), max_len=60)
        site_safe = _safe_filename(site_name, max_len=40)
        cat = category or category_of(site_name)
        d = os.path.join(self.root, term_safe, cat, site_safe)
        os.makedirs(d, exist_ok=True)
        return d

    def _next_seq(self, base_dir: str) -> int:
        """扫描目录已有序号子文件夹，返回下一个序号。"""
        max_seq = -1
        if os.path.isdir(base_dir):
            for name in os.listdir(base_dir):
                m = re.match(r'^(\d{2})_', name)
                if m:
                    max_seq = max(max_seq, int(m.group(1)))
        return max_seq + 1

    def create_item_dir(self, term: str, site_name: str, title: str,
                        size_bytes: int, category: str = "") -> str:
        """创建序号子文件夹，返回其路径。"""
        base = self._base_dir(term, site_name, category)
        seq = self._next_seq(base)
        date = time.strftime("%Y%m%d")
        short = _short_title(title)
        sz = _human_size(size_bytes)
        folder = f"{seq:02d}_{date}_{short}_{sz}"
        item_dir = os.path.join(base, folder)
        os.makedirs(item_dir, exist_ok=True)
        return item_dir

    def save_file(self, url: str, raw_bytes: bytes, term: str,
                  site_name: str, file_type: str, title: str = "",
                  item_dir: str = "", category: str = "") -> str:
        """保存原始文件到序号子文件夹。返回文件路径。

        item_dir 为空时自动创建（兼容单独调用）。
        """
        ext = self._guess_extension(file_type, title, url)
        safe = _safe_filename(title or "data", max_len=40)
        fname = f"{safe}{ext}" if ext else f"{safe}.dat"
        if not item_dir:
            item_dir = self.create_item_dir(term, site_name, title, len(raw_bytes), category)
        # 防重名
        path = os.path.join(item_dir, fname)
        n = 1
        while os.path.exists(path):
            stem, e = os.path.splitext(fname)
            path = os.path.join(item_dir, f"{stem}_{n}{e}")
            n += 1
        with open(path, "wb") as f:
            f.write(raw_bytes)
        # HTML 双份：提取干净正文（去导航/广告）落盘 `_正文.txt`，保留原始 HTML
        if file_type == "html":
            try:
                from trafilatura import extract
                html_text = raw_bytes.decode("utf-8", errors="replace")
                body = extract(html_text)
                if body and len(body.strip()) > 200:
                    body_path = os.path.join(item_dir, f"{os.path.splitext(fname)[0]}_正文.txt")
                    with open(body_path, "w", encoding="utf-8") as f:
                        f.write(body)
            except Exception:  # noqa: BLE001 提取失败不影响原始保存
                pass
        return path

    def save_metadata(self, term: str, site_name: str, file_type: str,
                      url: str, title: str, original_term: str, size: int = 0,
                      item_dir: str = "", category: str = "") -> str:
        """保存元数据 JSON 到序号子文件夹内。

        item_dir 为空时按 title+size 自动定位（兼容单独调用）。
        """
        if not item_dir:
            base = self._base_dir(term, site_name, category)
            seq = self._next_seq(base)
            date = time.strftime("%Y%m%d")
            short = _short_title(title)
            sz = _human_size(size)
            item_dir = os.path.join(base, f"{seq:02d}_{date}_{short}_{sz}")
            os.makedirs(item_dir, exist_ok=True)

        ts = time.time()
        meta = {
            "url": url,
            "title": title,
            "file_type": file_type,
            "original_search_term": original_term,
            "crawled_at": ts,
            "timestamp_str": time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime(ts)),
            "file_size_bytes": size,
            "category": category_of(site_name),
            "site": site_name,
        }
        meta_path = os.path.join(item_dir, "meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        return meta_path

    def _guess_extension(self, file_type: str, title: str, url: str) -> str:
        """根据类型/文件名猜测扩展名。

        URL 扩展名是硬依据（与 downloader 一致）：.jpg 图片存 .jpg，不硬套 .png。
        """
        ft = file_type.lower()
        url_lower = url.lower().split("?")[0]
        # 1) URL 扩展名优先
        fname = url_lower.rstrip("/").rsplit("/", 1)[-1]
        if "." in fname and len(fname) < 80:
            url_ext = os.path.splitext(fname)[1]
            if url_ext in _URL_EXT:
                return url_ext
        # 2) type 兜底
        ext_map = {
            "pdf": ".pdf", "html": ".html", "text": ".txt",
            "doc": ".doc", "docx": ".docx", "ppt": ".ppt",
            "pptx": ".pptx", "video": ".mp4", "audio": ".mp3",
            "image": ".png", "markdown": ".md",
            "archive": ".zip", "json": ".json", "csv": ".csv",
            "xml": ".xml", "yaml": ".yml", "model": ".bin",
            "code": ".py", "markdown": ".md",
        }
        if ft in ext_map:
            return ext_map[ft]
        return ""
