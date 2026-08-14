# -*- coding: utf-8 -*-
"""交互层：问用户/收集选择（select_*/guide_*），无下载实现。

从旧版引导脚本抽离（架构重构 T10，见 docs/directory-contract.md）。
依赖：core/domain（逻辑）+ 自身状态 _SORT_PICKED。
"""
import builtins as _builtins
import os
import re

# 仓库根（core/interaction/__init__.py → 上三级）
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.domain import clean_term_list, load_builtin_vocab, detect_personality, recommend_types, describe_personality, sites_for_types, site_sort_options, recognize_site, ALL_TYPES, SITE_TYPE_MAP, SITE_SUBFORMS, _SORT_SORTABLE

def _safe_input(prompt: str = "") -> str:
    try:
        return _builtins.input(prompt)  # 动态读 builtins.input：外部 mock(测试) 仍生效
    except EOFError:
        print()
        return ""
    except KeyboardInterrupt:
        print("\n已取消，退出")
        raise SystemExit(0)


def get_terms_from_input() -> list:
    """来源①：自己输入词。"""
    raw = input("  输入词（用逗号/空格/换行隔开，乱点也行）：\n  ")
    return clean_term_list(raw)["words"]


def get_terms_from_file() -> list:
    """来源②：导入词库文件（乱格式自动整理）。"""
    path = input("  词库文件路径（txt，每行一个词或乱格式都行）：").strip().strip('"')
    if os.path.isfile(path):  # 只认文件；目录/不存在 → 走粘贴兜底（防 PermissionError）
        raw = open(path, encoding="utf-8", errors="replace").read()
    else:
        print("  ⚠ 不是有效文件（目录/不存在），请直接把词粘进来（逗号/换行隔开）：")
        raw = input("  ")
    return clean_term_list(raw)["words"]


def get_terms_from_builtin() -> list:
    """来源③：内置 2740 专业词表。"""
    words = load_builtin_vocab()
    print(f"  ✅ 载入内置专业词表 {len(words)} 个词")
    return words


def select_term_source() -> list:
    """三种词来源交互选择 → 返回词清单（含预览确认）。"""
    print("\n━━━ 词从哪里来？━━━")
    print("  ① 自己输入几个词")
    print("  ② 导入词库文件（乱格式我自动整理）")
    print("  ③ 用内置 2740 个专业词表")
    choice = input("  选 1/2/3（回车=1）：").strip() or "1"
    if choice == "1":
        words = get_terms_from_input()
    elif choice == "2":
        words = get_terms_from_file()
    else:
        words = get_terms_from_builtin()
    if words:
        print(f"\n  整理出 {len(words)} 个词：")
        for i, w in enumerate(words[:10], 1):
            print(f"    {i}. {w}")
        if len(words) > 10:
            print(f"    ... 共 {len(words)} 个")
        confirm = input("  确认用这些词？(y=用 / 输入序号或词名可删)：").strip()
        if confirm.lower() not in ("", "y", "yes", "是", "确认"):
            for c in re.split(r"[,\s，、]+", confirm):
                if c.isdigit() and 1 <= int(c) <= len(words):
                    words[int(c) - 1] = None
                elif c:
                    words = [w for w in words if w != c]
            words = [w for w in words if w]
            print(f"  ✅ 确认后剩 {len(words)} 个词")
    return words


_SORT_PICKED = {}  # 本次大规模选择的 站→排序


def select_speed(last: str = "") -> str:
    print("\n━━━ 爬多快？━━━")
    print("  🐇 快速：安全范围内稍快（想快点看效果，绝不踩反爬线）")
    print("  🚶 标准：正常稳妥（日常推荐）")
    print("  🐢 全量：慢慢爬（最大规模时用，最稳）")
    _def = {"fast": "快", "normal": "标准", "full": "全量"}.get(last, "标准")
    c = input(f"  选 快/标准/全量（回车={_def}）：").strip()
    r = {"快": "fast", "快速": "fast", "标准": "normal", "全量": "full"}.get(c)
    if r:
        return r
    return last if last in ("fast", "normal", "full") else "normal"


def _parse_yesno(prompt: str, default: bool = True) -> bool:
    c = input(f"  {prompt}（y/n，回车={'是' if default else '否'}）：").strip().lower()
    if c in ("y", "yes", "是", "要", "全", "一起"):
        return True
    if c in ("n", "no", "否", "不要", "不"):
        return False
    return default


