# -*- coding: utf-8 -*-
"""领域逻辑层：词库整理 / 词性格 / 站映射 / 登录判定（纯逻辑，无交互输入）。

从旧版引导脚本抽离（架构重构 T11，见 docs/directory-contract.md）。
core 内部单向依赖：interaction/domain → download → bridges/engines。
"""
import os
import re

# 内置词表路径（core/domain/__init__.py → 仓库根 → config/seeds/）
VOCAB_FULL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config", "seeds", "vocab_terms_full.txt")

def _split_terms(text: str) -> list:
    """把一段乱文本拆成候选词（分隔符 + 序号前 + 中英混合空格）。"""
    parts = re.split(r"[,，、;；\n\r\t]+", text)
    words = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # 中文/数字 空格拆分（"机器学习 transformer"→两词；"machine learning"不拆）
        sub = re.split(r"(?<=[一-鿿])\s+(?=[一-鿿a-zA-Z0-9])|(?<=[a-zA-Z0-9])\s+(?=[一-鿿])", p)
        for s in sub:
            for s2 in re.split(r"\s+(?=\d+[\.、)）])", s):
                s2 = s2.strip()
                s2 = re.sub(r"^\s*\d+[\.、\)）]\s*", "", s2)
                s2 = s2.strip(" '\"（）()【】[]《》“”‘’")
                if s2:
                    words.append(s2)
    return words


def _is_junk(text: str) -> bool:
    """去噪：纯数字/数字开头长串/超长无分隔句子。"""
    if not text:
        return True
    if text.isdigit():
        return True
    if re.match(r"^\d{3,}[一-鿿]", text):  # 数字开头+中文（如 12345长串）
        return True
    if re.match(r"^\d+\s+\S", text) and len(text) > 15:
        return True
    # 超长中文无空格（>30字）→ 是句子不是词
    if len(text) > 30 and " " not in text and re.fullmatch(r"[一-鿿]+", text):
        return True
    if len(text) > 40 and (text.count(" ") > 8 or not re.search(r"[a-zA-Z一-鿿]", text)):
        return True
    return False


def clean_term_list(raw_text: str) -> dict:
    """整理用户给的词库（乱格式），返回 {words:[...], urls:[...]}。"""
    words = []
    urls = []
    seen_w = set()
    seen_u = set()
    for m in re.finditer(r"https?://[^\s,，、;；，、\n]+", raw_text):
        u = m.group(0).strip("。.,，；;")
        if u and u not in seen_u:
            seen_u.add(u)
            urls.append(u)
    text = re.sub(r"https?://[^\s,，、;；，、\n]+", " ", raw_text)
    for t in _split_terms(text):
        if _is_junk(t):
            continue
        key = t.lower()
        if key not in seen_w:
            seen_w.add(key)
            words.append(t)
    return {"words": words, "urls": urls}


def load_builtin_vocab() -> list:
    """内置 2740 专业词表（跳过 # 注释/标题行）。"""
    if not os.path.exists(VOCAB_FULL):
        return []
    words = []
    for line in open(VOCAB_FULL, encoding="utf-8"):
        w = line.strip()
        if not w or w.startswith("#"):
            continue
        if w not in words:
            words.append(w)
    return words


_ACADEMIC = ("论文", "综述", "transformer", "attention", "llm", "大语言模型",
             "深度学习", "神经网络", "强化学习", "图神经", "gnn", "nlp", "自然语言",
             "computer vision", "计算机视觉", "generative", "生成式", "diffusion",
             "reinforcement", "机器学习", "machine learning", "deep learning", "rag")


_TUTORIAL = ("教程", "入门", "学习", "从零", "基础", "实战", "课程", "教学",
             "python", "前端", "后端", "开发", "编程", "tutorial", "guide",
             "getting started")


_HOT = ("热点", "最新", "大模型", "agi", "芯片", "大会", "发布", "趋势", "未来",
        "突破", "openai", "gpt", "人工智能", "智能体", "机器人", "行业", "应用")


_CODE = ("框架", "库", "sdk", "api", "源码", "github", "开源", "代码", "部署",
         "工具", "pytorch", "tensorflow", "flask", "django", "react", "vue",
         "docker", "kubernetes", "k8s")


ALL_TYPES = ("论文", "视频", "文章", "代码", "数据集", "课程", "文档", "题库")


