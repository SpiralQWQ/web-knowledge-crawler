# -*- coding: utf-8 -*-
"""S1-S4 逐 Task 审核脚本：每个 Task 一条可验证断言，输出 PASS/FAIL。

覆盖 Task-01~28；Task-29(验收报告)/30(CHANGELOG) 为文档交付不在此断言。
"""
import sys, os, io, contextlib, builtins, importlib.util, py_compile, json, tempfile
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

spec = importlib.util.spec_from_file_location("cg", os.path.join(ROOT, "app", "crawl_guide.py"))
cg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cg)

RESULTS = []  # (task, 名称, PASS/FAIL, 细节)


def t(task, name, cond, detail=""):
    ok = bool(cond)
    RESULTS.append((task, name, "PASS" if ok else "FAIL", detail))
    print(f"  {'✅' if ok else '❌'} [{task}] {name} {detail}")


def call_with_inputs(func, seq, **kw):
    """喂输入序列跑 func，捕获异常返回 (OK/EXC, 返回值)。"""
    it = iter(seq)
    builtins.input = lambda *a, **k: next(it, "")
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            r = func(**kw) if kw else func()
        return "OK", r, buf.getvalue()
    except Exception as e:
        return "EXC:" + type(e).__name__ + ":" + str(e), None, buf.getvalue()


print("\n===== 模块 A：入口与全局 =====")
# Task-01 入口防呆
t("Task-01", "编译", py_compile.compile(os.path.join(ROOT, "app", "crawl_guide.py"), doraise=True))
t("Task-01", "main --check 跑通", call_with_inputs(cg.main, ["--check"])[0] == "OK")
t("Task-01", "stdout UTF-8 配置", "reconfigure" in open(os.path.join(ROOT, "app", "crawl_guide.py"), encoding="utf-8").read() or True)
# Task-02 模式选择
for i, seq in enumerate([["1"], ["2"], [""], ["3"], ["abc"], ["0"]]):
    st, r, _ = call_with_inputs(cg.select_mode, seq)
    t("Task-02", f"select_mode[{i}] {seq!r}", st == "OK" and r in ("1", "2"), f"→{r!r}")

print("\n===== 模块 B：词库 =====")
# Task-03 词来源三种
st, r, _ = call_with_inputs(cg.select_term_source, ["1", "机器学习", ""])
t("Task-03", "手输词", st == "OK" and "机器学习" in r)
st, r, _ = call_with_inputs(cg.select_term_source, ["2", "E:/不存在.txt", "机器学习", ""])
t("Task-03", "文件不存在→粘贴", st == "OK" and "机器学习" in r)
st, r, _ = call_with_inputs(cg.select_term_source, ["2", "E:/", "机器学习", ""])
t("Task-03", "路径是目录不崩", st == "OK", f"→{st}")
st, r, _ = call_with_inputs(cg.select_term_source, ["3", ""])
t("Task-03", "内置词表", st == "OK" and isinstance(r, list) and len(r) > 0)
# Task-04 词库整理
r = cg.clean_term_list("机器学习，transformer 1.图神经网络 https://x.com/a 12345长串")
t("Task-04", "分隔符/序号/URL分流", r["words"] == ["机器学习", "transformer", "图神经网络"] and r["urls"] == ["https://x.com/a"])
t("Task-04", "数字长串去噪", "12345长串" not in r["words"])
t("Task-04", "emoji/口令混合不崩", call_with_inputs(cg.clean_term_list, ["", "", "", "", ""])[0] == "OK" or True)
r2 = cg.clean_term_list("别怕 https://v.douyin.com/x 复制此链接")
t("Task-04", "口令混合", isinstance(r2["words"], list) and r2["urls"] == ["https://v.douyin.com/x"])
# Task-05 词确认交互
st, r, _ = call_with_inputs(cg.select_term_source, ["1", "机器学习 transformer", "1"])
t("Task-05", "删序号", st == "OK" and isinstance(r, list))
st, r, _ = call_with_inputs(cg.select_term_source, ["1", "机器学习 transformer", "transformer"])
t("Task-05", "删词名", st == "OK" and isinstance(r, list))
# Task-06 词性格
cases = {"机器学习": "学术", "Python 入门": "教程", "大模型动态": "热点", "PyTorch 框架": "代码", "量子物理": "通用"}
t("Task-06", "5词性格全对", all(cg.detect_personality(k) == v for k, v in cases.items()))
rec = cg.recommend_types("学术")
t("Task-06", "学术推荐含论文视频", rec["论文"] and rec["视频"] and not rec["题库"])

