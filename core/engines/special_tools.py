"""专项工具搜索器 — 用成熟下载工具的能力做站内搜索。

yt-dlp 内置 ytsearchN: 前缀，可直接搜 YouTube/抖音/B站 等视频站，
比 Playwright 渲染搜索页更稳。实测 yt-dlp 抓 YouTube/B站 元数据成功。
"""
import asyncio
import json
import os

from .base import BaseSearcher, register
from core.config import BASE, tool


class YtdlpSearchSearcher(BaseSearcher):
    """用 yt-dlp ytsearch 搜索视频站。子类定义 platform 前缀（ytsearch / ytsearchvideo 等）。"""

    search_prefix = "ytsearch"
    domain = ""

    @property
    def name(self) -> str:
        return self.__class__.__dict__.get("name", "")

    @property
    def domain_(self) -> str:
        return self.domain

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        yt = tool("ytdlp")
        if not yt or not os.path.exists(yt):
            return []
        n = min(max_results, 10)
        query = f"{self.search_prefix}{n}:{term}"
        cmd = [yt, "--dump-json", "--no-playlist", "--no-warnings", query]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        try:
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=90)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:  # noqa: BLE001
                pass
            return []
        results = []
        for line in out.decode("utf-8", errors="replace").strip().split("\n"):
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            url = d.get("webpage_url") or d.get("original_url") or ""
            title = d.get("title", "") or ""
            if url:
                results.append({
                    "url": url,
                    "title": title,
                    "type": "video",
                    "summary": "",
                    "original_term": term,
                })
            if len(results) >= max_results:
                break
        return results


@register
class YoutubeYtdlpSearcher(YtdlpSearchSearcher):
    name = "youtube"
    search_prefix = "ytsearch"
    domain = "youtube.com"
