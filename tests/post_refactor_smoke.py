# -*- coding: utf-8 -*-
"""重构后结构穷举：全量编译 / 断链扫描 / 入口+模块冒烟 / 51 搜索器实例化 / 关键函数存在性。

专治重构可能破坏的点（import 路径/注册/函数缺失）。任何 FAIL 立即报告。
"""
import sys, os, glob, subprocess, py_compile
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FAILS, PASS = [], []


def t(name, ok, detail=""):
    (PASS if ok else FAILS).append(name)
    print(f"  {'✅' if ok else '❌'} {name} {detail}")


# ============ E01 全量编译 + 断链扫描 ============
print("\n===== E01 全量编译 + 断链扫描 =====")
all_py = glob.glob("app/**/*.py", recursive=True) + glob.glob("core/**/*.py", recursive=True) + \
         glob.glob("config/*.py", recursive=True) + glob.glob("tests/*.py") + glob.glob("scripts/*.py")
bad = []
for f in all_py:
    try:
        py_compile.compile(f, doraise=True)
    except Exception as e:
        bad.append(f"{f}: {e}")
t("全量编译", not bad, f"{len(all_py)} 文件" + (f" 失败:{bad[:3]}" if bad else ""))
# 断链扫描：只扫 import/from 行（docstring 不算），排除脚本自身
broken = []
for f in all_py:
    src = open(f, encoding="utf-8").read()
    for line in src.split("\n"):
        s = line.strip()
        if not (s.startswith("import ") or s.startswith("from ")):
            continue
        if any(p in s for p in ["collector.search_engine", "collector.shared", "collector.config",
                                "collector.cookies", "collector.dedup", "collector.manifest",
                                "collector.router", "collector.login", "import tools.",
                                "from tools import", "collector.cdp_helper"]):
            broken.append(f"{f}: {line.strip()}")
t("import 断链扫描", not broken, broken[:5])

# ============ E02 入口 + 模块冒烟 ============
print("\n===== E02 入口 + 模块冒烟 =====")
entry_ok = []
for mod in ["app.crawl_guide", "app.crawl_all", "app.crawl_sites", "app.export_all_cookies",
            "app.export_cookies", "app.cli"]:
    try:
        __import__(mod)
        entry_ok.append(mod)
    except Exception as e:
        t(f"入口 {mod}", False, str(e)[:80])
t("app 6 入口 import", len(entry_ok) == 6, f"{entry_ok}")
core_ok = []
# 注：crawl_helper 需要 crawl4ai 专用环境（AAATool），由子进程调用，主进程不直接 import → 不在本列表
for mod in ["core.config", "core.domain", "core.interaction", "core.auth", "core.download",
            "core.engines", "core.filter", "core.bridges", "core.auth.cookies", "core.auth.login_collectors",
            "core.download.downloader", "core.download.preserver", "core.download.deduper",
            "core.download.scheduler", "core.download.manifest", "core.filter.keyword_filter",
            "core.filter.noise_filter", "core.domain.semantic_expansion", "core.domain.site_category",
            "core.bridges.cdp_helper", "core.bridges.scrapling_helper", "core.bridges.patchright_helper",
            "core.bridges.camofox_helper", "core.bridges.douyin_chain_helper"]:
    try:
        __import__(mod)
        core_ok.append(mod)
    except Exception as e:
        t(f"模块 {mod}", False, str(e)[:80])
t("core 全部模块 import", len(core_ok) == 24, f"{len(core_ok)}/24")

# ============ E03 搜索器实例化 ============
print("\n===== E03 51 搜索器实例化 =====")
try:
    from core.engines.base import list_searchers, get_searcher
    names = list_searchers()
    bad_se = [n for n in names if get_searcher(n) is None]
    t("51 搜索器注册", len(names) == len(set(names)) and not bad_se, f"{len(names)} 个")
    # 逐一实例化（不跑 search，只确认可实例化）
    inst_ok = 0
    for n in names:
        try:
            s = get_searcher(n)
            if s is not None and hasattr(s, "search"):
                inst_ok += 1
        except Exception:
            pass
    t("搜索器实例化", inst_ok == len(names), f"{inst_ok}/{len(names)}")
except Exception as e:
    t("搜索器注册", False, str(e)[:80])

# ============ 关键函数存在性（重构后） ============
print("\n===== 关键函数存在性 =====")
import importlib.util
spec = importlib.util.spec_from_file_location("cg", os.path.join(ROOT, "app", "crawl_guide.py"))
cg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cg)
need = ["run_guide", "main", "build_crawl_command", "_plan_mass", "_plan_single",
        "select_mode", "select_types", "select_sites", "select_details", "select_speed",
        "select_output_dir", "guide_single_crawl", "guide_mass_crawl", "_parse_yesno", "_safe_input",
        "clean_term_list", "load_builtin_vocab", "detect_personality", "recommend_types",
        "recognize_site", "sites_for_types", "_has_login_cookie", "ensure_login",
        "download_single", "download_chain", "_browser_collect_author", "_download_video_list",
        "_probe_url_info", "_probe_author_url", "load_prefs", "save_prefs"]
missing = [n for n in need if not hasattr(cg, n)]
t("关键函数存在", not missing, f"缺失:{missing}" if missing else f"{len(need)} 个")

print(f"\n{'='*60}")
print(f"结构穷举: PASS {len(PASS)}, FAIL {len(FAILS)}")
for f in FAILS:
    print(f"  ❌ {f}")
if not FAILS:
    print("  ✅ 重构后结构全部通过")
