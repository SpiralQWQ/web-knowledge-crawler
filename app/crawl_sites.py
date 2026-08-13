"""整站抓取入口 — 对官方文档/教程/博客等无搜索功能的站，抓取整站内容。

遍历 config/site_entries.txt 的 195 个站：
  抓入口页 → 提取站内链接 → 逐页抓取 markdown → 存 知识库/{站点名}/{类别}/

用法:
  python tools/crawl_sites.py                          # 全部195站
  python tools/crawl_sites.py --sites pytorch,react    # 指定站
  python tools/crawl_sites.py --max-pages 30           # 每站最多页数
"""
import argparse
import asyncio
import logging
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("crawl_sites")


def _setup_stdout():
    try:
        if not sys.stdout.isatty():
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if not sys.stderr.isatty():
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass


async def run(entries, max_pages, delay):
    from core.download.site_crawler import SiteCrawler
    from core.download.preserver import FilePreserver
    from core.download.deduper import Deduper
    from core.download.downloader import RawDownloader

    crawler = SiteCrawler(config_dir=BASE)
    preserver = FilePreserver(root_dir=os.path.join(BASE, "知识库"))
    deduper = Deduper(os.path.join(BASE, "data", "collector.db"))
    cookie_file = os.path.join(BASE, "data", "cookies_all.txt")
    if not os.path.exists(cookie_file):
        cookie_file = ""

    total_downloaded = 0
    total_failed = 0

    for i, entry in enumerate(entries):
        site = entry["name"]
        logger.info("=" * 50)
        logger.info("📦 整站抓取[%d/%d]: %s (%s)", i + 1, len(entries), site, entry["url"])
        try:
            # 音频类站点（播客/访谈）→ RSS 采集音频直链
            if entry["category"] == "音频":
                n_ok, n_fail = await _collect_podcast(entry, preserver, deduper, downloader)
                total_downloaded += n_ok
                total_failed += n_fail
                logger.info("  ✔ [%s] 音频采集完成: %d 集下载, %d 失败", site, n_ok, n_fail)
                if delay > 0:
                    await asyncio.sleep(delay)
                continue
            pages = await crawler.crawl_site(entry, max_pages=max_pages, cookie_file=cookie_file)
            logger.info("  • [%s] 抓到 %d 页", site, len(pages))
        except Exception as e:  # noqa: BLE001
            logger.warning("  ⚠️ [%s] 抓取失败: %s", site, e)
            total_failed += 1
            continue

        n_ok = 0
        for p in pages:
            url = p["url"]
            md = p.get("markdown", "")
            if not md:
                continue
            if deduper.is_duplicate(url, site):
                continue
            try:
                cat = p.get("category") or entry["category"]
                md_bytes = md.encode("utf-8")
                size = len(md_bytes)
                item_dir = preserver.create_item_dir(site, "site", p.get("title", ""), size, category=cat)
                local = preserver.save_file(url, md_bytes, site, "site", "html",
                                            p.get("title", ""), item_dir, category=cat)
                preserver.save_metadata(site, "site", "html", url, p.get("title", ""),
                                        site, size, item_dir, category=cat)
                deduper.add_result(url, site, "site", "html", "saved", size, local)
                n_ok += 1
                # 网页内嵌资源扩展（图片/pdf/doc/音频/压缩包）
                from core.download.resource_extractor import extract_multi
                for e in extract_multi(md, url, site):
                    eu = e["url"]
                    if deduper.is_duplicate(eu, site):
                        continue
                    dr = await downloader.download(eu, file_type=e["type"])
                    if dr.success and dr.raw_bytes:
                        esize = len(dr.raw_bytes)
                        eitem = preserver.create_item_dir(site, "site", e.get("title", ""),
                                                          esize, category=cat)
                        elocal = preserver.save_file(eu, dr.raw_bytes, site, "site",
                                                     e["type"], e.get("title", ""), eitem, category=cat)
                        preserver.save_metadata(site, "site", e["type"], eu, e.get("title", ""),
                                                site, esize, eitem, category=cat)
                        deduper.add_result(eu, site, "site", e["type"], "saved", esize, elocal)
                        n_ok += 1
            except Exception as e:  # noqa: BLE001
                logger.warning("  ✗ [%s] 保存失败: %s", url[:50], e)
                total_failed += 1
        total_downloaded += n_ok
        logger.info("  ✔ [%s] 完成: %d/%d 页落盘", site, n_ok, len(pages))
        if delay > 0:
            await asyncio.sleep(delay)

    logger.info("=" * 50)
    logger.info("✅ 整站抓取完成: %d 站, 下载 %d 页, 失败 %d", len(entries), total_downloaded, total_failed)