def select_output_dir(default_dir: str, prompt: str = "保存到哪里？") -> str:
    """选择输出位置：默认 / 自定义路径，选完提示确认（参考 video_tools --out-dir）。"""
    print(f"\n━━━ {prompt}━━━")
    print(f"  ① 默认：{default_dir}")
    print(f"  ② 自定义路径（直接输入完整路径）")
    c = input("  选择（回车=默认）：").strip().strip('"')
    if c in ("2", "②", "自定义", "自定义路径"):
        out = input("  请输入完整保存路径：").strip().strip('"').strip()
        if not out:
            print("  ⚠ 没输入路径，用默认")
            out = default_dir
    elif c in ("1", "①") or not c:
        out = default_dir
    else:
        # 直接输入了路径（跳过选择步骤）
        out = c
    print(f"  ✓ 将保存到：{out}")
    return out


def guide_single_crawl() -> dict:
    print("\n━━━ 指定爬取（点菜式）━━━")
    raw = input("  发链接（视频/文章/网页都行，分享口令也行）：").strip()
    # 从粘贴内容提取真正的链接（抖音/小红书/B站分享口令含短链）
    m = re.search(r"https?://[^\s，,；;]+", raw)
    if m:
        url = m.group(0).rstrip("/,.;，。")
        if url != raw:
            print(f"  ✓ 从分享内容提取出链接：{url}")
    else:
        url = raw
    if not url.startswith("http"):
        print("  ⚠ 没检测到链接。请重新粘贴：完整链接，或抖音/小红书/B站分享口令")
        return None
    site = recognize_site(url)
    print(f"  认出是：{site} 的链接")
    if site == "未知":
        if not _parse_yesno("没认出来是哪个网站，换链接或手动填站名？", default=False):
            print("  ⚠ 换一个认识的链接再试（B站/抖音/小红书/知乎/掘金等）")
            return None
        site = input("  手动填站名（如 bilibili/douyin）：").strip() or site
        if site == "未知":
            print("  ⚠ 没填有效站名，取消本次爬取")
            return None
    chain = False
    if site in ("bilibili", "douyin", "youtube", "xiaohongshu", "weibo"):
        chain = _parse_yesno("这个内容有没有【系列/作者更多】？要不要连根一起爬？")
    speed = select_speed()
    out_dir = select_output_dir(os.path.join(BASE, "知识库", "指定爬取"))
    return {"mode": "single", "url": url, "site": site, "chain": chain,
            "speed": speed, "out_dir": out_dir}


def select_types(rec: dict, last: list = None) -> list:
    """选择内容类型；last=上次选择（有偏好时回车按上次，无偏好按推荐）。"""
    print("\n━━━ 要哪种内容？━━━（推荐已打勾，可加可减）")
    if last:
        print(f"      （上次选了：{'、'.join(last)}，回车可复用）")
    chosen = []
    for t in ALL_TYPES:
        mark = "☑上次" if (last and t in last) else ("☑推荐" if rec.get(t) else "☐")
        c = input(f"  {mark} {t}？(y要/n不要，回车=按{'上次' if last else '推荐'})：").strip().lower()
        if c in ("y", "yes", "是", "要"):
            chosen.append(t)
        elif c in ("n", "no", "否", "不要"):
            continue
        elif last and t in last:
            chosen.append(t)      # 有偏好：回车=按上次
        elif not last and rec.get(t):
            chosen.append(t)      # 无偏好：回车=按推荐
    if not chosen:
        print("  ⚠ 一个都没选，默认按推荐")
        chosen = [t for t in ALL_TYPES if rec.get(t)] or ["文章"]
    # 混合站告知（含子形态类型；当前默认全抓，不假装询问"要不要都抓"）
    for s in SITE_SUBFORMS:
        if s in sites_for_types(chosen):
            print(f"\n  ℹ {s} 是混合站，里面有：{' / '.join(SITE_SUBFORMS[s])}（默认全抓）")
    return chosen


def select_sites(types: list, last: list = None) -> list:
    """选择网站；last=上次选择（有偏好时回车按上次爬过的，无偏好回车=爬）。"""
    sites = sites_for_types(types)
    print(f"\n━━━ 网站（{len(sites)} 个匹配，一个都不选=取消本次）━━━")
    global _SORT_PICKED
    _SORT_PICKED = {}  # 重置本次排序选择
    if last:
        print(f"      （上次选了：{'、'.join(last)}，回车可复用上次）")
    keep = []
    for s in sites:
        _tag = "（上次爬过）" if (last and s in last) else ""
        c = input(f"  爬 {s} 吗？{_tag}(y/n，回车={'按上次' if last else '爬'})：").strip().lower()
        if c in ("n", "no", "否", "不要"):
            continue
        if c in ("y", "yes", "是", "要"):
            keep.append(s)
        elif last is None:
            keep.append(s)      # 无偏好：回车=爬
        elif s in last:
            keep.append(s)      # 有偏好：回车=上次爬过
        # else: 有偏好但上次没爬 → 回车=不爬
        opts = site_sort_options(s)
        if len(opts) > 1 and s in keep:
            srt = input(f"    {s} 按什么排？({'/'.join(opts)}，回车=推荐{opts[0]})：").strip()
            if not srt:
                srt = opts[0]
            _SORT_PICKED[s] = srt
            # 诚实标注：仅 arxiv/github 排序真正生效，其余站按默认
            _eff = "排序已生效" if s in _SORT_SORTABLE else "该站排序暂不支持，按默认"
            print(f"    → {s} 按 {srt}（{_eff}）")
    if not keep:
        print("  ⚠ 一个网站都没选，取消本次爬取")
    return keep


