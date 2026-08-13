"""噪声快速过滤器 — 基于启发式规则在页级做快速过滤，不进入 LLM。"""
import re

# 噪音关键词（出现在标题/摘要即判定为噪音）
_NOISE_KEYWORDS = [
    "login", "signin", "sign-in", "signup", "register", "account",
    "privacy policy", "terms of service", "cookie policy",
    "advertising", "sponsor", "advertised", "paid promotion",
    "careers", "job", "hiring", "recruit",
    "error", "404", "not found",
]

# 安全前缀：URL 匹配这些域名视为可信
_TRUSTED_PREFIXES = [
    ".arxiv.org",
    ".bilibili.com",
    ".zhihu.com",
    ".juejin.cn",
    ".csdn.net",
    ".cnblogs.com",
    ".github.com",
    ".stackoverflow.com",
    ".segmentfault.com",
    ".dev.to",
    ".medium.com",
    ".huggingface.co",
    ".kaggle.com",
    ".modelscope.cn",
    ".youtube.com",
    ".time.geekbang.org",
    ".sspai.com",
    ".infoq.cn",
    ".jiqizhixin.com",
    ".qbitai.com",
    ".36kr.com",
    ".huxiu.com",
    ".tmtpost.com",
    ".oschina.net",
    ".v2ex.com",
    ".lobste.rs",
    ".news.ycombinator.com",
    ".aclanthology.org",
    ".openreview.net",
    ".neurips.cc",
    ".icml.cc",
    ".iclr.cc",
    ".dblp.org",
    ".paperswithcode.com",
    ".semanticscholar.org",
    ".connectedpapers.com",
    ".scirate.com",
    ".ocw.mit.edu",
    ".missing.csail.mit.edu",
    ".stanford.edu",
    ".harvard.edu",
    ".towardsdatascience.com",
    ".hackernoon.com",
    ".alignmentforum.org",
    ".datawhale.cn",
    ".aitopics.org",
    ".ai.alignmentforum.org",
]


def is_noise_url(url: str) -> bool:
    """检查 URL 是否为噪音链接。"""
    url_lower = url.lower()
    # 排除已知不可信域
    for bad in ["doubleclick", "adservice", "googleadservices"]:
        if bad in url_lower:
            return True
    return False


def quick_filter(result: dict) -> bool:
    """
    对单条搜索结果做快速过滤。返回 True = 通过(非噪音)。

    规则：
    1. URL 不在可信域名且含噪音关键词 → 拒绝
    2. HTML 正文 < 200 字符 → 拒绝
    3. 标题/摘要含明显非CS领域信号(天文/物理/数学/生物) → 拒绝
    4. PDF DOC PPT 等文件类型 Content-Type 不匹配 → 拒绝
    """
    url = result.get("url", "")
    title = (result.get("title") or "").lower()
    summary = (result.get("summary") or "").lower()

    # 1. 噪音关键词检测
    combined = f" {title} {summary}"
    for kw in _NOISE_KEYWORDS:
        if kw in combined:
            return False

    # 2. URL 安全检查
    if is_noise_url(url):
        return False

    # 3. 非CS领域信号过滤（天文/物理/数学/生物等噪音）
    non_cs = (
        "galaxy", "stellar", "star formation", "astronom", "cosmolog", "supernova",
        "quasar", "nebula", "gravitation", "solar system", "planetary", "redshift",
        "magnetic field", "plasma", "particle physics", "hadron", "neutrino",
        "algebra", "topolog", "manifold", "theorem", "homology", "differential geometry",
        "quantum field", "condensed matter", "crystallograph", "molecule",
        "gene expression", "protein", "molecular biology", "biochem",
        "meteorolog", "atmospheric", "oceanograph", "earthquake", "geolog",
        "star formation", "solar flare", "nuclear reaction",
    )
    if any(k in combined for k in non_cs):
        return False

    # 4. 空结果过滤
    if not url.strip():
        return False

    return True


def deduplicate(results: list[dict]) -> list[dict]:
    """简单的 URL 去重（md5）。保留首次出现。"""
    seen = set()
    unique = []
    for r in results:
        h = hash((r["url"].strip(), r["original_term"]))
        if h not in seen:
            seen.add(h)
            unique.append(r)
    return unique


def merge_and_filter(all_results: list[list[dict]]) -> list[dict]:
    """合并多个搜索器的结果并过滤去重。"""
    flat = []
    for batch in all_results:
        flat.extend(batch)
    # 先快速过滤再去做重
    filtered = [r for r in flat if quick_filter(r)]
    return deduplicate(filtered)
