"""关键词相关性判断 — 用 yake 自动提取标题关键词，辅助"内容与搜索词相关"判定。

用途：替代手写 RELATED 词表（原 cdp_search 等靠人工维护），
对搜索结果标题自动提关键词，与搜索词词元比对，相关则保留。

局限：纯词法（无同义），"transformer"搜不出"注意力机制"标题——
该能力由语义扩展层（semantic_expansion）补齐。
"""
import re
from functools import lru_cache

_CACHE = {}

# 中英核心术语映射（AI/ML 常用，词法层解决中英不对应；语义扩展层补框架/生态同义）
_TERM_MAP = {
    "machine learning": ["机器学习"],
    "deep learning": ["深度学习"],
    "reinforcement learning": ["强化学习"],
    "neural network": ["神经网络"],
    "artificial intelligence": ["人工智能"],
    "natural language": ["自然语言"],
    "large language": ["大语言", "大模型"],
    "computer vision": ["计算机视觉"],
    "transformer": ["注意力机制", "attention"],
    "convolutional": ["卷积"],
    "generative": ["生成式"],
    "recommendation": ["推荐"],
    "data mining": ["数据挖掘"],
}

# CS/AI 技术特征词（判断内容是否"技术相关"，半相关保留，纯无关丢弃）
_CS_HINTS = (
    "ai", "智能", "模型", "学习", "算法", "数据", "系统", "编程", "代码", "开发",
    "语言", "网络", "搜索", "推荐", "分类", "识别", "预测", "生成", "机器",
    "神经", "深度", "强化", "训练", "框架", "工具", "技术", "架构", "应用",
    "分析", "计算", "信息", "软件", "硬件", "芯片", "论文", "研究", "工程",
    "llm", "gpt", "bert", "nlp", "agent", "token", "prompt", "vector", "model",
)


def _is_tech_content(title: str) -> bool:
    """标题含 CS/AI 技术特征词 → 半相关保留。"""
    tl = title.lower()
    return any(h in tl for h in _CS_HINTS)


def _term_variants(term: str) -> list:
    """搜索词的中英文变体（machine learning → [machine learning, 机器学习]）。"""
    tl = term.lower()
    out = [tl]
    for en, cn in _TERM_MAP.items():
        if en in tl:
            out.extend(cn)
        elif any(c in tl for c in cn):
            out.append(en)
    return out


def _get_extractor(lan: str = "zh"):
    """yake 提取器缓存（实例化较重，复用）。"""
    if lan not in _CACHE:
        try:
            from yake import KeywordExtractor
            _CACHE[lan] = KeywordExtractor(lan=lan, top=8, stopwords=None)
        except Exception:  # noqa: BLE001
            _CACHE[lan] = None
    return _CACHE[lan]


def extract_keywords(text: str, lan: str = "zh", top: int = 5) -> list:
    """yake 提取文本关键词（自动判断中英文 lan）。"""
    if not text:
        return []
    if re.search(r"[一-鿿]", text):
        lan = "zh"
    ex = _get_extractor(lan)
    if not ex:
        return []
    try:
        return [k for k, _ in ex.extract_keywords(text)][:top]
    except Exception:  # noqa: BLE001
        return []


def is_relevant_by_keywords(title: str, term: str) -> bool:
    """标题与搜索词的相关性判断：相关/半相关保留，纯无关丢弃。

    保留条件（任一）：
      1. 标题含搜索词中英变体
      2. 标题含语义扩展词（T12 后）
      3. yake 标题关键词含搜索词变体
      4. 标题含 CS/AI 技术特征词（半相关）
    空标题无法判断 → True 保留（宁留勿误杀）。
    """
    if not title or not term:
        return True
    tl = title.lower()
    # 分词规范化：连字符/下划线/斜杠/点 → 空格（仓库名 vue-access-control 才能匹配 "access control"）
    tl_norm = re.sub(r"[-_/\.]+", " ", tl)
    variants = _term_variants(term)
    if any(v in tl for v in variants) or any(v in tl_norm for v in variants):
        return True  # 标题含搜索词或其同义/中文变体
    # 仓库名连写兜底（accesscontrol、node_acl）：搜索词所有词元都出现在标题
    _words = [w for w in re.split(r"\s+", variants[0]) if len(w) >= 3]
    if _words and all(w in tl for w in _words):
        return True
    # 语义同义词扩展（如 transformer→attention；TensorFlow→ML 生态）
    from core.domain.semantic_expansion import expand_terms
    expanded = expand_terms(term)
    if any(w in tl for w in expanded) or any(w in tl_norm for w in expanded):
        return True
    # yake 标题关键词辅助
    kws = extract_keywords(title)
    blob = " ".join(k.lower() for k in kws)
    if any(v in blob for v in variants):
        return True
    # 半相关：技术内容保留（避免误杀 LLM/BERT/AI 相关）
    return _is_tech_content(tl)