_PERSONALITY_REC = {
    "学术": {"论文": True, "视频": True, "文章": True, "代码": False, "数据集": True, "课程": False, "文档": False, "题库": False},
    "教程": {"论文": False, "视频": True, "文章": True, "代码": True, "数据集": False, "课程": True, "文档": True, "题库": False},
    "热点": {"论文": False, "视频": True, "文章": True, "代码": False, "数据集": False, "课程": False, "文档": False, "题库": False},
    "代码": {"论文": False, "视频": False, "文章": True, "代码": True, "数据集": True, "课程": False, "文档": True, "题库": False},
    "通用": {"论文": True, "视频": True, "文章": True, "代码": True, "数据集": True, "课程": True, "文档": True, "题库": False},
}


_PERSONALITY_DESC = {
    "学术": "偏学术研究（前沿论文多）", "教程": "偏学习教程（教学视频和入门文章多）",
    "热点": "偏热点资讯（最新新闻和讨论多）", "代码": "偏代码工具（开源项目和框架多）",
    "通用": "通用词（各类型都有）",
}


def detect_personality(term: str) -> str:
    """识别词性格（长词加权）。"""
    t = term.lower()
    scores = {
        "学术": sum(len(k) for k in _ACADEMIC if k in t),
        "教程": sum(len(k) for k in _TUTORIAL if k in t),
        "热点": sum(len(k) for k in _HOT if k in t),
        "代码": sum(len(k) for k in _CODE if k in t),
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "通用"


def recommend_types(personality: str) -> dict:
    """性格 → 8 类型是否推荐。"""
    return dict(_PERSONALITY_REC.get(personality, _PERSONALITY_REC["通用"]))


def describe_personality(personality: str) -> str:
    return _PERSONALITY_DESC.get(personality, "通用")


SITE_TYPE_MAP = {
    "论文": ["arxiv", "dblp", "semanticscholar", "paperswithcode", "aclanthology",
             "openreview", "neurips", "icml", "iclr", "google_scholar"],
    "视频": ["bilibili", "youtube", "douyin"],
    "文章": ["juejin", "csdn", "zhihu", "segmentfault", "infoq", "sspai", "36kr",
             "medium", "oschina", "hackernews", "weibo", "alignmentforum", "xiaohongshu"],
    "代码": ["github_topics", "gitee"],
    "数据集": ["huggingface", "kaggle"],
    "课程": ["coursera", "edx", "khanacademy"],
    "文档": ["cursor", "claude_code_docs", "opencode"],
    "题库": ["leetcode"],
}


SITE_SORT_OPTIONS = {
    "bilibili": ["综合", "播放量", "最新", "点赞"], "douyin": ["综合", "点赞", "最新"],
    "youtube": ["相关", "观看次数", "上传时间"], "zhihu": ["综合", "赞同", "最新"],
    "github_topics": ["star数", "最新"], "gitee": ["star数", "最新"],
    "arxiv": ["最新", "相关"], "dblp": ["最新", "相关"],
    "juejin": ["综合", "最新", "热门"], "csdn": ["综合", "最新", "热门"],
    "segmentfault": ["综合", "最新"], "hackernews": ["综合", "最新"],
    "infoq": ["综合", "最新"], "36kr": ["综合", "最新"], "sspai": ["综合", "最新"],
    "medium": ["综合", "最新"], "oschina": ["综合", "最新"], "weibo": ["综合", "最新"],
    "kaggle": ["综合", "最新"], "huggingface": ["综合", "最新"],
}


DEFAULT_SORT = ["综合", "最新"]


_SORT_SORTABLE = {"arxiv", "github_topics"}


SITE_SUBFORMS = {
    "douyin": ["短视频", "图集", "图文", "纯图+音乐"],
    "xiaohongshu": ["图文笔记", "图集", "视频笔记"],
    "bilibili": ["长视频", "专栏文章"],
    "weibo": ["图文", "视频"],
    "zhihu": ["问答", "文章", "视频"],
}


_DOMAIN_SITE = {
    "bilibili.com": "bilibili", "douyin.com": "douyin", "youtube.com": "youtube",
    "xiaohongshu.com": "xiaohongshu", "xhslink.com": "xiaohongshu",
    "juejin.cn": "juejin", "csdn.net": "csdn", "zhihu.com": "zhihu",
    "segmentfault.com": "segmentfault", "medium.com": "medium", "oschina.net": "oschina",
    "weibo.com": "weibo", "infoq.cn": "infoq", "36kr.com": "36kr", "sspai.com": "sspai",
    "arxiv.org": "arxiv", "github.com": "github_topics", "gitee.com": "gitee",
    "huggingface.co": "huggingface", "kaggle.com": "kaggle",
    "leetcode.cn": "leetcode", "leetcode.com": "leetcode",
    "coursera.org": "coursera", "edx.org": "edx", "khanacademy.org": "khanacademy",
    "cursor.com": "cursor", "platform.claude.com": "claude_code_docs",
    "opencode.ai": "opencode", "openreview.net": "openreview",
    "neurips.cc": "neurips", "icml.cc": "icml", "iclr.cc": "iclr",
    "dblp.org": "dblp", "aclanthology.org": "aclanthology",
    "semanticscholar.org": "semanticscholar", "news.ycombinator.com": "hackernews",
    "huxiu.com": "huxiu", "alignmentforum.org": "alignmentforum",
}


def site_sort_options(site: str) -> list:
    return SITE_SORT_OPTIONS.get(site, DEFAULT_SORT)


def sites_for_types(types: list) -> list:
    sites, seen = [], set()
    for t in types:
        for s in SITE_TYPE_MAP.get(t, []):
            if s not in seen:
                seen.add(s)
                sites.append(s)
    return sites


def type_for_site(site: str) -> str:
    for t, lst in SITE_TYPE_MAP.items():
        if site in lst:
            return t
    return "文章"


def recognize_site(url: str) -> str:
    """从链接认出网站。"""
    u = url.lower()
    for domain, site in _DOMAIN_SITE.items():
        if domain in u:
            return site
    return "未知"


NEED_LOGIN = {
    "douyin": ("https://www.douyin.com/", "douyin.com", ("sessionid",)),
    "xiaohongshu": ("https://www.xiaohongshu.com/", "xiaohongshu.com", ("web_session",)),
    "weibo": ("https://weibo.com/", "weibo.com", ("sub", "wb_persist_fetch", "wbpsess")),
    "bilibili": ("https://www.bilibili.com/", "bilibili.com", ("sessdata",)),
    "leetcode": ("https://leetcode.cn/", "leetcode.cn", ("leetcode_session",)),
    "gitee": ("https://gitee.com/", "gitee.com", ("gitee_session",)),
    "zhihu": ("https://www.zhihu.com/", "zhihu.com", ("z_c0",)),
    "khanacademy": ("https://www.khanacademy.org/", "khanacademy.org", ("kaas", "kc_session")),
}


def _login_cookie_in(raw: str, domain: str, keys: tuple) -> bool:
    """从 Netscape cookie 文本判断该域名是否含关键登录 cookie（按列匹配）。

    纯函数，便于验证边界：别站的同名 cookie、匿名 cookie、#HttpOnly_ 行。
    """
    for line in raw.splitlines():
        line = line.rstrip("\r")
        if not line:
            continue
        # #HttpOnly_ 是 HttpOnly cookie 前缀（不算注释）；其余 # 开头才是注释
        if line.startswith("#") and not line.startswith("#HttpOnly_"):
            continue
        if line.startswith("#HttpOnly_"):
            line = line[len("#HttpOnly_"):]
        fields = line.split("\t")
        if len(fields) < 6:
            continue
        if domain not in fields[0].lower():
            continue
        name = fields[5].lower()
        if any(k in name for k in keys):
            return True
    return False


def _has_login_cookie(site: str) -> bool:
    """是否已持有该站"真正登录态"（关键 cookie，如抖音 sessionid）。

    修复：匿名 cookie（ttwid/__ac_nonce）不算登录，否则 yt-dlp 下载仍失败。
    """
    if site not in NEED_LOGIN:
        return True  # 不需要登录的站
    _, domain, keys = NEED_LOGIN[site]
    from core.auth.cookie_util import _cookie_file
    cf = _cookie_file()
    if not cf or not os.path.exists(cf):
        return False
    try:
        raw = open(cf, "r", encoding="utf-8", errors="replace").read()
    except Exception:  # noqa: BLE001
        return False
    return _login_cookie_in(raw, domain.lower(), keys)
