"""种子采集 — 从预定义 seed 列表中匹配包含关键词的条目。

第2类站点: 有Cookie但不支持站内搜索
策略: 检查每条 seed URL/title 是否包含当前 term(或中英映射中的任一形式)，
命中则直接下载原始文件。
"""
import os
import re


class SeedFetcher:
    """从种子文件中过滤匹配的条目并下载。"""

    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), "..", "..", "..", "config")

    async def fetch(self, term: str, category: str) -> list[dict]:
        """
        从指定类别的种子文件中查找匹配当前 term 的条目。

        Args:
            term: 专业词汇
            category: "repos" | "docs" | "media"

        Returns:
            [{"url": "...", "title": "...", "type": "..."}]
        """
        cat_file = {
            "repos": "repo_seeds.txt",
            "docs": "doc_seeds.txt",
            "media": "video_keywords_full.txt",
        }[category]
        path = os.path.join(self.config_dir, "seeds", cat_file)
        if not os.path.isfile(path):
            return []
        lines = open(path, encoding="utf-8", errors="replace").readlines()
        # 匹配规则: URL 或 title 中包含 term (不区分大小写)
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        results = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # 格式: URL | Title
            parts = [p.strip() for p in line.split("|")]
            url = parts[0] if len(parts) >= 1 else ""
            title = parts[1] if len(parts) >= 2 else ""
            full_text = f"{url} {title}"
            if pattern.search(full_text):
                ft = self._guess_type(url, title)
                results.append({"url": url, "title": title, "type": ft, "original_term": term})
        return results[:30]

    @staticmethod
    def _guess_type(url: str, title: str) -> str:
        """推测文件类型。"""
        u = (url + " " + title).lower()
        if ".pdf" in u or "pdf" in u:
            return "pdf"
        if ".mp4" in u or "video" in u:
            return "video"
        if ".html" in u or "教程" in u:
            return "html"
        if ".zip" in u or "仓库" in u or "source" in u:
            return "html"  # git clone → html repo page
        return "html"
