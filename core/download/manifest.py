"""SQLite 元数据库：每条采集记录（源/类型/时间/指纹/路径），幂等去重 + 断点续爬。"""
import os
import sqlite3
import time

from .dedup import url_hash


class Manifest:
    def __init__(self, db_path):
        self.db = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._conn = sqlite3.connect(db_path, timeout=30)
        try:
            self._conn.execute("PRAGMA journal_mode=WAL;")  # 多进程并发读写支持
        except sqlite3.OperationalError:
            pass
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS items(
                url_hash TEXT PRIMARY KEY,
                url TEXT, kind TEXT, platform TEXT, title TEXT,
                file_path TEXT, meta_path TEXT,
                md5 TEXT, size_bytes INTEGER,
                fetched_at TEXT, status TEXT,
                stars INTEGER DEFAULT 0)""")
        # 兼容旧库：补 stars 列
        cols = [c[1] for c in self._conn.execute("PRAGMA table_info(items)").fetchall()]
        if "stars" not in cols:
            self._conn.execute("ALTER TABLE items ADD COLUMN stars INTEGER DEFAULT 0")
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_items_kind ON items(kind)")
        self._conn.commit()

    def exists(self, url: str) -> bool:
        """已成功采集（status='ok'）才视为已存在，失败的允许重试。"""
        row = self._conn.execute(
            "SELECT 1 FROM items WHERE url_hash=? AND status='ok'",
            (url_hash(url),)).fetchone()
        return row is not None

    def get(self, url: str):
        return self._conn.execute(
            "SELECT * FROM items WHERE url_hash=?", (url_hash(url),)).fetchone()

    def find_by_md5(self, md5: str):
        """P6：按内容指纹查已归档记录（防同内容不同链接重复归档）。"""
        if not md5:
            return None
        return self._conn.execute(
            "SELECT * FROM items WHERE md5=? AND status='ok'", (md5,)).fetchone()

    def record(self, url, kind, platform="", title="", file_path="",
               meta_path="", md5="", size_bytes=0, status="ok", stars=0):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        h = url_hash(url)
        # P4：stars=0 的新记录不覆盖已发现的 stars（repo_mirror 镜像成功会以 0 复写 discovered 行）
        if stars == 0:
            old = self._conn.execute(
                "SELECT stars FROM items WHERE url_hash=?", (h,)).fetchone()
            if old and old[0]:
                stars = old[0]
        self._conn.execute(
            "INSERT OR REPLACE INTO items VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (h, url, kind, platform, title, file_path, meta_path,
             md5, size_bytes, now, status, stars))
        self._conn.commit()

    def count(self, kind=None) -> int:
        if kind:
            row = self._conn.execute(
                "SELECT COUNT(*) FROM items WHERE kind=?", (kind,)).fetchone()
        else:
            row = self._conn.execute("SELECT COUNT(*) FROM items").fetchone()
        return row[0] if row else 0

    def stats(self) -> dict:
        rows = self._conn.execute(
            "SELECT kind, COUNT(*) FROM items GROUP BY kind").fetchall()
        return dict(rows)

    def close(self):
        self._conn.close()
