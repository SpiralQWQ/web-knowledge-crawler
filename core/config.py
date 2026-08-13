"""全局配置：读取 config/collector.yaml + 环境变量覆盖（KC_BASE 等）。"""
import os

try:
    import yaml
except ImportError:
    yaml = None

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))  # .../collector
_REPO_ROOT = os.path.dirname(_THIS_DIR)  # 仓库根（collector 的上一级，config/.env 都在这里）

# P1：先加载 .env（含 KC_BASE）再决定 BASE——否则 .env 的 KC_BASE 被静默忽略，与 media_collect 不一致，
# 会导致两模块知识库输出到不同根/盘符
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(_REPO_ROOT, ".env"))
except ImportError:
    pass

BASE = os.environ.get("KC_BASE") or _REPO_ROOT  # 数据/知识库根（可被 .env KC_BASE 覆盖）
CFG_PATH = os.path.join(_REPO_ROOT, "config", "collector.yaml")  # 配置文件始终随代码仓库


def rel_path(path: str) -> str:
    """相对 BASE 的路径；跨盘（KC_KB_FALLBACK D: 回退/KC_BASE 异盘）relpath 抛 ValueError 时回退绝对路径。
    P2/P3：防跨盘时整批崩溃或误记 fail。"""
    try:
        return os.path.relpath(path, BASE)
    except ValueError:
        return path

_CFG = {}
if yaml is not None:
    try:
        with open(CFG_PATH, encoding="utf-8") as f:
            _CFG = yaml.safe_load(f) or {}
    except Exception:
        _CFG = {}


def get(key, default=None):
    return _CFG.get(key, default)


KB_MIN_FREE_GB = 20  # 知识库所在盘剩余空间低于该值 → 回退到 D 盘（用户规则）


def _kb_root() -> str:
    """知识库根目录：E 盘剩余 <20GB 时回退到 D 盘（同架构/命名），可用 KC_KB_FALLBACK 覆盖。"""
    root = os.path.join(BASE, get("knowledge_root", "知识库"))
    try:
        import shutil
        free_gb = shutil.disk_usage(os.path.dirname(root)).free / (1024 ** 3)
    except Exception:  # noqa: BLE001
        free_gb = float("inf")
    if free_gb < KB_MIN_FREE_GB:
        # P9：不硬编码个人绝对路径，KC_KB_FALLBACK 由 .env 配置；未配置则警告并暂存原盘
        fallback = os.environ.get("KC_KB_FALLBACK", "").strip()
        if fallback:
            print(f"[存储] {os.path.splitdrive(root)[0]} 盘剩余 {free_gb:.0f}GB < {KB_MIN_FREE_GB}GB，知识库改存 {fallback}")
            return fallback
        print(f"[存储] ⚠ {os.path.splitdrive(root)[0]} 盘剩余 {free_gb:.0f}GB < {KB_MIN_FREE_GB}GB，且未设置 KC_KB_FALLBACK，暂存原盘")
    return root


KB = _kb_root()
DIRS = {
    "web": os.path.join(KB, "网页"),
    "video": os.path.join(KB, "视频"),
    "paper": os.path.join(KB, "论文"),
    "doc": os.path.join(KB, "文档"),
    "repo": os.path.join(KB, "仓库"),
}
DB_PATH = os.path.join(BASE, get("db_path", "data/collector.db"))
LOG_DIR = os.path.join(BASE, get("log_dir", "logs"))
TOOLS = get("tools", {})
COOKIES = get("cookies", {})
POLITE = get("politeness", {})
ARXIV = get("arxiv", {})
GH = get("github", {})
TEMP = os.path.join(BASE, "temp")


def tool(name, default=""):
    """本地工具路径：环境变量优先，其次 config/tools。"""
    env_map = {"crawl4ai_py": "CRAWL4AI_PY", "douyin_dl_src": "DD_DL_SRC",
               "douyin_dl_py": "DD_DL_PY", "ytdlp": "DD_YTDLP", "ffmpeg": "FFMPEG",
               "scrapling_py": "SCRAPLING_PY", "patchright_py": "PATCHRIGHT_PY",
               "playwright_py": "PLAYWRIGHT_PY", "camofox_dir": "CAMOFOX_DIR",
               "media_crawler_dir": "MEDIA_CRAWLER_DIR", "spider_xhs_dir": "SPIDER_XHS_DIR",
               "acl_anthology_dir": "ACL_ANTHOLOGY_DIR"}
    return os.environ.get(env_map.get(name, ""), "") or TOOLS.get(name, default)


def ensure_dirs():
    for d in DIRS.values():
        os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(TEMP, exist_ok=True)
