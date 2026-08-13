# -*- coding: utf-8 -*-
"""crawl_guide 全选项穷举 v2（模拟"傻子用户随便乱点"）。

覆盖：所有交互函数 × 输入变体（空/数字/乱输/EOF/超长/emoji/口令乱贴），
加上 guide_mass_crawl / run_guide 完整流程的极端序列。任何异常即记录。
"""
import sys, os, io, contextlib, builtins
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import importlib.util

spec = importlib.util.spec_from_file_location("cg", os.path.join(ROOT, "app", "crawl_guide.py"))
cg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cg)

FAILS, BAD = [], []


def run(name, func, seq):
    it = iter(seq)
    builtins.input = lambda *a, **k: next(it, "")
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            r = func()
        return ("OK", r)
    except SystemExit:
        return ("OK", "SystemExit")
    except Exception as e:
        return ("EXC:" + type(e).__name__ + ":" + str(e), None)


def ex(name, func, seqs, check=None):
    for i, seq in enumerate(seqs):
        st, r = run(name, func, seq)
        if st != "OK":
            FAILS.append(f"{name}[{i}] 输入={seq!r} → {st}")
        elif check and not check(r):
            BAD.append(f"{name}[{i}] 输入={seq!r} → 不合理 {r!r}")


# ============ ① _safe_input EOF/Ctrl+C ============
import builtins as _b
_old_raw = _b.input
_b.input = lambda p='': (_ for _ in ()).throw(EOFError())
try:
    r = cg._safe_input("")
    if r != "":
        BAD.append(f"_safe_input EOF → {r!r} (应空)")
except Exception as e:
    FAILS.append(f"_safe_input EOF → {type(e).__name__}:{e}")
finally:
    _b.input = _old_raw

# ============ ② 交互入口（含傻子场景） ============
ex("select_mode", cg.select_mode,
   [[], [""], ["1"], ["2"], ["3"], ["0"], ["-1"], ["abc"], ["乱输"],
    ["https://v.douyin.com/x/ 复制此链接"],  # 口令贴错位置
    ["y"], ["n"], ["1.5"], ["@"], ["a" * 200]],
   check=lambda r: r in ("1", "2"))

ex("select_speed", cg.select_speed,
   [[], [""], ["快"], ["标准"], ["全量"], ["快速"], ["1"], ["abc"], ["🐢"], ["超长" * 50]],
   check=lambda r: r in ("fast", "normal", "full"))

ex("_parse_yesno", lambda: cg._parse_yesno("?", default=True),
   [[], ["y"], ["n"], ["yes"], ["no"], ["是"], ["否"], ["不要"], ["Y"], ["N"],
    ["1"], ["abc"], [""], ["\n"], [" y "], ["  n  "]],
   check=lambda r: isinstance(r, bool))

ex("select_output_dir", lambda: cg.select_output_dir("D:/默认"),
   [[], ["1"], ["2", "E:/自定义"], ["2", ""], ["E:/直接路径"],
    ['"E:/带引号路径"'], ["E:/含 空格 路径"], ["abc"], ["@#$"], ["\\\\.\\无意义"],
    ["2", "乱输路径"], [""]],
   check=lambda r: isinstance(r, str) and len(r) > 0)

ex("select_term_source", cg.select_term_source,
   [[], ["1", "机器学习", ""], ["1", "", ""], ["1", "机器学习 🚀🔥", ""],
    ["1", "别怕 https://v.douyin.com/x 复制此链接", ""],  # 口令贴词
    ["1", "机器学习", "1"], ["1", "机器学习", "不存在的词"],
    ["2", "E:/不存在文件.txt", "机器学习", ""], ["2", "", ""],
    ["2", "E:/", "机器学习", ""],   # 路径是目录
    ["3", ""], ["0", "机器学习", ""], ["9", "机器学习", ""],
    ["abc", "机器学习", ""], ["1", "a" * 500, ""]],
   check=lambda r: isinstance(r, list))

# ============ ③ 内容类型 ============
REC = {"论文": True, "视频": True, "文章": False, "代码": False, "数据集": True,
       "课程": False, "文档": False, "题库": False}
ex("select_types", lambda: cg.select_types(REC),
   [[] * 8, [""] * 8, ["n"] * 8, ["y"] * 8,
    ["y", "n", "", "y", "n", "", "", ""],
    ["abc"] * 8, ["1"] * 8, ["🐢"] * 8, ["a" * 200] * 8,
    ["n", "n", "n", "n", "n", "n", "n", "n"]],
   check=lambda r: isinstance(r, list) and len(r) >= 1)

