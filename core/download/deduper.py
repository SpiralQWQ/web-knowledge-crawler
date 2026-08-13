"""md5/URL 去重器 — 基于 manifest.db(SQLite WAL)的重复检测。

使用方式:
    deduper = Deduper("data/collector.db")
    # 添加结果时自动去重
    deduper.add_result(url, term, site_name)
    if deduper.is_duplicate(url, term):
        skip()
    else:
        download_and_save()
"""
import hashlib
import os


class Deduper:
    """基于 URL+term 组合的 md5 去重器。"""

    def __init__(self, db_path: str = "data/collector.db"):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        import sqlite3
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS crawl_manifest (
                url_hash TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                original_term TEXT NOT NULL,
                site_name TEXT NOT NULL,
                file_type TEXT NOT NULL DEFAULT 'html',
                status TEXT NOT NULL DEFAULT 'pending',  -- pending/saved/failed
                crawled_at REAL,
                file_size INTEGER DEFAULT 0,
                local_path TEXT
            )
        """)
        conn.commit()
        conn.close()

    def is_duplicate(self, url: str, term: str) -> bool:
        """检查 URL+term 组合是否已存在 → True 表示重复。"""
        h = self._hash_url(url)
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        row = conn.execute(
            "SELECT 1 FROM crawl_manifest WHERE url_hash=? AND original_term=?",
            (h, term),
        ).fetchone()
        conn.close()
        return row is not None

    def add_result(self, url: str, term: str, site_name: str,
                   file_type: str = "html", status: str = "pending",
                   file_size: int = 0, local_path: str = ""):
        """注册一条爬取结果到 manifest。"""
        h = self._hash_url(url)
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT OR REPLACE INTO crawl_manifest
               (url_hash, url, original_term, site_name, file_type, status, crawled_at, file_size, local_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (h, url, term, site_name, file_type, status,
             __import__('time').time(), file_size, local_path),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def _hash_url(url: str) -> str:
        """URL → md5 hash (前16位)。"""
        return hashlib.md5(url.strip().encode("utf-8")).hexdigest()[:16]
