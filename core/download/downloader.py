"""统一下载器 — 按 URL 扩展名 + 类型自动选择下载策略，返回原始字节。

完整类型体系（举一反三，涵盖所有常见格式）：
  文档: pdf/doc/docx/ppt/pptx/xls/xlsx/epub/mobi
  视频: mp4/avi/mkv/webm/mov/flv/m3u8/ts
  音频: mp3/wav/ogg/flac/aac/m4a
  图片: png/jpg/jpeg/gif/svg/webp/bmp/ico
  代码: zip/tar/gz/7z/rar（源码包）
  网页: html/htm/shtml
  文本: txt/md/csv/json/xml/yaml/log
  仓库: repo（git clone 走 crawl_all 分流）

核心原则：URL 扩展名是硬依据 —— 即使搜索器 type 标错，
扩展名命中也会走正确的下载路径。type 只作兜底。
"""
import asyncio
import mimetypes
import os
import subprocess
from typing import Callable

# 完整扩展名 → 下载策略
_EXT_STRATEGY = {
    # 文档
    ".pdf": "pdf", ".doc": "doc", ".docx": "doc", ".ppt": "ppt", ".pptx": "ppt",
    ".xls": "doc", ".xlsx": "doc", ".epub": "doc", ".mobi": "doc", ".azw3": "doc",
    # 视频
    ".mp4": "video", ".avi": "video", ".mkv": "video", ".webm": "video",
    ".mov": "video", ".flv": "video", ".m3u8": "video", ".ts": "video",
    # 音频
    ".mp3": "audio", ".wav": "audio", ".ogg": "audio", ".flac": "audio",
    ".aac": "audio", ".m4a": "audio",
    # 图片
    ".png": "image", ".jpg": "image", ".jpeg": "image", ".gif": "image",
    ".svg": "image", ".webp": "image", ".bmp": "image", ".ico": "image",
    # 代码/压缩包
    ".zip": "archive", ".tar": "archive", ".gz": "archive", ".tgz": "archive",
    ".7z": "archive", ".rar": "archive",
    # 网页
    ".html": "html", ".htm": "html", ".shtml": "html",
    # 文本
    ".txt": "text", ".md": "markdown", ".csv": "text", ".json": "text",
    ".xml": "text", ".yaml": "text", ".yml": "text", ".log": "text",
}

# 类型兜底映射
_TYPE_FALLBACK = {
    "pdf": ".pdf", "html": ".html", "video": ".mp4", "audio": ".mp3",
    "image": ".png", "doc": ".doc", "ppt": ".ppt", "markdown": ".md",
    "text": ".txt", "archive": ".zip",
}

# 已知 JS 动态站域名 → HTML 直接走 Scrapling 渲染（Crawl4AI 只能抓到导航壳）
_JS_DYNAMIC_DOMAINS = ("csdn.net", "juejin.cn", "zhihu.com", "bilibili.com", "xiaohongshu.com")

# YouTube 代理缓存（国内直连不通，需本地 Clash；端口探测一次缓存）
_PROXY_CACHE = {"checked": False, "proxy": ""}


def youtube_proxy(url: str) -> str:
    """YouTube 走本地代理（国内网络）。返回代理地址或空串。

    端口：环境变量 CLASH_PROXY 优先，否则探测 127.0.0.1:7897/7890/7891。
    只对 youtube.com/youtu.be 生效，抖音/B站等直连不受影响。
    """
    if "youtube.com" not in url and "youtu.be" not in url:
        return ""
    if _PROXY_CACHE["checked"]:
        return _PROXY_CACHE["proxy"]
    _PROXY_CACHE["checked"] = True
    env_p = os.environ.get("CLASH_PROXY", "").strip()
    if env_p:
        _PROXY_CACHE["proxy"] = env_p
        return env_p
    import urllib.request
    for port in (7897, 7890, 7891):
        try:
            ph = urllib.request.ProxyHandler({"http": f"http://127.0.0.1:{port}",
                                              "https": f"http://127.0.0.1:{port}"})
            op = urllib.request.build_opener(ph)
            op.open("https://www.youtube.com", timeout=4)
            _PROXY_CACHE["proxy"] = f"http://127.0.0.1:{port}"
            break
        except Exception:  # noqa: BLE001
            continue
    return _PROXY_CACHE["proxy"]


class DownloadResult:
    """下载结果。"""
    def __init__(self, url: str, raw_bytes: bytes | None = None,
                 local_path: str = "", success: bool = True,
                 content_type: str = "", size: int = 0):
        self.url = url
        self.raw_bytes = raw_bytes
        self.local_path = local_path
        self.success = success
        self.content_type = content_type
        self.size = size