# ============ ④ 网站选择 ============
TYPES = ["视频", "文章"]
N16 = len(cg.sites_for_types(TYPES)) + 10
ex("select_sites", lambda: cg.select_sites(TYPES),
   [[] * N16, [""] * N16, ["n"] * N16, ["y"] * N16,
    ["n"] + [""] * (N16 - 1),
    ["y", "abc"] + [""] * (N16 - 2),
    ["🐢"] * N16, ["1"] * N16],
   check=lambda r: isinstance(r, list))

# ============ ⑤ 细节 ============
ex("select_details", lambda: cg.select_details(["bilibili", "zhihu", "youtube"]),
   [[] * 10, [""] * 10, ["近1周", "中文", "0", "", ""],
    ["", "", "-5", "", ""], ["", "", "abc", "", ""], ["", "", "999999", "", ""],
    ["", "", "1.5", "", ""], ["abc"] * 5, ["🐢"] * 5, ["a" * 300] * 5,
    ["近1周", "英文", "50", "y", "y"], ["", "", "500", "n", "n"]],
   check=lambda r: isinstance(r, dict) and isinstance(r.get("max_results"), int)
                   and 1 <= r["max_results"] <= 500)

# ============ ⑥ 指定爬取全分支 ============
ex("guide_single_crawl", cg.guide_single_crawl,
   [[], [""], ["abc"], ["1"],
    ["https://v.douyin.com/x/", "", "", ""],
    ["https://v.douyin.com/x/", "y", "", ""],
    ["https://v.douyin.com/x/", "n", "", ""],
    ["https://v.douyin.com/x/", "乱输", "", ""],
    ["https://未知站.xyz/a", ""], ["https://未知站.xyz/a", "y", "bilibili", "", ""],
    ["https://未知站.xyz/a", "y", ""], ["https://未知站.xyz/a", "y", "乱输", "", ""],
    ['"https://www.bilibili.com/video/BV1xx"', "", "", ""],
    ["https://juejin.cn/post/123", "", ""],
    ["https://v.douyin.com/x/" * 5, "", ""],  # 超长
    ["https://v.douyin.com/x/", "y", "https://www.bilibili.com/video/BV1xx", "", ""]],  # 站名填URL
   check=lambda r: r is None or (isinstance(r, dict) and r.get("url")))

# ============ ⑦ guide_mass_crawl 完整流程（傻子极端序列） ============
# 全回车（最懒）：模式后全默认
SEQ_ALL_ENTER = [""] * 45
# 全 y：词来源1 + 词 + 确认 + 类型全y + 站全y + 细节默认 + 速度 + 位置
SEQ_ALL_Y = ["1", "机器学习", ""] + ["y"] * 8 + ["y"] * N16 + [""] * 10
# 类型全n + 站全n（应返回 None）
SEQ_ALL_N = ["1", "机器学习", ""] + ["n"] * 8 + ["n"] * N16 + [""] * 10
# 词空
SEQ_EMPTY_WORD = ["1", "", ""] + [""] * 30
# 口令贴词 + 全选
SEQ_PASTE = ["1", "别怕 https://v.douyin.com/x 复制", ""] + [""] * 40
# 词来源2 不存在文件
SEQ_FILE_BAD = ["2", "E:/不存在.txt", "机器学习", ""] + [""] * 35
# 词来源3 内置
SEQ_BUILTIN = ["3", ""] + [""] * 35
# 词来源9 乱输 → 默认内置
SEQ_SRC9 = ["9", ""] + [""] * 35
# 超长词
SEQ_LONGWORD = ["1", "机" * 300, ""] + [""] * 35

for i, seq in enumerate([SEQ_ALL_ENTER, SEQ_ALL_Y, SEQ_ALL_N, SEQ_EMPTY_WORD,
                         SEQ_PASTE, SEQ_FILE_BAD, SEQ_BUILTIN, SEQ_SRC9, SEQ_LONGWORD]):
    st, r = run("guide_mass_crawl", cg.guide_mass_crawl, seq)
    if st != "OK":
        FAILS.append(f"guide_mass_crawl[{i}] → {st}")
    elif r is not None and not (isinstance(r, dict) and r.get("words")):
        BAD.append(f"guide_mass_crawl[{i}] → 不合理 {r!r}")

# ============ ⑧ run_guide 完整流程（确认开爬=n 取消，不真爬） ============
# 大规模全默认 + 确认开爬 n
SEQ_RUN_MASS = ["2"] + SEQ_ALL_ENTER[1:44] + ["n"]
# 指定爬取：链接 + 连根n + 速度 + 位置 + 确认n
SEQ_RUN_SINGLE = ["1", "https://v.douyin.com/x/", "n", "", "", "n"]
# 模式乱输(3) → 应回退大规模 + 确认n
SEQ_RUN_MODE3 = ["3"] + SEQ_ALL_ENTER[1:44] + ["n"]
# 指定爬取无链接 → 应返回不崩
SEQ_RUN_NOLINK = ["1", "abc"]