def select_details(sites: list, last: dict = None) -> dict:
    print("\n━━━ 细节 ━━━")
    last = last or {}
    d = {}
    if any(s in ("bilibili", "douyin", "youtube", "weibo", "36kr", "infoq", "hackernews",
                 "arxiv", "dblp", "semanticscholar", "zhihu", "juejin", "csdn") for s in sites):
        _def = last.get("time_range", "全部")
        c = input(f"  时间范围？(近1周/近1月/近1年/全部，回车={_def})：").strip()
        d["time_range"] = c or _def
    if any(s in ("youtube", "arxiv", "dblp", "semanticscholar", "medium", "hackernews",
                 "github_topics", "huggingface", "kaggle", "coursera", "edx", "paperswithcode") for s in sites):
        _def = last.get("lang", "都要")
        c = input(f"  语言？(中文/英文/都要，回车={_def})：").strip()
        d["lang"] = c or _def
    _def = last.get("max_results", 20)
    c = input(f"  每个网站拿几条？(10/20/50/100，回车={_def})：").strip()
    n = int(c) if c.isdigit() else _def
    d["max_results"] = max(1, min(n, 500))  # 限 1~500：防 0/超大/负数造成异常请求
    if any(s in ("bilibili", "douyin", "youtube") for s in sites):
        d["video_all_parts"] = _parse_yesno("视频有多集，全部下还是只首集？", default=last.get("video_all_parts", True))
    if any(s in SITE_TYPE_MAP["文章"] + SITE_TYPE_MAP["论文"] for s in sites):
        d["include_attachments"] = _parse_yesno("要不要图片/PDF/代码附件？", default=last.get("include_attachments", False))
    return d


def load_prefs() -> dict:
    import json
    p = os.path.join(BASE, "config", "crawl_prefs.json")
    try:
        if os.path.exists(p):
            return json.load(open(p, encoding="utf-8"))
    except Exception:
        pass
    return {}


def save_prefs(prefs: dict) -> None:
    import json
    p = os.path.join(BASE, "config", "crawl_prefs.json")
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(prefs, f, ensure_ascii=False, indent=1)
    except Exception:
        pass


def select_mode() -> str:
    print("\n━━━ 你要哪种爬法？━━━")
    print("  ① 指定爬取：发链接，爬特定的（可连根爬系列）")
    print("  ② 大规模爬取：选词选站，批量搜")
    c = input("  选 1/2（回车=2）：").strip()
    return c if c in ("1", "2") else "2"  # 非法输入(3/乱输)回默认，不按原样误走


def guide_mass_crawl() -> dict:
    words = select_term_source()
    if not words:
        print("  ⚠ 没有词，无法大规模爬取")
        return None
    p = detect_personality(words[0])
    print(f"\n  📌 词[{words[0]}] 性格：{describe_personality(p)}")
    # 偏好记忆：读上次选择作默认（v2.3.2）
    prefs = load_prefs()
    _last = prefs.get("last", {}) or {}
    types = select_types(recommend_types(p), _last.get("types"))
    sites = select_sites(types, _last.get("sites"))
    if not sites:
        print("  没有选任何网站，本次取消（避免误触发全站爬取）")
        return None
    details = select_details(sites, _last.get("details"))
    speed = select_speed(_last.get("speed", ""))
    out_dir = select_output_dir(os.path.join(BASE, "知识库"), "保存到哪里？(大规模爬取)")
    prefs["last"] = {"types": types, "sites": sites, "speed": speed, "details": details}
    save_prefs(prefs)
    sort_map = {k: v for k, v in _SORT_PICKED.items() if k in _SORT_SORTABLE}
    return {"mode": "mass", "words": words, "types": types, "sites": sites,
            "details": details, "speed": speed, "out_dir": out_dir, "sort_map": sort_map}
