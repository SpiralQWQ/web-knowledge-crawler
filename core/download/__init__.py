# -*- coding: utf-8 -*-
"""下载执行层：指定爬取/连根爬/预览/进度（download_single/download_chain 等）。

从旧版引导脚本抽离（架构重构 T12，见 docs/directory-contract.md）。
依赖：core.auth（登录）+ core.download（下载器/落盘/cookie）+ core.config。
"""
import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile

from core.config import tool
from core.auth.cookie_util import _cookie_file
from core.download.downloader import RawDownloader, youtube_proxy
from core.download.preserver import FilePreserver
from core.auth import ensure_login

# 仓库根
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_SPEED_PARAMS = {
    "fast": {"concurrency": 4, "delay": 0.5},
    "normal": {"concurrency": 3, "delay": 1.0},
    "full": {"concurrency": 2, "delay": 2.0},
}


def download_single(url: str, site: str, speed: str = "normal",
                    out_dir: str = "", chain: bool = False) -> str:
    """指定爬取：先展示内容信息，再分阶段下载 → 落盘（默认 知识库/指定爬取/，可自定义）。"""
    import asyncio
    from core.download.downloader import RawDownloader
    from core.download.preserver import FilePreserver
    from core.config import tool
    ft = "video" if site in ("douyin", "bilibili", "youtube") else "html"
    out_root = out_dir or os.path.join(BASE, "知识库", "指定爬取")
    # 登录检查：需登录站（抖音/B站等）无 cookie 时自动引导登录
    if not ensure_login(site):
        return ""
    # [1/3] 先解析内容信息（标题/时长/作者），给用户预览
    info = _probe_url_info(url, site)
    if info:
        print(f"\n  📄 内容预览：{info}")
    # [2/3] 下载（flush 确保"下载中"先显示，再开始下载出进度条）
    print(f"  ⏳ [2/3] 下载中（类型：{ft}）→ {out_root}", flush=True)
    try:
        d = RawDownloader()
        dr = asyncio.run(d.download(url, file_type=ft, stream_progress=True))
        if not dr.success or not dr.raw_bytes:
            print(f"  ⚠ 下载失败：{getattr(dr, 'error', '未知')}")
            return ""
        # [3/3] 保存（标题优先用预览解析的）
        title = (info or "").split("|")[0].strip() if info else (getattr(dr, "title", "") or "")
        p = FilePreserver(root_dir=out_root)
        local = p.save_file(url, dr.raw_bytes, "指定爬取", site, ft, title)
        print(f"\n  ✅ [3/3] 下载完成")
        # 显示存储类型 + 存储规范
        size = f"{len(dr.raw_bytes)/1024/1024:.1f}MB" if len(dr.raw_bytes) > 1024*1024 else f"{len(dr.raw_bytes)/1024:.0f}KB"
        print(f"  存储类型：{'视频' if ft=='video' else '网页' if ft=='html' else ft}")
        print(f"  存储规范：{os.path.basename(os.path.dirname(local))}/")
        print(f"           ├─ {os.path.basename(local)}（{size}）← 原始文件")
        print(f"           └─ meta.json（URL/标题/来源/时间）")
        print(f"  已保存：{local}")
        # 连根爬：本视频下完，解析作者主页，再抓该作者前 N 个视频
        if chain:
            n = input("\n  🔗 该作者再抓几个视频？（回车=10）：").strip()
            n = int(n) if n.isdigit() and 1 <= int(n) <= 50 else 10
            download_chain(url, site, out_root, n)
        return local
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ 下载异常：{e}")
        return ""


def _probe_url_info(url: str, site: str) -> str:
    """用 yt-dlp 解析视频信息（标题/时长），供下载前预览。非视频站返回空。"""
    if site not in ("douyin", "bilibili", "youtube"):
        return ""
    try:
        from core.config import tool
        yt = tool("ytdlp")
        if not yt:
            return ""
        from core.auth.cookie_util import _cookie_file
        import subprocess
        cmd = [yt, "--no-playlist", "--skip-download",
               "--print", "%(title)s | %(duration_string)s | %(uploader)s", url]
        cf = _cookie_file()
        if site != "youtube" and cf and os.path.exists(cf):  # YouTube 带过期cookie会解析失败
            cmd.insert(1, "--cookies")
            cmd.insert(2, cf)
        # YouTube 走本地代理（国内直连不通）
        if site == "youtube":
            from core.download.downloader import youtube_proxy
            px = youtube_proxy(url)
            if px:
                cmd = cmd[:-1] + ["--proxy", px, cmd[-1]]  # 必须插 URL 前，yt-dlp 不认 URL 后参数
        # 防乱码：子进程用 UTF-8 输出（参考 video_tools run）
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        r = subprocess.run(cmd, capture_output=True, timeout=30,
                           encoding="utf-8", errors="replace", env=env)
        line = (r.stdout or "").strip().split("\n")[-1]
        return line if line and "ERROR" not in line else ""
    except Exception:  # noqa: BLE001
        return ""


