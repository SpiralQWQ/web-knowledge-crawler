"""播客 RSS 音频采集器 — 解析播客站的 RSS feed，提取音频直链。

为什么用 RSS：播客站（Lex Fridman/SE Radio/Linear Digressions 等）的分集音频
不直接在网页里，而是通过 RSS feed 的 <enclosure url="xxx.mp3"> 发布。
从 RSS 拿音频直链比从页面挖可靠得多（实测：Lex 500 集、SE Radio 737 集）。

用法:
    fetcher = PodcastFetcher()
    rss_url = await fetcher.discover_rss("https://www.se-radio.net/")
    eps = await fetcher.parse_rss(rss_url, max_eps=10)   # [{"title","audio_url"}]
"""
import asyncio
import re
import urllib.request
from urllib.parse import urlparse

# 常见 RSS 路径（按优先级探测）
_RSS_PATHS = [
    "/feed/podcast/", "/feed/", "/rss", "/rss/", "/feed.xml",
    "/podcast.xml", "/index.xml", "/category/feed/",
]

# 探测超时
_TIMEOUT = 20

_HEADERS = {"User-Agent": "KnowledgeCollector/1.0 (CC Project)"}


class PodcastFetcher:
    """播客 RSS 采集器。"""

    async def discover_rss(self, entry_url: str) -> str:
        """从入口页找 RSS 地址。**优先返回含音频的 feed**。

        有些站（SE Radio）WordPress 版 feed 无 <enclosure>，音频在 FeedBurner 版，
        所以探测时不仅要"是 RSS"，还要"含音频"才优先。
        """
        candidates = []
        html = await self._fetch_text(entry_url)
        if html:
            # <link rel="alternate" type="application/rss+xml" href="...">
            for pat in (
                r'<link[^>]*type=["\']application/rss\+xml["\'][^>]*href=["\']([^"\']+)["\']',
                r'<link[^>]*href=["\']([^"\']+)["\'][^>]*type=["\']application/rss\+xml["\']',
                r'<link[^>]*rel=["\']alternate["\'][^>]*type=["\']application/rss\+xml["\'][^>]*href=["\']([^"\']+)["\']',
            ):
                for m in re.finditer(pat, html, re.I):
                    candidates.append(self._abs_url(m.group(1), entry_url))
        base = entry_url.rstrip("/")
        for path in _RSS_PATHS:
            candidates.append(base + path)

        # 去重
        seen, cands = set(), []
        for c in candidates:
            if c not in seen:
                seen.add(c)
                cands.append(c)

        audio_feed = ""
        for c in cands:
            data = await self._fetch_text(c)
            if not data:
                continue
            if not re.search(r"<rss|<feed|<channel", data, re.I):
                continue
            if not audio_feed:
                audio_feed = c
            # 含音频才优先返回（enclosure / itunes / 直接音频链接）
            if (re.search(r"<enclosure[^>]*url=", data, re.I)
                    or re.search(r"<itunes:", data, re.I)
                    or re.search(r"\.(?:mp3|m4a|ogg|wav|flac)(?:\?|[\"'\s<])", data, re.I)):
                return c
        return audio_feed

    def _abs_url(self, url: str, base: str) -> str:
        if url.startswith("//"):
            return "https:" + url
        if url.startswith("/"):
            return "https://" + (urlparse(base).netloc or "") + url
        if url.startswith("http"):
            return url
        return base.rstrip("/") + "/" + url

    async def _probe(self, url: str) -> bool:
        """探测 URL 是否是可解析的 RSS。"""
        data = await self._fetch_text(url)
        if not data:
            return False
        return bool(re.search(r"<rss|<feed|<channel", data, re.I))

    async def parse_rss(self, rss_url: str, max_eps: int = 10) -> list[dict]:
        """解析 RSS，提取分集音频直链。

        Returns:
            [{"title": str, "audio_url": str, "url": str, "type": "audio"}, ...]
        """
        data = await self._fetch_text(rss_url)
        if not data:
            return []
        # 每个 <item> 提取 title + enclosure url（enclosure 优先，无则 content:encoded 里的 mp3）
        results = []
        seen = set()
        # 拆分 item
        items = re.findall(r"<item>.*?</item>", data, re.S)
        for it in items:
            title = ""
            tm = re.search(r"<title>(?:<!\[CDATA\[)?([^<\]]+)", it)
            if tm:
                title = tm.group(1).strip()
            # enclosure url
            em = re.search(r'<enclosure[^>]*url=["\']([^"\']+)["\']', it, re.I)
            audio_url = em.group(1) if em else ""
            if not audio_url:
                # 退路1：content:encoded / description 里的 mp3/m4a 直链
                cm = re.search(r'https?://[^"\'\s<>]+\.(?:mp3|m4a|ogg|wav|flac)(?:\?[^"\'\s<>]*)?', it, re.I)
                audio_url = cm.group(0) if cm else ""
            if not audio_url:
                # 退路2：<link> 分集页 URL（音频在页面里，交给下载器按 .mp3/.m4a 扩展名处理）
                lm = re.search(r"<link>(?:<!\[CDATA\[)?([^<\]]+\.(?:mp3|m4a|ogg|wav|flac)(?:/[^<\]]*)?)", it, re.I)
                if not lm:
                    lm = re.search(r"<link>(?:<!\[CDATA\[)?([^<\]]+)", it)
                audio_url = lm.group(1).strip() if lm else ""
            if not audio_url:
                continue
            if audio_url in seen:
                continue
            seen.add(audio_url)
            results.append({
                "title": (title or audio_url.rsplit("/", 1)[-1])[:150],
                "url": audio_url,
                "type": "audio",
                "summary": "",
                "original_term": rss_url,
            })
            if len(results) >= max_eps:
                break
        return results

    async def _fetch_text(self, url: str) -> str:
        """urllib 拉取文本（走 executor，处理 SSL/重定向）。"""
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE  # 部分播客站 SSL 证书异常

        def _fetch():
            req = urllib.request.Request(url, headers=_HEADERS)
            resp = urllib.request.urlopen(req, timeout=_TIMEOUT, context=ctx)
            try:
                return resp.read().decode("utf-8", errors="replace")
            finally:
                resp.close()

        loop = asyncio.get_event_loop()
        for attempt in range(3):  # 网络波动重试（2MB 大 RSS 偶发失败）
            try:
                return await loop.run_in_executor(None, _fetch)
            except Exception:  # noqa: BLE001
                if attempt < 2:
                    await asyncio.sleep(1.5 * (attempt + 1))
        return ""