async def _collect_podcast(entry: dict, preserver, deduper, downloader,
                           max_eps: int = 5) -> tuple:
    """音频类站点：RSS 采集分集音频直链 → 逐个下载。返回 (成功数, 失败数)。"""
    from core.download.podcast_fetcher import PodcastFetcher

    pf = PodcastFetcher()
    site = entry["name"]
    cat = entry["category"]
    rss = await pf.discover_rss(entry["url"])
    if not rss:
        logger.warning("  ⚠️ [%s] 未找到 RSS feed", site)
        return 0, 0
    eps = await pf.parse_rss(rss, max_eps)
    if not eps:
        logger.warning("  ⚠️ [%s] RSS 无音频直链: %s", site, rss[:60])
        return 0, 0
    logger.info("  • [%s] RSS %s → %d 集音频", site, rss[:55], len(eps))

    n_ok = n_fail = 0
    for e in eps:
        eu = e["url"]
        if deduper.is_duplicate(eu, site):
            continue
        try:
            dr = await downloader.download(eu, file_type="audio")
        except Exception:  # noqa: BLE001
            deduper.add_result(eu, site, "site", "audio", "failed")
            n_fail += 1
            continue
        if dr.success and dr.raw_bytes:
            size = len(dr.raw_bytes)
            item_dir = preserver.create_item_dir(site, "site", e.get("title", ""),
                                                 size, category=cat)
            local = preserver.save_file(eu, dr.raw_bytes, site, "site", "audio",
                                        e.get("title", ""), item_dir, category=cat)
            preserver.save_metadata(site, "site", "audio", eu, e.get("title", ""),
                                    site, size, item_dir, category=cat)
            deduper.add_result(eu, site, "site", "audio", "saved", size, local)
            n_ok += 1
            logger.info("    ✅ 音频: %s (%dKB)", e.get("title", "")[:40], size // 1024)
        else:
            deduper.add_result(eu, site, "site", "audio", "failed")
            n_fail += 1
    return n_ok, n_fail


def main():
    parser = argparse.ArgumentParser(description="整站抓取（官方文档/教程/博客站）")
    parser.add_argument("--sites", default=None, help="逗号分隔站点名子集(如 pytorch,react)")
    parser.add_argument("--max-pages", type=int, default=30, help="每站最多抓取页数(默认30)")
    parser.add_argument("--delay", type=float, default=1.0, help="站间延迟秒数(默认1.0)")
    args = parser.parse_args()

    from core.download.site_crawler import SiteCrawler
    crawler = SiteCrawler(config_dir=BASE)
    entries = crawler.load_entries()
    if args.sites:
        want = set(s.strip().lower() for s in args.sites.split(",") if s.strip())
        entries = [e for e in entries if e["name"].lower() in want]

    logger.info("=" * 60)
    logger.info("整站抓取启动")
    logger.info("站点: %d 个 (每站最多 %d 页)", len(entries), args.max_pages)
    logger.info("预计耗时: 每站~%d秒 × %d站 ≈ %d分钟",
                args.max_pages * 6, len(entries), args.max_pages * 6 * len(entries) // 60)
    logger.info("=" * 60)

    asyncio.run(run(entries, args.max_pages, args.delay))


_setup_stdout()

if __name__ == "__main__":
    main()