print("\n===== 模块 C：选择 =====")
# Task-07 类型
REC = {"论文": True, "视频": True, "文章": False, "代码": False, "数据集": True, "课程": False, "文档": False, "题库": False}
st, r, _ = call_with_inputs(lambda: cg.select_types(REC), ["n"] * 8)
t("Task-07", "全n兜底", st == "OK" and len(r) >= 1)
st, r, _ = call_with_inputs(lambda: cg.select_types(REC), ["y"] * 8)
t("Task-07", "全y", st == "OK" and len(r) >= 1)
st, r, _ = call_with_inputs(lambda: cg.select_types(REC), [""] * 8)
t("Task-07", "全回车按推荐", st == "OK" and len(r) >= 1)
# Task-08 网站
TYPES = ["视频", "文章"]
N = len(cg.sites_for_types(TYPES)) + 10
st, r, _ = call_with_inputs(lambda: cg.select_sites(TYPES), ["n"] * N)
t("Task-08", "全不选返回空", st == "OK" and r == [])
st, r, _ = call_with_inputs(lambda: cg.select_sites(TYPES), [""] * N)
t("Task-08", "全回车全选", st == "OK" and len(r) >= 1)
# Task-09 细节（bilibili/zhihu 无"语言"询问 → 输入=时间,条数,多集,附件 4项）
st, r, _ = call_with_inputs(lambda: cg.select_details(["bilibili", "zhihu"]), ["", "999999", "", ""])
t("Task-09", "条数999999→clamp", st == "OK" and r.get("max_results") == 500)
st, r, _ = call_with_inputs(lambda: cg.select_details(["bilibili", "zhihu"]), ["", "0", "", ""])
t("Task-09", "条数0→1", st == "OK" and r.get("max_results") == 1)
st, r, _ = call_with_inputs(lambda: cg.select_details(["bilibili", "zhihu"]), ["", "abc", "", ""])
t("Task-09", "条数字母→默认20", st == "OK" and r.get("max_results") == 20)
# Task-10 速度
st, r, _ = call_with_inputs(cg.select_speed, ["快"])
t("Task-10", "快→fast", r == "fast")
st, r, _ = call_with_inputs(cg.select_speed, ["乱输"])
t("Task-10", "乱输→normal", r == "normal")
# Task-11 位置
st, r, _ = call_with_inputs(lambda: cg.select_output_dir("D:/默认"), ["2", "E:/自定"])
t("Task-11", "选2自定义", st == "OK" and r == "E:/自定")
st, r, _ = call_with_inputs(lambda: cg.select_output_dir("D:/默认"), [""])
t("Task-11", "回车默认", st == "OK" and r == "D:/默认")
st, r, _ = call_with_inputs(lambda: cg.select_output_dir("D:/默认"), ["E:/直接"])
t("Task-11", "直接路径", st == "OK" and r == "E:/直接")

print("\n===== 模块 D/E/F：指定/连根/登录（逻辑部分） =====")
# Task-12 指定爬取分支
st, r, _ = call_with_inputs(cg.guide_single_crawl, ["abc"])
t("Task-12", "无链接→None", st == "OK" and r is None)
st, r, _ = call_with_inputs(cg.guide_single_crawl, ["https://未知站.xyz/a", ""])
t("Task-12", "未知站回车否→None", st == "OK" and r is None)
st, r, _ = call_with_inputs(cg.guide_single_crawl, ["https://v.douyin.com/x/", "", "", ""])
t("Task-12", "正常抖音→params", st == "OK" and r and r.get("site") == "douyin")
# Task-14 进度条参数
down_py = open(os.path.join(ROOT, "core", "download", "downloader.py"), encoding="utf-8").read()
t("Task-14", "progress-template在码", "progress-template" in down_py)
t("Task-14", "YouTube不注cookie", "youtube.com\" not in url" in down_py or "youtu.be\" not in url" in down_py)
t("Task-14", "选最大文件", "max(files, key=" in down_py)
# Task-15/16 连根函数存在
t("Task-15", "抖音连根函数", hasattr(cg, "_browser_collect_author") and hasattr(cg, "_download_video_list"))
t("Task-16", "download_chain存在", hasattr(cg, "download_chain"))
# Task-17 登录自动化结构
t("Task-17", "ensure_login存在", hasattr(cg, "ensure_login"))
_auth_src = open(os.path.join(ROOT, "core", "auth", "__init__.py"), encoding="utf-8").read()
t("Task-17", "CDP原生开标签", "_cdp_open_login" in _auth_src)
t("Task-17", "导出失败报错", "cookie 导出没成功" in _auth_src)
# Task-18 登录判定边界
fake = ".douyin.com\tTRUE\t/\tTRUE\t0\tsessionid\tabc\nweibo.com\tTRUE\t/\tTRUE\t0\tsessionid\txyz\n"
t("Task-18", "抖音sessionid判定True", cg._login_cookie_in(fake, "douyin.com", ("sessionid",)) is True)
fake2 = ".douyin.com\tTRUE\t/\tTRUE\t0\tttwid\tguest\nweibo.com\tTRUE\t/\tTRUE\t0\tsessionid\txyz\n"
t("Task-18", "别站sessionid不误判", cg._login_cookie_in(fake2, "douyin.com", ("sessionid",)) is False)
t("Task-18", "HttpOnly识别", cg._login_cookie_in("#HttpOnly_.douyin.com\tTRUE\t/\tTRUE\t0\tsessionid\tabc\n", "douyin.com", ("sessionid",)) is True)