def _probe_author_url(url: str, site: str) -> str:
    """用 yt-dlp 解析作者主页 URL（连根爬用）。解析不到返回空字符串。"""
    try:
        from core.config import tool
        yt = tool("ytdlp")
        if not yt:
            return ""
        from core.auth.cookie_util import _cookie_file
        import subprocess
        cf = _cookie_file()
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        # 1) 优先 uploader_url（作者主页直链）
        cmd = [yt, "--no-playlist", "--skip-download", "--print", "%(uploader_url)s", url]
        if site != "youtube" and cf and os.path.exists(cf):  # YouTube 带过期cookie会解析失败
            cmd[1:1] = ["--cookies", cf]
        if site == "youtube":
            from core.download.downloader import youtube_proxy
            px = youtube_proxy(url)
            if px:
                cmd = cmd[:-1] + ["--proxy", px, cmd[-1]]  # 必须插 URL 前，yt-dlp 不认 URL 后参数
        r = subprocess.run(cmd, capture_output=True, timeout=30,
                           encoding="utf-8", errors="replace", env=env)
        up = (r.stdout or "").strip().splitlines()
        if up and up[-1].strip().startswith("http"):
            return up[-1].strip()
        # 2) 兜底：uploader_id 拼主页（抖音/B站/youtube）
        cmd = [yt, "--no-playlist", "--skip-download", "--print", "%(uploader_id)s", url]
        if site != "youtube" and cf and os.path.exists(cf):  # YouTube 带过期cookie会解析失败
            cmd[1:1] = ["--cookies", cf]
        if site == "youtube":
            from core.download.downloader import youtube_proxy
            px = youtube_proxy(url)
            if px:
                cmd = cmd[:-1] + ["--proxy", px, cmd[-1]]  # 必须插 URL 前，yt-dlp 不认 URL 后参数
        r = subprocess.run(cmd, capture_output=True, timeout=30,
                           encoding="utf-8", errors="replace", env=env)
        uid = (r.stdout or "").strip().splitlines()
        uid = uid[-1].strip() if uid else ""
        if not uid or uid.lower() in ("none", "unknown"):
            return ""
        if site == "douyin":
            return f"https://www.douyin.com/user/{uid}"
        if site == "bilibili":
            return f"https://space.bilibili.com/{uid}/video"
        if site == "youtube":
            return f"https://www.youtube.com/channel/{uid}"
        return ""
    except Exception:  # noqa: BLE001
        return ""