class RawDownloader:
    """原始文件下载器。"""

    def __init__(self, user_agent: str = "KnowledgeCollector/1.0"):
        self.user_agent = user_agent
        self.timeout = 120
        self.max_retries = 2

    @staticmethod
    def _infer_extension(url: str) -> str:
        """从 URL 提取扩展名（硬依据）。"""
        path = url.split("?")[0].split("#")[0].lower()
        fname = path.rstrip("/").rsplit("/", 1)[-1]
        if "." in fname and len(fname) < 60:
            ext = os.path.splitext(fname)[1]
            if ext:
                return ext
        return ""

    def _strategy_for(self, url: str, file_type: str) -> str:
        """确定下载策略：URL 扩展名优先，type 兜底。"""
        ext = self._infer_extension(url)
        if ext in _EXT_STRATEGY:
            return _EXT_STRATEGY[ext]
        # type 兜底
        ft = (file_type or "").lower()
        if ft in _TYPE_FALLBACK:
            return ft
        return "generic"

    async def download(self, url: str, file_type: str = "unknown",
                       session=None, stream_progress: bool = False) -> DownloadResult:
        for attempt in range(1 + self.max_retries):
            try:
                result = await self._download_once(url, file_type, stream_progress)
                if result.success:
                    return result
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                else:
                    return result
            except Exception:  # noqa: BLE001
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                else:
                    return DownloadResult(url, success=False, size=0)
        return DownloadResult(url, success=False, size=0)

    async def _download_once(self, url: str, file_type: str,
                             stream_progress: bool = False) -> DownloadResult:
        """按扩展名/类型分流。"""
        strategy = self._strategy_for(url, file_type)

        if strategy == "pdf":
            return await self._download_pdf(url)
        elif strategy == "video":
            return await self._download_video(url, stream_progress)
        elif strategy == "html":
            return await self._download_html(url)
        elif strategy == "image":
            return await self._download_image(url)
        elif strategy == "audio":
            return await self._download_audio(url)
        elif strategy in ("doc", "ppt", "archive"):
            return await self._download_binary(url)
        elif strategy == "markdown":
            return await self._download_markdown(url)
        elif strategy == "text":
            return await self._download_text(url)
        else:
            return await self._download_generic(url)

    async def _fetch_url(self, url: str) -> tuple[bytes, str]:
        """urllib 拉取（走 executor）。"""
        import urllib.request

        def _fetch():
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            resp = urllib.request.urlopen(req, timeout=self.timeout)
            try:
                return resp.read(), resp.headers.get("Content-Type", "")
            finally:
                resp.close()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _fetch)

    async def _download_pdf(self, url: str) -> DownloadResult:
        raw, ct = await self._fetch_url(url)
        return DownloadResult(url, raw_bytes=raw, success=True, content_type=ct, size=len(raw))

    async def _download_binary(self, url: str) -> DownloadResult:
        """二进制文件（doc/ppt/zip等）：HTTP 原始字节。"""
        raw, ct = await self._fetch_url(url)
        return DownloadResult(url, raw_bytes=raw, success=True, content_type=ct, size=len(raw))

    async def _download_text(self, url: str) -> DownloadResult:
        raw, ct = await self._fetch_url(url)
        text = raw.decode("utf-8", errors="replace")
        return DownloadResult(url, raw_bytes=text.encode("utf-8"), success=True,
                              content_type="text/plain", size=len(text))

    async def _download_markdown(self, url: str) -> DownloadResult:
        raw, ct = await self._fetch_url(url)
        text = raw.decode("utf-8", errors="replace")
        return DownloadResult(url, raw_bytes=text.encode("utf-8"), success=True,
                              content_type="text/markdown", size=len(text))

    async def _download_video(self, url: str, stream_progress: bool = False) -> DownloadResult:
        """视频用 yt-dlp 下载原始文件。带 cookie（硬性规则：有 cookie 必用）。

        stream_progress=True：stdout 实时透传（yt-dlp 进度条可见，参考 video_tools run_stream）。
        """
        from core.config import tool
        yt = tool("ytdlp")
        if not yt:
            return await self._download_binary(url)
        import tempfile
        tmp = tempfile.mkdtemp()
        cmd = [yt, "--no-playlist", "-o", os.path.join(tmp, "%(title).40s_%(id)s.%(ext)s")]
        # 注入登录 cookie（抖音/B站等需 cookie 的视频站）；YouTube 不带（过期cookie反害解析）
        try:
            from core.auth.cookie_util import _cookie_file
            cf = _cookie_file()
            if ("youtube.com" not in url and "youtu.be" not in url) and cf and os.path.exists(cf):
                cmd += ["--cookies", cf]
        except Exception:  # noqa: BLE001
            pass
        # YouTube 走本地代理（国内直连不通）
        px = youtube_proxy(url)
        if px:
            cmd += ["--proxy", px]
        cmd += [url]
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")  # 防中文乱码
        if stream_progress:
            # 精简进度：隐藏 [generic]/[Douyin] 解析日志，只留干净百分比。
            # 关键：stderr 透传（yt-dlp 进度默认写 stderr，PIPE 捕获会吞掉）+ 纯模板无前缀
            # TTY 下 yt-dlp 用 \r 单行原地刷新，非 TTY 逐行输出
            cmd += ["--no-warnings",
                    "--progress-template", "下载 %(progress._percent_str)s"]
        # stdout 透传（进度条可见）vs 捕获（crawl_all 静默）；进度模式下 stderr 也透传防吞
        proc = await asyncio.create_subprocess_exec(
            *cmd, env=env,
            stdout=None if stream_progress else asyncio.subprocess.PIPE,
            stderr=None if stream_progress else asyncio.subprocess.PIPE)
        try:
            await asyncio.wait_for(proc.wait(), timeout=600)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:  # noqa: BLE001
                pass
            return DownloadResult(url, success=False, size=0)
        files = [f for f in os.listdir(tmp) if os.path.isfile(os.path.join(tmp, f))
                 and not f.endswith(".part")]
        if files:
            # 选最大文件：避免 files[0] 误选到 .m3u8 清单等小文件
            fpath = os.path.join(tmp, max(files, key=lambda f: os.path.getsize(os.path.join(tmp, f))))
            raw = open(fpath, "rb").read()
            os.remove(fpath)
            os.rmdir(tmp)
            return DownloadResult(url, raw_bytes=raw, success=True,
                                  content_type="video/mp4", size=len(raw))
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
        return DownloadResult(url, success=False, size=0)

    async def _download_html(self, url: str) -> DownloadResult:
        """HTML 抓取回退链：
        - 已知 JS 动态站 → Scrapling(dynamic) → StealthyFetcher → patchright(带cookie)
        - 其他站 → Crawl4AI → Scrapling(dynamic) → StealthyFetcher → patchright
        """
        if any(d in url for d in _JS_DYNAMIC_DOMAINS):
            result = await self._download_html_scrapling(url, "dynamic")
            if result.success and result.size > 500:
                return result
            result = await self._download_html_scrapling(url, "stealth")
            if result.success and result.size > 500:
                return result
            return await self._download_html_patchright(url)
        # 非 JS 站
        result = await self._download_html_crawl4ai(url)
        if result.success and result.size > 500:
            return result
        result = await self._download_html_scrapling(url, "dynamic")
        if result.success and result.size > 500:
            return result
        result = await self._download_html_scrapling(url, "stealth")
        if result.success and result.size > 500:
            return result
        return await self._download_html_patchright(url)

    async def _download_html_patchright(self, url: str) -> DownloadResult:
        """用 patchright 隐形 Chromium 渲染（最高反爬级，带 cookie 注入）。"""
        from core.config import BASE, tool
        py = tool("patchright_py")
        if not py or not os.path.exists(py):
            return DownloadResult(url, success=False, size=0)
        helper = os.path.join(BASE, "core", "bridges", "patchright_helper.py")
        cmd = [py, helper, url]
        from core.auth.cookie_util import _cookie_file
        cookie_file = _cookie_file()
        if cookie_file and os.path.exists(cookie_file):
            cmd.append(cookie_file)
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env)
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout=90)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:  # noqa: BLE001
                pass
            return DownloadResult(url, success=False, size=0)
        import json as _json
        data = None
        for line in reversed(out.decode("utf-8", errors="replace").strip().split("\n")):
            if line.strip().startswith("{"):
                try:
                    data = _json.loads(line)
                    break
                except Exception:  # noqa: BLE001
                    continue
        if data and data.get("success") and data.get("html"):
            html = data["html"]
            return DownloadResult(url, raw_bytes=html.encode("utf-8"), success=True,
                                  content_type="text/html", size=len(html))
        return DownloadResult(url, success=False, size=0)

    async def _download_html_crawl4ai(self, url: str) -> DownloadResult:
        """HTML 用 Crawl4AI 抓取（复用 crawl_helper + cookie）。"""
        from core.config import BASE, tool
        py = tool("crawl4ai_py")
        if not py or not os.path.exists(py):
            return await self._download_binary(url)
        helper = os.path.join(BASE, "core", "bridges", "crawl_helper.py")
        cmd = [py, helper, url]
        from core.auth.cookie_util import _cookie_file
        cookie_file = _cookie_file()
        if cookie_file and os.path.exists(cookie_file):
            cmd.append(cookie_file)
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env)
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout=120)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:  # noqa: BLE001
                pass
            return DownloadResult(url, success=False, size=0)
        import json as _json
        data = None
        for line in reversed(out.decode("utf-8", errors="replace").strip().split("\n")):
            if line.strip().startswith("{"):
                try:
                    data = _json.loads(line)
                    break
                except Exception:  # noqa: BLE001
                    continue
        if data and data.get("success") and data.get("markdown"):
            md = data["markdown"]
            return DownloadResult(url, raw_bytes=md.encode("utf-8"), success=True,
                                  content_type="text/markdown", size=len(md))
        return DownloadResult(url, success=False, size=0)

    async def _download_html_scrapling(self, url: str, mode: str = "dynamic") -> DownloadResult:
        """用 Scrapling 渲染 HTML（JS 动态站攻坚层，走 scrapling_helper 子进程）。
        mode: dynamic=DynamicFetcher(默认) / stealth=StealthyFetcher(过 Cloudflare)。"""
        from core.config import BASE, tool
        py = tool("scrapling_py")
        if not py or not os.path.exists(py):
            return DownloadResult(url, success=False, size=0)
        helper = os.path.join(BASE, "core", "bridges", "scrapling_helper.py")
        cmd = [py, helper, url, "--mode", mode, "--timeout", "45"]
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env)
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout=90)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:  # noqa: BLE001
                pass
            return DownloadResult(url, success=False, size=0)
        import json as _json
        data = None
        for line in reversed(out.decode("utf-8", errors="replace").strip().split("\n")):
            if line.strip().startswith("{"):
                try:
                    data = _json.loads(line)
                    break
                except Exception:  # noqa: BLE001
                    continue
        if data and data.get("success") and data.get("html"):
            html = data["html"]
            return DownloadResult(url, raw_bytes=html.encode("utf-8"), success=True,
                                  content_type="text/html", size=len(html))
        return DownloadResult(url, success=False, size=0)

    async def _download_image(self, url: str) -> DownloadResult:
        return await self._download_binary(url)

    async def _download_audio(self, url: str) -> DownloadResult:
        """音频下载：yt-dlp 优先（SoundCloud 等页面链接），HTTP 兜底（直链 .mp3）。

        播客 RSS 常给出 SoundCloud 等页面 URL，直接 HTTP 拿不到文件，
        yt-dlp 能解析出真实音频流。
        """
        from core.config import tool
        yt = tool("ytdlp")
        if yt:
            import tempfile, shutil
            tmp = tempfile.mkdtemp()
            cmd = [yt, "--no-playlist", "-x",
                   "-o", os.path.join(tmp, "%(title).40s_%(id)s.%(ext)s"), url]
            px = youtube_proxy(url)
            if px:
                cmd = cmd[:3] + ["--proxy", px] + cmd[3:]
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            try:
                await asyncio.wait_for(proc.wait(), timeout=600)
            except asyncio.TimeoutError:
                try:
                    proc.kill()
                except Exception:  # noqa: BLE001
                    pass
                shutil.rmtree(tmp, ignore_errors=True)
                return await self._download_binary(url)
            files = [f for f in os.listdir(tmp) if os.path.isfile(os.path.join(tmp, f))
                     and not f.endswith(".part")]
            if files:
                # 选最大文件：避免 files[0] 误选到 .m3u8 清单等小文件
                fpath = os.path.join(tmp, max(files, key=lambda f: os.path.getsize(os.path.join(tmp, f))))
                raw = open(fpath, "rb").read()
                os.remove(fpath)
                os.rmdir(tmp)
                return DownloadResult(url, raw_bytes=raw, success=True,
                                      content_type="audio/mpeg", size=len(raw))
            shutil.rmtree(tmp, ignore_errors=True)
        # 兜底：直链 .mp3 等
        return await self._download_binary(url)

    async def _download_generic(self, url: str) -> DownloadResult:
        """未知类型：HTTP 原始字节。"""
        raw, ct = await self._fetch_url(url)
        return DownloadResult(url, raw_bytes=raw, success=True, content_type=ct, size=len(raw))
