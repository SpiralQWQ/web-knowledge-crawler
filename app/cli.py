"""命令行入口：python -m collector.cli ..."""
import argparse
import os


def main():
    from . import config
    config.ensure_dirs()
    p = argparse.ArgumentParser(description="web-knowledge-crawler 采集器（爬取阶段）")
    p.add_argument("--web", metavar="SEED_FILE", help="网页采集（Crawl4AI）")
    p.add_argument("--video", metavar="SEED_FILE", help="视频采集（media-collect）")
    p.add_argument("--paper", metavar="SEED_FILE", help="论文采集（arXiv API）")
    p.add_argument("--doc", metavar="SEED_FILE", help="文档采集（网页托管 PDF/DOC）")
    p.add_argument("--mirror", metavar="SEED_FILE", help="仓库镜像（git clone --mirror）")
    p.add_argument("--discover-repos", action="store_true", help="发现 GitHub 500star+ 仓库（写入 repo_seeds.txt）")
    p.add_argument("--min-stars", type=int, default=500, help="仓库发现最低 star")
    p.add_argument("--stats", action="store_true", help="查看采集统计")
    args = p.parse_args()

    if args.stats:
        from .manifest import Manifest
        man = Manifest(config.DB_PATH)
        print("采集统计:", man.stats() or "（空）", "| 总数:", man.count())
        man.close()
        return
    if args.web:
        from .web_crawler import collect_batch
        collect_batch(args.web)
        return
    if args.video:
        from .video_collector import collect_batch
        collect_batch(args.video)
        return
    if args.paper:
        from .paper_collector import collect_batch
        collect_batch(args.paper)
        return
    if args.doc:
        from .doc_collector import collect_batch
        collect_batch(args.doc)
        return
    if args.mirror:
        from .repo_mirror import collect_batch
        collect_batch(args.mirror)
        return
    if args.discover_repos:
        from .repo_discover import discover
        seeds = os.path.join(config.BASE, "config", "seeds", "repo_seeds.txt")
        discover(args.min_stars, out_seeds=seeds)
        return
    p.print_help()


if __name__ == "__main__":
    main()