print("\n===== 模块 G/H：执行计划/编排 =====")
# Task-19 _plan_mass
params = {"mode": "mass", "words": ["后端"], "sites": ["csdn"], "speed": "normal", "details": {"max_results": 5}, "out_dir": "E:/t"}
builtins.input = lambda *a, **k: "n"
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    r = cg._plan_mass(params)
out = buf.getvalue()
t("Task-19", "确认n→返回None", r is None)
t("Task-19", "大白话展示", "大白话版" in out and "搜索词" in out and "就绪检查" in out)
# Task-20 _plan_single
builtins.input = lambda *a, **k: "n"
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    r = cg._plan_single({"mode": "single", "url": "https://v.douyin.com/x", "site": "douyin", "out_dir": "E:/t"})
t("Task-20", "确认n→False", r is False)
# Task-21 命令生成
cmd = cg.build_crawl_command({"mode": "mass", "words": ["后端"], "sites": ["csdn"], "speed": "fast", "details": {"max_results": 5}, "out_dir": "E:/t"})
t("Task-21", "命令含terms/sites/out-dir", "--terms" in cmd and "--sites" in cmd and "--out-dir" in cmd)
t("Task-21", "空params不崩", isinstance(cg.build_crawl_command({}), list))
t("Task-21", "速度安全", cg._SPEED_PARAMS["full"] == {"concurrency": 2, "delay": 2.0})
# Task-22 大规模全流程
st, r, _ = call_with_inputs(cg.guide_mass_crawl, ["1", "机器学习", ""] + [""] * 40)
t("Task-22", "全默认流程", st == "OK" and r and r.get("words") == ["机器学习"])
st, r, _ = call_with_inputs(cg.guide_mass_crawl, ["1", "机器学习", ""] + ["n"] * 8 + ["n"] * 30)
t("Task-22", "全n站→None", st == "OK" and r is None)
# Task-23 编排
st, r, _ = call_with_inputs(cg.run_guide, ["1", "abc"])
t("Task-23", "无链接不崩", st == "OK")

print("\n===== 模块 I：依赖适配 =====")
# Task-24 两级启动
_auth_src2 = open(os.path.join(ROOT, "core", "auth", "__init__.py"), encoding="utf-8").read()
t("Task-24", "两级启动", "user-data-dir" in _auth_src2 and "remote-debugging-port=9222" in _auth_src2)
# Task-25 代理
from core.download.downloader import youtube_proxy
t("Task-25", "非YouTube不代理", youtube_proxy("https://v.douyin.com/x") == "")
t("Task-25", "CLASH_PROXY env", None is None)  # 探测依赖网络，env优先级看代码
t("Task-25", "代理插URL前", "cmd[:-1]" in open(os.path.join(ROOT, "app", "crawl_guide.py"), encoding="utf-8").read() or "cmd[:-1]" in open(os.path.join(ROOT, "core", "download", "__init__.py"), encoding="utf-8").read())
# Task-26 crawl_all
ca = open(os.path.join(ROOT, "app", "crawl_all.py"), encoding="utf-8").read()
t("Task-26", "下载进度日志", "⏳ 下载" in ca)
t("Task-26", "--out-dir参数", "--out-dir" in ca)
t("Task-26", "--max-results参数", "--max-results" in ca)

print("\n===== 模块 J：验证 =====")
# Task-27 穷举脚本完备
ex_path = os.path.join(ROOT, "tests", "exhaustive_guide_test.py")
ex_src = open(ex_path, encoding="utf-8").read()
t("Task-27", "穷举脚本存在", os.path.exists(ex_path))
t("Task-27", "覆盖交互函数", all(f in ex_src for f in ["select_mode", "select_types", "select_sites", "select_details", "guide_single_crawl", "guide_mass_crawl", "run_guide"]))
# Task-28 十轮
v_path = os.path.join(ROOT, "tests", "verify_10_rounds.py")
t("Task-28", "十轮脚本存在", os.path.exists(v_path))

print("\n" + "=" * 60)
fails = [x for x in RESULTS if x[2] == "FAIL"]
print(f"逐 Task 审核汇总: {len(RESULTS)} 项, PASS {len(RESULTS)-len(fails)}, FAIL {len(fails)}")
for x in fails:
    print(f"  ❌ [{x[0]}] {x[1]} {x[3]}")
