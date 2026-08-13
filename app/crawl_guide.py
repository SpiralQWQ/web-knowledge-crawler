from core.download import _SPEED_PARAMS, _browser_collect_author, _download_video_list, _probe_author_url, _probe_url_info, download_chain, download_single
from core.auth import _browser_alive, _cdp_open_login, ensure_browser_open, ensure_login
from core.interaction import _SORT_PICKED, _parse_yesno, _safe_input, get_terms_from_builtin, get_terms_from_file, get_terms_from_input, guide_mass_crawl, guide_single_crawl, load_prefs, save_prefs, select_details, select_mode, select_output_dir, select_sites, select_speed, select_term_source, select_types
from core.domain import ALL_TYPES, DEFAULT_SORT, NEED_LOGIN, SITE_SORT_OPTIONS, SITE_SUBFORMS, SITE_TYPE_MAP, _ACADEMIC, _CODE, _DOMAIN_SITE, _HOT, _PERSONALITY_DESC, _PERSONALITY_REC, _SORT_SORTABLE, _TUTORIAL, _has_login_cookie, _is_junk, _login_cookie_in, _split_terms, clean_term_list, describe_personality, detect_personality, load_builtin_vocab, recognize_site, recommend_types, site_sort_options, sites_for_types, type_for_site

# -*- coding: utf-8 -*-
"""智能爬取引导（傻瓜入口）— 爬取前交互引导，你点菜爬虫执行。

用法:
    python tools/crawl_guide.py         # 进入引导
    python tools/crawl_guide.py --check # 自检

流程: 模式选择 → 词来源(手输/词库/内置) → 词性格推荐类型 → 选站+排序
      → 细节动态 → 速度 → 确认 → 调 crawl_all 执行
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOCAB_FULL = os.path.join(BASE, "config", "seeds", "vocab_terms_full.txt")

# 安全 input 包装：用户误按 Ctrl+D(EOF) 不崩溃（当空回车处理），Ctrl+C 优雅退出
import builtins as _builtins




input = _safe_input  # 本模块所有 input() 都用安全版


# ============================================================
# A1 词库整理
# ============================================================









# ============================================================
# A2 三种词来源
# ============================================================









# ============================================================
# B1 词性格识别 / B2 类型推荐
# ============================================================











# ============================================================
# C1/C2/C3 站映射
# ============================================================


# 排序接线（v2.3.2）：仅这些站排序真正生效，其余站诚实标注"按默认"








def check_site_mapping() -> dict:
    import app.crawl_all as ca
    sched = set(s["name"] for s in ca.build_sites_config() if s["type"] == "search")
    mapped = set()
    for lst in SITE_TYPE_MAP.values():
        mapped.update(lst)
    return {"调度站": len(sched), "已映射": len(mapped),
            "漏映射": sorted(sched - mapped), "多余": sorted(mapped - sched)}




# ============================================================
# 登录自动化：检测需登录站 → 自动启浏览器 → 开登录页 → 收集 cookie
# ============================================================

# 需登录站 → (登录页 URL, cookie 域名, 关键登录 cookie 关键字)
# 关键 cookie：判定"真登录态"的标准（如抖音 sessionid）。只有匿名 cookie 不算登录。

# 需 CDP 真实浏览器(9222)才能搜索的站（大规模爬取前预检用，与 cdp_search.py 搜索器对齐）
_CDP_SITES = {"douyin", "csdn", "weibo", "bilibili", "infoq", "36kr", "sspai",
              "tmtpost", "leetcode", "gitee", "semanticscholar", "khanacademy"}














# ============================================================
# D 交互流程
# ============================================================























# ============================================================
# E1 执行集成
# ============================================================















def build_crawl_command(params: dict) -> list:
    cmd = [sys.executable, os.path.join(BASE, "tools", "crawl_all.py")]
    if params.get("mode") == "mass":  # 空/缺 mode 不崩，走基础命令
        tmp = os.path.join(BASE, "temp", "guide_terms.txt")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write("\n".join(params["words"]) + "\n")
        cmd += ["--terms", tmp]
        if params.get("sites"):
            cmd += ["--sites", ",".join(params["sites"])]
        sp = _SPEED_PARAMS.get(params.get("speed", "normal"), _SPEED_PARAMS["normal"])
        cmd += ["--concurrency", str(sp["concurrency"]), "--delay", str(sp["delay"])]
        d = params.get("details", {})
        if d.get("max_results"):
            cmd += ["--max-results", str(d["max_results"])]
        if params.get("out_dir"):
            cmd += ["--out-dir", params["out_dir"]]
        sm = params.get("sort_map") or {}
        if sm:
            cmd += ["--sort", ",".join(f"{k}={v}" for k, v in sm.items())]
    # 指定爬取不走 crawl_all（无 --url 参数），由 run_guide 直接调 download_single
    return cmd


def _plan_mass(params: dict):
    """大规模爬取执行计划（大白话版）+ 依赖预检。确认开爬返回命令 list，取消返回 None。"""
    cmd = build_crawl_command(params)
    _sites = params.get("sites", [])
    _words = params.get("words", [])
    _spd = _SPEED_PARAMS.get(params.get("speed", "normal"), _SPEED_PARAMS["normal"])
    _det = params.get("details", {})
    _speed_names = {"fast": "快速", "normal": "标准", "full": "全量"}
    print("\n━━━ 将执行（大白话版）━━━")
    print(f"  🎯 这次要做的：用 {len(_words)} 个词，去 {len(_sites)} 个网站找内容")
    print(f"  📚 搜索词：{'、'.join(_words)}")
    print(f"  🌐 网站：{'、'.join(_sites)}")
    print(f"  🔢 每个网站最多拿：{_det.get('max_results', 20)} 条")
    print(f"  📂 保存到：{params.get('out_dir') or '知识库/'}")
    print(f"  ⚡ 速度：{_speed_names.get(params.get('speed', 'normal'), '标准')}（{_spd['concurrency']} 个词同时找，站间等 {_spd['delay']} 秒，安全不封号）")
    print(f"  📋 详细命令（懂的人看）：{' '.join(cmd)}")
    # 依赖状态总览（总是显示，不只在异常时提示）
    _need_cdp = [s for s in _sites if s in _CDP_SITES]
    _need_login = [s for s in _sites if s in NEED_LOGIN and not _has_login_cookie(s)]
    print("\n  🛠 就绪检查：")
    for _s in _sites:
        if _s in _CDP_SITES:
            _ok = _browser_alive()
            print(f"    {_s}: {'✅ 真实浏览器已就绪' if _ok else '❌ 浏览器没开（会爬不到）'}")
        elif _s in NEED_LOGIN:
            _ok = _has_login_cookie(_s)
            print(f"    {_s}: {'✅ 已登录' if _ok else '❌ 未登录（会爬不到）'}")
        else:
            print(f"    {_s}: ✅ 无需登录")
    # 缺失自动补救
    if _need_cdp and not _browser_alive():
        print("\n  🌐 检测到浏览器没开，自动启动调试浏览器…")
        if ensure_browser_open():
            print("  ✓ 浏览器已启动")
        else:
            print("  ⚠ 浏览器启动失败，这些站会爬不到内容")
    if _need_login:
        print(f"\n  ⚠ 未登录的站：{'、'.join(_need_login)}——爬不到内容。建议先取消，单独指定爬取一次完成登录")
    if not _parse_yesno("\n确认开爬？", default=True):
        print("已取消")
        return None
    return cmd


def _plan_single(params: dict) -> bool:
    """指定爬取执行计划（大白话版）；确认开爬返回 True。"""
    _site = params["site"]
    _ft = "视频" if _site in ("douyin", "bilibili", "youtube") else "网页/内容"
    _spd_n = {"fast": "快速", "normal": "标准", "full": "全量"}.get(params.get("speed", "normal"), "标准")
    print("\n━━━ 将执行（大白话版）━━━")
    print(f"  🎯 这次要做的：下载下面这个内容")
    print(f"  🔗 链接：{params['url']}")
    print(f"  🌐 来源：{_site}（{_ft}）")
    print(f"  📂 保存到：{params.get('out_dir') or '知识库/指定爬取/'}")
    print(f"  ⚡ 速度：{_spd_n}")
    if params.get("chain"):
        print(f"  🔗 连根：会额外下载该作者前几个系列视频")
    if not _parse_yesno("\n确认开爬？", default=True):
        print("已取消")
        return False
    return True


def run_guide() -> None:
    print("\n🤖 智能爬取引导（你点菜，爬虫执行）")
    mode = select_mode()
    if mode == "1":
        params = guide_single_crawl()
        if not params:
            return
        if not _plan_single(params):
            return
        download_single(params["url"], params["site"], params.get("speed", "normal"),
                        params.get("out_dir", ""), chain=params.get("chain", False))
        return
    params = guide_mass_crawl()
    if not params:
        return
    cmd = _plan_mass(params)
    if not cmd:
        return
    import subprocess
    # 预估算时（词×站×延迟），避免用户以为卡住
    sp = _SPEED_PARAMS.get(params.get("speed", "normal"), _SPEED_PARAMS["normal"])
    n_words = len(params.get("words", []))
    n_sites = len(params.get("sites", []))
    est = n_words * n_sites * sp["delay"] / 60
    print(f"\n  🚀 开始爬取：{n_words} 词 × {n_sites} 站（预计最快 ~{est:.0f} 分钟，不含下载耗时）")
    print("     中途可 Ctrl+C 中断，已下载内容不会丢。进度在下方滚动...")
    try:
        subprocess.run(cmd, check=True)
        print("\n  ✅ 爬取完成")
    except Exception as e:  # noqa: BLE001
        print(f"执行出错: {e}")


# ============================================================
# 自检 / 入口
# ============================================================

def _run_check() -> None:
    print("[智能爬取引导 自检]")
    r = clean_term_list("机器学习，transformer 1.图神经网络 https://x.com/a 12345长串")
    print("  A1 词库整理:", r["words"], "| URL:", r["urls"])
    print("  A2 内置词表:", len(load_builtin_vocab()), "词")
    print("  B1 词性格: 机器学习→", detect_personality("机器学习"),
          "| Python入门→", detect_personality("Python 入门教程"),
          "| 大模型动态→", detect_personality("大模型最新动态"))
    print("  C1 站映射:", check_site_mapping())
    print("  D 认站: bilibili链接→", recognize_site("https://www.bilibili.com/video/BV1xx"))
    print("  自检通过 ✅")


def main() -> None:
    # 输出统一 UTF-8：防 GBK 终端打印 ✓/emoji 时崩溃（不同终端兼容）
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    if "--check" in sys.argv:
        _run_check()
    else:
        run_guide()


if __name__ == "__main__":
    main()
