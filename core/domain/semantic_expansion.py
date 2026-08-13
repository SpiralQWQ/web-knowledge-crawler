"""语义扩展（占位）— 2740 词语义相似词扩展，扩大限定词召回。

T11 将用 text2vec 生成扩展词表；当前占位返回空（词法阶段不扩展）。
"""
import os

# 扩展词表文件（T11 生成）
_EXP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "..", "config", "seeds", "semantic_expansion.txt")


def expand_terms(term: str, top: int = 5) -> list:
    """返回某搜索词的语义相似词（当前占位：文件未生成则空）。"""
    try:
        if not os.path.exists(_EXP_FILE):
            return []
        with open(_EXP_FILE, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if parts and parts[0].lower() == term.lower():
                    return [p for p in parts[1:top + 1] if p]
    except Exception:  # noqa: BLE001
        return []
    return []