for i, seq in enumerate([SEQ_RUN_MASS, SEQ_RUN_SINGLE, SEQ_RUN_MODE3, SEQ_RUN_NOLINK]):
    st, r = run("run_guide", cg.run_guide, seq)
    if st != "OK":
        FAILS.append(f"run_guide[{i}] → {st}")

# ============ ⑨ 纯函数边界 ============
for i, raw in enumerate(["", "  ", "机器学习", "机器学习,transformer 1.深度学习 https://x.com/a",
                         "12345长串", "a" * 60, "，；、\n混合 空格", "@#$%",
                         "机器学习 🚀🔥", "别怕 https://v.douyin.com/x 复制此链接",
                         "https://a.com/x https://b.com/y 词1 词2"]):
    try:
        r = cg.clean_term_list(raw)
        if not isinstance(r, dict) or not isinstance(r.get("words"), list):
            BAD.append(f"clean_term_list[{i}] → {r!r}")
    except Exception as e:
        FAILS.append(f"clean_term_list[{i}] {raw!r} → {type(e).__name__}:{e}")

for i, t in enumerate(["", "123", "12345长串", "机器学习", "a" * 31, "中" * 31,
                       "1.5版本", "transformer", "x" * 41, "🚀🔥" * 15]):
    try:
        cg._is_junk(t)
    except Exception as e:
        FAILS.append(f"_is_junk[{i}] {t!r} → {type(e).__name__}:{e}")

for i, t in enumerate(["", "机器学习", "Python 入门", "量子物理", "x" * 100, "@#$", "123", "🚀"]):
    try:
        r = cg.detect_personality(t)
        if r not in ("学术", "教程", "热点", "代码", "通用"):
            BAD.append(f"detect_personality[{i}] {t!r} → {r!r}")
    except Exception as e:
        FAILS.append(f"detect_personality[{i}] {t!r} → {type(e).__name__}:{e}")

for i, u in enumerate(["", "https://www.bilibili.com/video/BV1", "https://v.douyin.com/x",
                       "https://youtube.com/watch", "notaurl", "https://未知站.com/",
                       "x" * 50, "https://www.douyin.com/user/self"]):
    try:
        cg.recognize_site(u)
    except Exception as e:
        FAILS.append(f"recognize_site[{i}] {u!r} → {type(e).__name__}:{e}")

LOGIN_ROWS = [".douyin.com\tTRUE\t/\tTRUE\t0\tsessionid\tabc\n",
              "#HttpOnly_.douyin.com\tTRUE\t/\tTRUE\t0\tsessionid\tabc\n",
              "# 注释行\n", "weibo.com\tTRUE\t/\tTRUE\t0\tsessionid\txyz\n",
              ".douyin.com\tTRUE\t/\tTRUE\t0\tttwid\tguest\n", "短行\n", "",
              "no_tab_here\n", ".douyin.com\tTRUE\t/\tTRUE\tsessionid\tabc\n",
              "\t\t\t\t\t\n"]
for i, raw in enumerate(LOGIN_ROWS):
    try:
        cg._login_cookie_in(raw, "douyin.com", ("sessionid",))
    except Exception as e:
        FAILS.append(f"_login_cookie_in[{i}] {raw!r} → {type(e).__name__}:{e}")

PARAMS = [
    {"mode": "mass", "words": ["机器学习"], "sites": ["arxiv"], "speed": "fast", "details": {"max_results": 5}},
    {"mode": "mass", "words": [], "sites": [], "speed": "乱输", "details": {}},
    {"mode": "mass", "words": ["a"], "sites": ["x" * 10], "speed": "full", "details": {"max_results": 999999}},
    {"mode": "单条"}, {}, {"mode": "mass", "words": ["词"], "sites": ["bilibili"], "speed": "normal",
     "details": {"max_results": -5}, "out_dir": "E:/位置"},
]
for i, p in enumerate(PARAMS):
    try:
        r = cg.build_crawl_command(p)
        if not isinstance(r, list):
            BAD.append(f"build_crawl_command[{i}] {p!r} → {r!r}")
    except Exception as e:
        FAILS.append(f"build_crawl_command[{i}] {p!r} → {type(e).__name__}:{e}")

# ============ 汇总 ============
print(f"\n{'='*60}")
print(f"傻子用户穷举: 崩溃/异常 {len(FAILS)} 项, 不合理 {len(BAD)} 项")
print(f"{'='*60}")
for f in FAILS:
    print("  ❌", f)
for b in BAD:
    print("  ⚠️", b)
if not FAILS and not BAD:
    print("  ✅ 全部通过")
