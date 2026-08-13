"""静态资源采集 — 第3类：无搜索功能、无Cookie的已知URL直接下载。

策略: 使用预定义的 `static_pdfs.txt` / `static_docs.txt` 种子文件，
按 term 匹配条目 → HTTP GET 原始文件。

注意: 这些站不需要登录（完全公开），也没有搜索框，只能下载已知URL。
"""
import re


class StaticFetcher:
    """从已知URL种子文件中下载原始文件。"""

    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or ""

    async def fetch(self, term: str) -> list[dict]:
        """
        匹配并返回可下载的条目。

        Returns:
            [{"url": "...", "title": "...", "type": "pdf"|"html"}]
        """
        results = []
        # 从 static_pdfs.txt 匹配
        pdf_path = f"{self.config_dir}/config/seeds/static_pdfs.txt"
        if __import__('os').path.isfile(pdf_path):
            lines = open(pdf_path, encoding="utf-8").readlines()
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [p.strip() for p in line.split("|")]
                url = parts[0]
                title = parts[1] if len(parts) > 1 else url.split("/")[-1]
                full_text = f"{url} {title}".lower()
                if pattern.search(full_text.lower()):
                    ft = "pdf" if ".pdf" in url.lower() else "html"
                    results.append({"url": url, "title": title, "type": ft, "original_term": term})

        return results[:50]
