#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""web-knowledge-crawler 开箱即用配置向导 (setup.py)

拉取仓库后运行:  python setup.py
→ 交互式询问关键配置 → 自动生成 .env + 检测依赖 → 开箱即用

无需提前看任何文档——回答几个问题就能开始用。
"""
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

# 输出 UTF-8：防 GBK 终端打印 ✅/emoji 崩溃
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass


def ask(prompt: str, default: str = "", validate=None) -> str:
    """防呆输入：默认值 / EOF / Ctrl+C 不崩。"""
    while True:
        try:
            v = input(prompt + (f" [{default}]" if default else "") + "：").strip().strip('"')
        except (EOFError, KeyboardInterrupt):
            print()
            v = ""
        v = v or default
        if not validate or validate(v):
            return v
        print("  ⚠ 输入无效，请重试（可直接回车用默认/跳过）")


def main():
    print("=" * 52)
    print("  web-knowledge-crawler  配置向导")
    print("  回答几个问题，自动生成 .env，即可开箱即用。")
    print("=" * 52)

    # 1. Python 版本检查
    if sys.version_info >= (3, 10):
        print(f"\n[1/5] ✅ Python {sys.version.split()[0]}（满足 3.10+）")
    else:
        print(f"\n[1/5] ❌ Python {sys.version.split()[0]}（需 3.10+）")
        return 1

    # 2. 安装依赖
    print("\n[2/5] 安装 Python 依赖...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r",
                        str(BASE / "requirements.txt")], check=False)
        print("  ✅ 依赖安装完成（或已安装）")
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ 依赖安装失败（{e}），可稍后手动: pip install -r requirements.txt")

    # 3. Crawl4AI 环境路径（网页渲染，可选）
    print("\n[3/5] Crawl4AI 环境（网页渲染用，可跳过）")
    c4ai = ask("  输入 Crawl4AI 的 python.exe 路径（回车跳过）", validate=lambda p: not p or os.path.exists(p))
    if c4ai and not os.path.exists(c4ai):
        print("  ⚠ 路径不存在，已跳过（该站会优雅降级）")
        c4ai = ""

    # 4. yt-dlp 可执行文件（视频/音频下载，可选）
    print("\n[4/5] yt-dlp（视频/音频下载，可跳过）")
    yt = ask("  输入 yt-dlp 可执行文件路径（回车跳过）", validate=lambda p: not p or os.path.exists(p))
    if yt and not os.path.exists(yt):
        print("  ⚠ 路径不存在，已跳过")
        yt = ""

    # 5. Cookie 浏览器 + GitHub token（可选）
    print("\n[5/5] 登录态与令牌（可跳过）")
    browser = ask("  需登录站用哪个浏览器注入 cookie？(edge/chrome/firefox)", default="edge")
    gh = ask("  GitHub Token（提升搜索限流，可选，回车跳过）")

    # 生成 .env
    env_path = BASE / ".env"
    lines = [
        "# 由 setup.py 生成（可再手动改）",
        f"CRAWL4AI_PY={c4ai}",
        f"DD_YTDLP={yt}",
        f"KC_COOKIE_BROWSER={browser or 'edge'}",
        f"GH_TOKEN={gh}" if gh else "# GH_TOKEN=",
        "# 其他工具路径（Scrapling/Patchright/Playwright 等）见 config/collector.yaml",
    ]
    if env_path.exists():
        print("\n  ⚠ 已存在 .env，是否覆盖？(y/n)")
        if input("  ").strip().lower() not in ("y", "yes", "是"):
            print("  ✅ 保留现有 .env，向导结束")
            print("\n  🚀 下一步: python app/crawl_guide.py")
            return 0
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n  ✅ 已生成 .env（{env_path}）")

    print("\n" + "=" * 52)
    print("  配置完成！开始使用:")
    print("    python app/crawl_guide.py     # 🧭 智能引导（推荐）")
    print("    python app/crawl_all.py       # 大规模爬取")
    print("=" * 52)
    print("  提示：需要登录的站（抖音/小红书等）首次爬取会自动引导登录。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
