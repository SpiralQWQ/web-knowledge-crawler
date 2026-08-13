"""命令行入口：python -m app.cli ..."""
import argparse


def main():
    from core.config import DB_PATH
    from core.download.manifest import Manifest

    p = argparse.ArgumentParser(description="web-knowledge-crawler 采集统计（爬取阶段）")
    p.add_argument("--stats", action="store_true", help="查看采集统计")
    args = p.parse_args()

    if args.stats:
        man = Manifest(DB_PATH)
        print("采集统计:", man.stats() or "（空）", "| 总数:", man.count())
        man.close()
        return
    p.print_help()


if __name__ == "__main__":
    main()