def _browser_collect_author(content_url: str, site: str, n: int) -> list:
    """借调试浏览器收集作者系列内容链接（抖音/小红书/微博）。

    yt-dlp 不支持这些站作者主页；Scrapling 渲染主页被登录墙挡。
    playwright 子进程：内容页 → 提取作者真实主页 → 主页滚动 → 收集内容链接。
    """
    import json, subprocess
    from core.config import tool
    py = tool("playwright_py")
    if not py or not os.path.exists(py):
        print("  ⚠ 没有 playwright 环境，无法收集作者内容链接")
        return []
    helper = os.path.join(BASE, "core", "bridges", "douyin_chain_helper.py")
    if not os.path.exists(helper):
        print("  ⚠ 缺少辅助脚本，无法收集作者内容链接")
        return []
    try:
        r = subprocess.run([py, helper, content_url, str(n), site],
                           capture_output=True, timeout=180, encoding="utf-8", errors="replace",
                           env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"))
        out = (r.stdout or "").strip().splitlines()
        if not out:
            return []
        data = json.loads(out[-1])
        if data.get("author_url"):
            print(f"  🔗 作者主页：{data['author_url']}")
        if data.get("error"):
            print(f"  ⚠ {data['error']}")
        return data.get("content_urls", [])
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ 作者内容收集异常：{e}")
        return []


def _download_video_list(content_urls: list, site: str, out_root: str) -> int:
    """逐个下载作者系列内容 → 落盘（遵守存储规范），返回成功数。

    小红书/微博图文内容：视频下载失败时回退下载页面 HTML。
    """
    import asyncio
    from core.download.downloader import RawDownloader
    from core.download.preserver import FilePreserver
    p = FilePreserver(root_dir=out_root)
    saved = 0
    for i, vu in enumerate(content_urls, 1):
        info = _probe_url_info(vu, site)
        title = (info or "").split("|")[0].strip() if info else ""
        print(f"  🔗 [{i}/{len(content_urls)}] 下载：{title or vu} …", flush=True)
        try:
            d = RawDownloader()
            dr = asyncio.run(d.download(vu, file_type="video", stream_progress=True))
            if not dr.success or not dr.raw_bytes:
                # 图文兜底（小红书/微博笔记）：下载页面 HTML
                dr2 = asyncio.run(d.download(vu, file_type="html", stream_progress=False))
                if dr2.success and dr2.raw_bytes:
                    p.save_file(vu, dr2.raw_bytes, "指定爬取", site, "html", title)
                    saved += 1
                    continue
                print("    ⚠ 下载失败，跳过")
                continue
            p.save_file(vu, dr.raw_bytes, "指定爬取", site, "video", title)
            saved += 1
        except Exception as e:  # noqa: BLE001
            print(f"    ⚠ 下载异常：{e}")
    return saved


def download_chain(url: str, site: str, out_root: str, n: int = 10) -> int:
    """连根爬：解析作者主页，下载该作者前 n 个视频 → 落盘（遵守存储规范）。

    诚实降级：yt-dlp 解析/下载失败时明确提示，不影响本视频已下载。
    """
    import tempfile, shutil, subprocess as _sp
    from core.config import tool
    from core.auth.cookie_util import _cookie_file
    from core.download.preserver import FilePreserver
    # 抖音/小红书/微博：借浏览器从内容页收集作者系列（yt-dlp 不支持这些站主页）
    if site in ("douyin", "xiaohongshu", "weibo"):
        _kind = "视频" if site == "douyin" else "内容"
        print(f"  🔗 正在收集该作者前 {n} 个{_kind}…")
        vids = _browser_collect_author(url, site, n)
        if not vids:
            print(f"  ⚠ 没能收集到该作者{_kind}（主页需登录/滚动加载，本次 0 个）")
            return 0
        print(f"  🔗 收集到 {len(vids)} 个{_kind}，逐个下载…")
        return _download_video_list(vids, site, out_root)
    yt = tool("ytdlp")
    if not yt:
        print("  ⚠ 没有 yt-dlp，连根跳过")
        return 0
    author_url = _probe_author_url(url, site)
    if not author_url:
        print("  ⚠ 没能解析出作者主页，连根跳过（本视频已下载）")
        return 0
    print(f"  🔗 解析到作者主页：{author_url}")
    print(f"  🔗 正在下载该作者前 {n} 个视频…")
    # 其他站（B站/youtube）：yt-dlp 直接下载作者主页前 N 个
    tmp = tempfile.mkdtemp(prefix="chain_")
    cmd = [yt, "--no-warnings", "--playlist-items", f"1:{n}",
           "-o", os.path.join(tmp, "%(title).40s_%(id)s.%(ext)s"), author_url]
    cf = _cookie_file()
    if site != "youtube" and cf and os.path.exists(cf):  # YouTube 带过期cookie会解析失败
        cmd[1:1] = ["--cookies", cf]
    # YouTube 走本地代理（国内直连不通）
    if site == "youtube":
        from core.download.downloader import youtube_proxy
        px = youtube_proxy(author_url)
        if px:
            cmd = cmd[:-1] + ["--proxy", px, cmd[-1]]  # 必须插 URL 前，yt-dlp 不认 URL 后参数
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    try:
        _sp.run(cmd, timeout=900, env=env)
    except Exception as e:  # noqa: BLE001
        # 中途出错/超时：已下载到的文件保留（不 rmtree），仍尝试落盘部分成果
        print(f"  ⚠ 连根下载中途出错（{e}），尝试保存已下载的部分...")
    p = FilePreserver(root_dir=out_root)
    saved = 0
    for f in os.listdir(tmp):
        fp = os.path.join(tmp, f)
        if not os.path.isfile(fp) or f.endswith(".part"):
            continue
        try:
            raw = open(fp, "rb").read()
            title = os.path.splitext(f)[0].rsplit("_", 1)[0]  # 文件名 标题_视频ID.ext → 标题
            local = p.save_file(author_url, raw, "指定爬取", site, "video", title)
            saved += 1
        except Exception:  # noqa: BLE001
            pass
    shutil.rmtree(tmp, ignore_errors=True)
    if saved:
        print(f"  ✅ 连根完成：多下载 {saved} 个该作者视频 → {out_root}")
    else:
        print("  ⚠ 连根没下到更多视频（该站连根可能暂不完整支持，本视频已下载）")
    return saved
