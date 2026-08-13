"""三分类采集调度器 — 统一入口。

调度策略: 混合模式(3~5个词并行 × 站内串行)
每个词的每个站根据类型自动选择:
- type=search → search_engine.BaseSearcher.search()
- type=seed   → shared.seed_fetcher.SeedFetcher.fetch()
- type=static → shared.static_fetcher.StaticFetcher.fetch()

运行方式:
    python tools/crawl_all.py                              # 默认全部词汇+站点
    python tools/crawl_all.py --terms vocab_terms.txt      # 指定词汇文件
    python tools/crawl_all.py --category search            # 只跑第1类
    python tools/crawl_all.py --concurrency 3              # 并发数(1~10)
"""
import asyncio
import logging
import os
import sys
import argparse
import time

# 加入仓库根到 path
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

def _setup_stdout():
    """控制台用系统编码(WriteConsoleW自动处理中文)，管道用UTF-8。"""
    try:
        if not sys.stdout.isatty():
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if not sys.stderr.isatty():
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


from core.download.scheduler import MixedScheduler, CrawlStats
from core.download.deduper import Deduper
from core.filter.noise_filter import quick_filter, merge_and_filter
from core.download.downloader import RawDownloader
from core.download.preserver import FilePreserver
from core.download.seed_fetcher import SeedFetcher
from core.download.static_fetcher import StaticFetcher


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("crawl_all")


def load_terms(path: str = "config/seeds/vocab_terms_full.txt") -> list[str]:
    """加载词汇列表。"""
    full_path = os.path.join(BASE, path)
    terms = []
    for line in open(full_path, encoding="utf-8", errors="replace"):
        t = line.strip().split("|")[0].strip() if "|" in line else line.strip()
        if t and not t.startswith("#"):
            terms.append(t)
    return terms[:2740]  # 限制最多2740个


# ============================================================
# 已确认爬不动的站（全站修复战役 F 系列 + 拯救战役排查结论）
# 说明：google_scholar/medium/oschina/paperswithcode/aclanthology
#      已通过 OpenAlex/RSS/HF API/本地XML 救活（拯救战役 C1-C5），移出禁用
# 详见项目调研文档（全站方法总表 / 高价值站拯救）
_DISABLED_SITES = {
    # 反爬极强，dynamic/stealth 均被拒
    "hackernoon",       # 反爬极强(dynamic/stealth都拒)
    "qbitai",           # 量子位 403 WAF（CDP 也过不了）
    # 搜索页只渲染导航/无结果
    "lobste.rs",        # 搜索只返回评论页，无文章
    "datawhale",        # 搜索无结果
    "connectedpapers",  # 搜索页无结果
    "scirate",          # 搜索无结果
    "modelscope",       # 搜索无结果（待接线）
    "qoder_docs",       # 仅营销页无 docs
    "devto",            # 搜索页改版无文章+API 空（恢复后重新启用）
    "tmtpost",          # ?s= 搜索不生效返回新闻流（换搜索方案后重新启用）
    "v2ex",             # IP 邀请码墙（换网络/IP 后重新启用）
    "jiqizhixin",       # 机器之心服务器故障（恢复后重新启用）
    # 需登录墙 / 接口待查
    "gitlab",           # 登录墙
}
# CDP 借真实浏览器已救活的站（v1.9 曾禁用，v2.0 移出）：gitee/leetcode/khanacademy/semanticscholar

def build_sites_config(category: str = None) -> list[dict]:
    """
    构建站点配置列表。

    Args:
        category: "search" | "seed" | "static" | None(全部)

    Returns:
        [{"name": "arxiv", "type": "search"},
         {"name": "github_repos", "type": "seed"},
         {"name": "static_pdfs", "type": "static"}]
    """
    config = {
        # 第1类: 站内搜索 (API优先 + Playwright模拟)
        "search": [
            {"name": "arxiv", "type": "search", "max_results": 30},
            {"name": "semanticscholar", "type": "search", "max_results": 30},
            {"name": "dblp", "type": "search", "max_results": 30},
            {"name": "paperswithcode", "type": "search", "max_results": 30},
            {"name": "aclanthology", "type": "search", "max_results": 30},
            {"name": "huggingface", "type": "search", "max_results": 20},
            {"name": "kaggle", "type": "search", "max_results": 20},
            {"name": "github_topics", "type": "search", "max_results": 30},
            {"name": "bilibili", "type": "search", "max_results": 20},
            {"name": "hackernews", "type": "search", "max_results": 20},
            {"name": "neurips", "type": "search", "max_results": 20},
            {"name": "icml", "type": "search", "max_results": 20},
            {"name": "iclr", "type": "search", "max_results": 20},
            {"name": "openreview", "type": "search", "max_results": 20},
            {"name": "zhihu", "type": "search", "max_results": 20},
            {"name": "juejin", "type": "search", "max_results": 20},
            {"name": "csdn", "type": "search", "max_results": 20},
            {"name": "segmentfault", "type": "search", "max_results": 20},
            {"name": "oschina", "type": "search", "max_results": 20},
            {"name": "v2ex", "type": "search", "max_results": 20},
            {"name": "devto", "type": "search", "max_results": 20},
            {"name": "medium", "type": "search", "max_results": 20},
            {"name": "hackernoon", "type": "search", "max_results": 20},
            {"name": "lobste.rs", "type": "search", "max_results": 20},
            {"name": "datawhale", "type": "search", "max_results": 20},
            {"name": "alignmentforum", "type": "search", "max_results": 20},
            # 视频搜索(Playwright)
            {"name": "youtube", "type": "search", "max_results": 20},
            {"name": "douyin", "type": "search", "max_results": 20},
            {"name": "xiaohongshu", "type": "search", "max_results": 20},
            # 学术搜索(Playwright)
            {"name": "google_scholar", "type": "search", "max_results": 20},
            {"name": "connectedpapers", "type": "search", "max_results": 15},
            {"name": "scirate", "type": "search", "max_results": 15},
            # 代码平台(Playwright)
            {"name": "gitee", "type": "search", "max_results": 20},
            {"name": "gitlab", "type": "search", "max_results": 20},
            {"name": "leetcode", "type": "search", "max_results": 20},
            # AI工具文档(Playwright)
            {"name": "cursor", "type": "search", "max_results": 20},
            {"name": "claude_code_docs", "type": "search", "max_results": 20},
            {"name": "opencode", "type": "search", "max_results": 20},
            {"name": "qoder_docs", "type": "search", "max_results": 20},
            # 课程平台(Playwright)
            {"name": "coursera", "type": "search", "max_results": 20},
            {"name": "edx", "type": "search", "max_results": 20},
            {"name": "khanacademy", "type": "search", "max_results": 20},
            # CDP 攻坚站(v2.0 借真实浏览器解锁反爬强的站)
            {"name": "weibo", "type": "search", "max_results": 20},
            {"name": "infoq", "type": "search", "max_results": 20},
            {"name": "36kr", "type": "search", "max_results": 20},
            {"name": "sspai", "type": "search", "max_results": 20},
            {"name": "tmtpost", "type": "search", "max_results": 20},
        ],
        # 第2类: 种子采集(有Cookie但不支持站内搜索)
        "seed": [
            {"name": "repo_seeds", "type": "seed", "category": "repos"},
            {"name": "doc_seeds", "type": "seed", "category": "docs"},
            {"name": "video_keywords", "type": "seed", "category": "media"},
        ],
        # 第3类: 静态下载(无搜索、无Cookie的已知URL)
        "static": [
            {"name": "static_pdfs", "type": "static"},
        ],
    }

    if category:
        result = config.get(category, [])
    else:
        result = config["search"] + config["seed"] + config["static"]

    # 源头切断：跳过已确认爬不动的站（见 _DISABLED_SITES）
    result = [s for s in result if s["name"] not in _DISABLED_SITES]

    return result


async def run_crawl(terms: list[str], sites_config: list[dict],
                    concurrency: int = 3, delay: float = 0.5, out_dir: str = "",
                    sort_map: dict = None):
    """
    执行爬取任务。

    流程:
    1. 每个 term × 每个 site 先调 search/seed/static 获取结果
    2. noise_filter.quick_filter 过滤噪音
    3. deduper.is_duplicate 去重
    4. RawDownloader 下载原始字节
    5. FilePreserver 落盘到 {out_dir 或 知识库}/{term}/{site}/{type}/
    6. manifest 记录元数据
    """
    scheduler = MixedScheduler(concurrency=concurrency, delay_between_sites=delay)
    scheduler.stats.total_terms = len(terms)
    scheduler.stats.total_sites = len(sites_config)

    deduper = Deduper(os.path.join(BASE, "data", "collector.db"))
    downloader = RawDownloader(user_agent="KnowledgeCollector/1.0 (CC Project)")
    preserver = FilePreserver(root_dir=out_dir or os.path.join(BASE, "知识库"))

    all_results = []
    stats = CrawlStats()

    async with asyncio.Semaphore(concurrency):
        # 语义扩展（可选，KC_SEMANTIC_EXPAND=N 开启）：每词额外搜 N 个语义相似词，扩大限定词
        try:
            expand_n = int(os.environ.get("KC_SEMANTIC_EXPAND", "0") or "0")
        except ValueError:
            expand_n = 0
        for term_i, term in enumerate(terms):
            stats.current_term = term
            stats.terms_done = term_i
            logger.info("=" * 50)
            logger.info("📦 开始爬取词汇[%d/%d]: %s", term_i + 1, len(terms), term)
            if term_i % max(1, len(terms)//10) == 0:
                logger.info(stats.summary())

            search_terms = [term]
            if expand_n > 0:
                try:
                    from core.domain.semantic_expansion import expand_terms
                    search_terms += [s for s in expand_terms(term)[:expand_n] if s]
                    logger.info("  ↪ 语义扩展: %s", " / ".join(search_terms[1:]))
                except Exception:  # noqa: BLE001
                    pass

            for sterm in search_terms:
                for site_cfg in sites_config:
                    try:
                        await _process_site(sterm, site_cfg, deduper, downloader, preserver, stats, sort_map)
                    except Exception as e:
                        stats.errors += 1
                        logger.warning("✗ %s → %s(%s): %s", sterm, site_cfg["name"], site_cfg.get("type"), e)

    logger.info("✅ 完成: %s", stats.summary())


async def _process_site(term: str, sc: dict, deduper: Deduper,
                        downloader: RawDownloader, preserver: FilePreserver,
                        stats: CrawlStats, sort_map: dict = None):
    """处理一个词在一个站上的所有步骤。输出完整日志确保每词每站爬取完全。"""
    stats.current_site = sc["name"]
    stype = sc.get("type", "search")
    site_name = sc["name"]

    results = []

    if stype == "search":
        from core.engines.base import get_searcher
        searcher = get_searcher(site_name)
        if not searcher:
            logger.warning("  ⚠️ [%s] 未注册搜索器，跳过", site_name)
            return
        raw_results = []
        try:
            # 排序接线（v2.3.2）：仅 arxiv/github_topics 支持排序，其余站按默认（诚实不假装）
            _sort = (sort_map or {}).get(site_name)
            if site_name in ("arxiv", "github_topics") and _sort:
                raw_results = await searcher.search(term, sc.get("max_results", 20), sort=_sort)
            else:
                raw_results = await searcher.search(term, sc.get("max_results", 20))
            # 过滤 + 去重
            filtered = [r for r in raw_results if quick_filter(r)]
            # 相关过滤层（R1，补丁重构 v2.2）：标题与搜索词无关的结果丢弃，不落盘
            try:
                from core.filter.keyword_filter import is_relevant_by_keywords
                filtered = [r for r in filtered if is_relevant_by_keywords(r.get("title", ""), term)]
            except Exception:  # noqa: BLE001 过滤层异常不阻塞采集
                pass
            seen = set()
            for r in filtered:
                h = hash((r["url"], term))
                if h not in seen:
                    seen.add(h)
                    results.append(r)
        except Exception as e:
            logger.warning("  ⚠️ [%s] 搜索失败: %s", site_name, e)
            results = []
        finally:
            try:
                close = searcher.close()
                if close and hasattr(close, "__await__"):
                    await close
            except Exception:  # noqa: BLE001
                pass
        if not raw_results:
            logger.info("  • [%s] 搜索返回 0 条（可能被限流/无结果）", site_name)
        else:
            logger.info("  • [%s] 搜索到 %d 条 → 过滤后 %d 条",
                        site_name, len(raw_results), len(results))

    elif stype == "seed":
        cat = sc.get("category", "repos")
        sf = SeedFetcher(config_dir=BASE)
        results = await sf.fetch(term, cat) or []
        logger.info("  • [%s] 种子匹配 %d 条", site_name, len(results))

    elif stype == "static":
        tf = StaticFetcher(config_dir=BASE)
        results = await tf.fetch(term) or []
        logger.info("  • [%s] 静态直链匹配 %d 条", site_name, len(results))

    elif stype == "site":
        # 整站抓取：抓入口页 → 提取站内链接 → 逐页抓取
        from core.download.site_crawler import SiteCrawler
        crawler = SiteCrawler(config_dir=BASE)
        entries = [e for e in crawler.load_entries() if e["name"] == site_name]
        if not entries:
            logger.warning("  ⚠️ [%s] 不在 site_entries.txt", site_name)
            return
        cookie_file = os.path.join(BASE, "data", "cookies_all.txt") if os.path.exists(
            os.path.join(BASE, "data", "cookies_all.txt")) else ""
        pages = await crawler.crawl_site(entries[0], max_pages=sc.get("max_pages", 30),
                                         cookie_file=cookie_file)
        results = [{
            "url": p["url"],
            "title": p["title"],
            "type": "html",
            "summary": "",
            "markdown": p["markdown"],
            "original_term": term,
        } for p in pages]
        logger.info("  • [%s] 整站抓取 %d 页", site_name, len(results))

    if not results:
        return

    # 统计
    n_downloaded = 0
    n_skipped = 0
    n_failed = 0
    for _i, r in enumerate(results, 1):
        url = r["url"]
        ft = r.get("type", "html")

        # 重复检测
        if deduper.is_duplicate(url, term):
            stats.skipped_dedup += 1
            n_skipped += 1
            continue

        # 下载进度日志（避免静默卡死错觉，每条下载前打一行）
        logger.info("  ⏳ 下载 [%d/%d] %s", _i, len(results), (r.get("title") or url)[:50])

        # 下载原始字节
        try:
            # 整站抓取已有 markdown → 直接落盘，避免重复抓取
            if r.get("markdown"):
                md_bytes = r["markdown"].encode("utf-8")
                size = len(md_bytes)
                item_dir = preserver.create_item_dir(term, sc["name"], r.get("title", ""), size)
                local = preserver.save_file(url, md_bytes, term, sc["name"], "html",
                                            r.get("title", ""), item_dir)
                meta_path = preserver.save_metadata(term, sc["name"], "html", url, r.get("title", ""),
                                                    r.get("original_term", term), size, item_dir)
                deduper.add_result(url, term, sc["name"], "html", "saved", size, local)
                stats.downloads_done += 1
                n_downloaded += 1
                # 多类型扩展：网页内嵌图片/文档/音频
                n_downloaded += await _download_extras(
                    r["markdown"], url, term, sc["name"], downloader, preserver, deduper, stats)
            elif ft == "repo":
                # GitHub/Gitee 仓库 → git clone
                ok = await _clone_repo(url, term, sc["name"], r.get("title", ""))
                if ok:
                    deduper.add_result(url, term, sc["name"], "repo", "saved", 0, "")
                    stats.downloads_done += 1
                    n_downloaded += 1
                else:
                    deduper.add_result(url, term, sc["name"], "repo", "failed")
                    n_failed += 1
            elif ft == "video":
                # 视频 → yt-dlp 下载实际文件(视频+封面+描述)
                ok = await _download_video(url, term, sc["name"], r.get("title", ""))
                if ok:
                    deduper.add_result(url, term, sc["name"], "video", "saved", 0, "")
                    stats.downloads_done += 1
                    n_downloaded += 1
                else:
                    # 兜底：视频下载失败(图文笔记/无视频) → 抓页面文本+内嵌图片
                    got = await _save_html_fallback(
                        url, term, sc["name"], r, downloader, preserver, deduper, stats)
                    if got:
                        n_downloaded += got
                    else:
                        n_failed += 1
            else:
                dr = await downloader.download(url, file_type=ft)
                if dr.success and dr.raw_bytes:
                    size = len(dr.raw_bytes)
                    # 先创建序号子文件夹，文件+meta 放同一目录
                    item_dir = preserver.create_item_dir(term, sc["name"], r.get("title", ""), size)
                    local = preserver.save_file(url, dr.raw_bytes, term, sc["name"], ft,
                                                r.get("title", ""), item_dir)
                    meta_path = preserver.save_metadata(term, sc["name"], ft, url, r.get("title", ""),
                                                        r.get("original_term", term), size, item_dir)
                    deduper.add_result(url, term, sc["name"], ft, "saved", size, local)
                    stats.downloads_done += 1
                    n_downloaded += 1
                    # 网页正文 → 内嵌资源扩展(图片/文档/音频/压缩包)
                    if ft in ("html", "markdown", "text") or "markdown" in dr.content_type:
                        n_downloaded += await _download_extras(
                            dr.raw_bytes.decode("utf-8", errors="replace"),
                            url, term, sc["name"], downloader, preserver, deduper, stats)
                else:
                    deduper.add_result(url, term, sc["name"], ft, "failed")
                    n_failed += 1
        except Exception as e:
            deduper.add_result(url, term, sc["name"], ft, "failed")
            n_failed += 1
            stats.errors += 1

    logger.info("  ✔ [%s] 完成: %d/%d 下载, %d 去重跳过, %d 失败 → 词汇[%s]",
                sc["name"], n_downloaded, len(results), n_skipped, n_failed, term)
    stats.sites_done += 1


async def _download_extras(md: str, page_url: str, term: str, site_name: str,
                           downloader: RawDownloader, preserver: FilePreserver,
                           deduper: Deduper, stats: CrawlStats) -> int:
    """网页内嵌资源扩展：图片 + 文档/音频/压缩包/代码。返回新增下载数。"""
    from core.download.resource_extractor import extract_multi
    try:
        extra = extract_multi(md, page_url, term)
    except Exception:  # noqa: BLE001
        return 0
    if not extra:
        return 0
    cnt = 0
    for e in extra:
        eu = e["url"]
        et = e["type"]
        if deduper.is_duplicate(eu, term):
            stats.skipped_dedup += 1
            continue
        try:
            dr = await downloader.download(eu, file_type=et)
        except Exception:  # noqa: BLE001
            deduper.add_result(eu, term, site_name, et, "failed")
            stats.errors += 1
            continue
        if dr.success and dr.raw_bytes:
            size = len(dr.raw_bytes)
            item_dir = preserver.create_item_dir(term, site_name, e.get("title", ""), size)
            local = preserver.save_file(eu, dr.raw_bytes, term, site_name, et,
                                        e.get("title", ""), item_dir)
            preserver.save_metadata(term, site_name, et, eu, e.get("title", ""),
                                    term, size, item_dir)
            deduper.add_result(eu, term, site_name, et, "saved", size, local)
            stats.downloads_done += 1
            cnt += 1
        else:
            deduper.add_result(eu, term, site_name, et, "failed")
            stats.errors += 1
    if cnt:
        logger.info("    ↳ 扩展 %d 个内嵌资源 (%s)", cnt, site_name)
    return cnt


async def _save_html_fallback(url: str, term: str, site_name: str, r: dict,
                              downloader: RawDownloader, preserver: FilePreserver,
                              deduper: Deduper, stats: CrawlStats) -> int:
    """视频下载失败兜底：抓页面文本(markdown) + 内嵌图片。返回新增下载数。"""
    try:
        dr = await downloader.download(url, file_type="html")
    except Exception:  # noqa: BLE001
        return 0
    if not dr.success or not dr.raw_bytes:
        deduper.add_result(url, term, site_name, "video", "failed")
        return 0
    md_text = dr.raw_bytes.decode("utf-8", errors="replace")
    size = len(dr.raw_bytes)
    item_dir = preserver.create_item_dir(term, site_name, r.get("title", ""), size)
    local = preserver.save_file(url, dr.raw_bytes, term, site_name, "markdown",
                                r.get("title", ""), item_dir)
    preserver.save_metadata(term, site_name, "markdown", url, r.get("title", ""),
                            r.get("original_term", term), size, item_dir)
    deduper.add_result(url, term, site_name, "markdown", "saved", size, local)
    stats.downloads_done += 1
    logger.info("    ↳ 视频失败→兜底抓页面文本")
    return 1 + await _download_extras(md_text, url, term, site_name,
                                      downloader, preserver, deduper, stats)


_MEDIA_EXT = (".mp4", ".mkv", ".webm", ".mov", ".flv", ".avi",
              ".m4a", ".mp3", ".wav", ".ogg", ".flac", ".ts")


def _is_media(fname: str) -> bool:
    return fname.lower().endswith(_MEDIA_EXT) and not fname.endswith(".part")


async def _clone_repo(url: str, term: str, site_name: str, title: str) -> bool:
    """git clone 仓库到 知识库/{term}/{类别}/{site}/。"""
    from core.download.preserver import FilePreserver
    from core.domain.site_category import category_of
    import subprocess, shutil

    preserver = FilePreserver(root_dir=os.path.join(BASE, "知识库"))
    cat = category_of(site_name)
    dest_dir = os.path.join(preserver.root, term.replace(" ", "_")[:60], cat,
                            site_name, "repo")
    # 仓库名
    repo_name = url.rstrip("/").split("/")[-1].replace(".git", "") or "repo"
    dest = os.path.join(dest_dir, repo_name)
    os.makedirs(dest_dir, exist_ok=True)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    cmd = ["git", "clone", "--depth", "1", url, dest]
    r = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    try:
        out, err = await asyncio.wait_for(r.communicate(), timeout=180)
    except asyncio.TimeoutError:
        try:
            r.kill()
        except Exception:  # noqa: BLE001
            pass
        return False
    ok = r.returncode == 0 and os.path.isdir(dest)
    if ok:
        logger.info("    ✅ 克隆仓库: %s", repo_name)
    else:
        logger.warning("    ⚠️ 克隆失败: %s", (err or out or b"")[:200])
    return ok


async def _download_video(url: str, term: str, site_name: str, title: str) -> bool:
    """yt-dlp 下载视频到 知识库/{term}/{类别}/{site}/{序号}_日期_标题_大小/。

    一次命令产出多类型资源（不要局限单一类型）：
      .mp4 视频 + .jpg 封面图(thumb) + .description 描述文本 + .info.json 元数据
    """
    from core.download.preserver import FilePreserver
    from core.domain.site_category import category_of
    from core.config import tool
    import subprocess, shutil

    yt = tool("ytdlp")
    if not yt:
        logger.warning("    ⚠️ 未配置 yt-dlp (DD_YTDLP)")
        return False
    preserver = FilePreserver(root_dir=os.path.join(BASE, "知识库"))
    cat = category_of(site_name)
    base_dir = os.path.join(preserver.root, term.replace(" ", "_")[:60], cat, site_name)
    os.makedirs(base_dir, exist_ok=True)
    tmp = os.path.join(base_dir, "_tmp_dl")
    os.makedirs(tmp, exist_ok=True)
    cookie_file = os.path.join(BASE, "data", "cookies_all.txt")
    cmd = [yt, "--no-playlist",
           "-o", os.path.join(tmp, "%(title).40s_%(id)s.%(ext)s"),
           "--write-thumbnail", "--write-description", "--write-info-json",
           url]
    if os.path.exists(cookie_file):
        cmd += ["--cookies", cookie_file]
    r = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    try:
        out, err = await asyncio.wait_for(r.communicate(), timeout=600)
    except asyncio.TimeoutError:
        try:
            r.kill()
        except Exception:  # noqa: BLE001
            pass
        shutil.rmtree(tmp, ignore_errors=True)
        return False
    media = [f for f in os.listdir(tmp) if os.path.isfile(os.path.join(tmp, f))
             and _is_media(f)]
    ok = r.returncode == 0 and len(media) > 0
    if not ok:
        shutil.rmtree(tmp, ignore_errors=True)
        logger.warning("    ⚠️ 视频下载失败: %s", (err or out or b"")[:200])
        return False
    # 算总大小 + 读真实标题(info.json) → 创建序号子文件夹 → 移入 视频+封面+描述
    total = sum(os.path.getsize(os.path.join(tmp, f)) for f in os.listdir(tmp)
                if os.path.isfile(os.path.join(tmp, f)))
    real_title = title or url
    infos = [f for f in os.listdir(tmp) if f.endswith(".info.json")]
    if infos:
        try:
            import json as _json
            with open(os.path.join(tmp, infos[0]), encoding="utf-8") as _f:
                real_title = (_json.load(_f).get("title") or real_title)
        except Exception:  # noqa: BLE001
            pass
    item_dir = preserver.create_item_dir(term, site_name, real_title, total)
    for f in os.listdir(tmp):
        shutil.move(os.path.join(tmp, f), os.path.join(item_dir, f))
    shutil.rmtree(tmp, ignore_errors=True)
    logger.info("    ✅ 视频+封面+描述: %s", media[0][:40])
    return True


def _parse_sort_arg(s: str) -> dict:
    """解析 --sort '站1=排序1,站2=排序2' → {站: 排序}。"""
    m = {}
    for part in (s or "").split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            k, v = k.strip(), v.strip()
            if k:
                m[k] = v
    return m


def main():
    parser = argparse.ArgumentParser(description="三分类知识采集调度器")
    parser.add_argument("--terms", default=None, help="词汇文件路径(默认 config/seeds/vocab_terms_full.txt)")
    parser.add_argument("--category", choices=["search", "seed", "static"], default=None,
                        help="只跑某个类别(默认全部)")
    parser.add_argument("--sites", default=None, help="逗号分隔的站点名子集(如: arxiv,huggingface,kaggle)")
    parser.add_argument("--concurrency", type=int, default=3, help="词级并发数(1~10, 默认3)")
    parser.add_argument("--delay", type=float, default=0.5, help="站间延迟秒数(默认0.5)")
    parser.add_argument("--max-results", type=int, default=None,
                        help="每站最多抓取条数(覆盖各站默认; 爬取引导按用户所选传递)")
    parser.add_argument("--out-dir", default=None, help="落盘根目录(默认 知识库/; 爬取引导按用户所选传递)")
    parser.add_argument("--sort", default=None, help="每站排序(如 arxiv=最新,github_topics=star数; 仅 arxiv/github 支持)")
    args = parser.parse_args()

    terms = load_terms(args.terms) if args.terms else load_terms()
    sites = build_sites_config(args.category)

    # --max-results 覆盖每站抓取条数（智能引导按用户所选传值）
    if args.max_results:
        sites = [{**s, "max_results": args.max_results} for s in sites]

    # --sites 过滤：只保留指定站点
    if args.sites:
        want = set(s.strip() for s in args.sites.split(",") if s.strip())
        sites = [s for s in sites if s["name"] in want]
        if not sites:
            print(f"[错误] --sites 指定的站点都不在配置中: {args.sites}")
            sys.exit(2)

    logger.info("=" * 60)
    logger.info("三分类知识采集启动")
    logger.info("词汇: %d 条 | 站点: %d 个 | 总任务: %d × %d ≈ %d次",
                len(terms), len(sites),
                len(terms), len(sites),
                len(terms) * len(sites))
    logger.info(f"并发: {args.concurrency}词 × 串行{len(sites)}站")
    logger.info(f"预估时间: ~{len(terms) * len(sites) * args.delay / 60:.0f}分钟(仅网络延迟不计下载耗时)")
    logger.info("=" * 60)

    asyncio.run(run_crawl(terms, sites, concurrency=args.concurrency, delay=args.delay,
                          out_dir=args.out_dir or "", sort_map=_parse_sort_arg(args.sort)))


_setup_stdout()


if __name__ == "__main__":
    main()
