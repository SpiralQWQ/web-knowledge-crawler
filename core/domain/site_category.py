"""站点→类别映射 — 决定爬取内容归入哪个类别目录。

类别对应知识库/{词汇}/{类别}/ 的目录名：
  论文 / 视频 / 网页 / 文档 / 数据集 / 仓库 / 课程

规则：每个搜索站点 + 种子类型固定归入一个类别。
"""
# 站点名 → 类别目录名
SITE_CATEGORY = {
    # 论文
    "arxiv": "论文", "semanticscholar": "论文", "dblp": "论文",
    "aclanthology": "论文", "openreview": "论文", "paperswithcode": "论文",
    "neurips": "论文", "icml": "论文", "iclr": "论文",
    # 视频
    "bilibili": "视频", "youtube": "视频", "douyin": "视频",
    "video_keywords": "视频",
    # 音频（播客/访谈）— 键名与 config/site_entries.txt 实际 name 对齐
    "Lex Fridman Podcast": "音频", "Linear Digressions": "音频",
    "Software Engineering Radio": "音频", "The AI Alignment Podcast": "音频",
    "The AI Podcast": "音频",
    # 网页（文章/博客/社区/资讯/公众号/图文）
    "zhihu": "网页", "juejin": "网页", "csdn": "网页", "cnblogs": "网页",
    "segmentfault": "网页", "oschina": "网页", "v2ex": "网页",
    "cnodejs": "网页", "lobste.rs": "网页", "stackoverflow": "网页",
    "devto": "网页", "datawhale": "网页", "alignmentforum": "网页",
    "kanxue": "网页", "medium": "网页", "hackernoon": "网页",
    "sspai": "网页", "wechat": "网页", "xiaohongshu": "网页",
    "36kr": "网页", "huxiu": "网页", "tmtpost": "网页",
    "jiqizhixin": "网页", "qbitai": "网页", "infoq": "网页",
    "hackernews": "网页", "leetcode": "网页",
    # 文档
    "doc_seeds": "文档", "static_pdfs": "文档",
    # 数据集（模型/数据集）
    "huggingface": "数据集", "kaggle": "数据集", "modelscope": "数据集",
    # 仓库
    "github_topics": "仓库", "gitee": "仓库", "gitlab": "仓库",
    "repo_seeds": "仓库",
    # 课程
    "coursera": "课程", "edx": "课程", "geekbang": "课程",
    "imooc": "课程", "icourse163": "课程", "khanacademy": "课程",
    "study163": "课程", "xuetangx": "课程", "jikexueyuan": "课程",
}

# 默认类别（未映射的站）
DEFAULT_CATEGORY = "网页"

# 细分类（site_entries.txt 里的 category 字段）→ 6 大类
CATEGORY_MAP = {
    # → 论文
    "论文": "论文", "学术搜索": "论文", "论文筛选": "论文",
    "论文关联图谱": "论文", "ACM论文库": "论文", "学术论文库": "论文",
    "科学出版": "论文", "学术论文发表": "论文", "arXiv评论": "论文",
    # → 视频
    "视频": "视频", "视频课程": "视频", "微软大会录像": "视频",
    "谷歌开发者大会": "视频", "AI与图形大会演讲": "视频", "PyTorch大会录像": "视频",
    "创意编程": "视频", "IT视频课程": "视频",
    # → 网页
    "官方文档": "网页", "框架文档": "网页", "工具文档": "网页",
    "教程": "网页", "博客": "网页", "技术博客": "网页",
    "技术文章": "网页", "技术社区": "网页", "云技术社区": "网页",
    "技术资讯": "网页", "科技资讯（需 Cookie）": "网页", "科技数码": "网页",
    "AI 垂直资讯": "网页", "算法教程": "网页", "Python教程": "网页",
    "开源月刊": "网页", "创作者工具访谈": "网页", "编程教育": "网页",
    "开源访谈": "网页", "AI深度访谈": "音频", "ML播客": "音频",
    "软工播客": "音频", "软工访谈": "音频", "AI对齐播客": "音频",
    "NVIDIA访谈": "音频", "逆向安全社区": "网页", "AI 垂直社区（需 Cookie）": "网页",
    "在线 IDE": "网页", "安全": "网页", "协议文档": "网页",
    # → 文档
    "文档直链": "文档", "云文档": "文档",
    # → 数据集
    "CV数据集": "数据集", "AI绘画模型": "数据集", "图标素材": "数据集",
    "扁平化图标": "数据集", "矢量图标": "数据集", "免费高清图片": "数据集",
    # → 仓库
    "代码托管": "仓库", "航天发射/火箭数据（社区）": "仓库",
    # → 课程
    "课程": "课程",
    # → AI 平台/工具（归网页，它们是产品首页/控制台）
    "AI 模型 API": "网页", "阿里 AI 模型": "网页", "开源 AI 编码 CLI": "网页",
    "开源 AI Agent 框架": "网页", "Claude 编码代理": "网页", "OpenAI 编码代理": "网页",
    "阿里 AI 办公助手": "网页", "阿里 AI 编程助手": "网页",
    "腾讯 AI 助手（OpenClaw 系）": "网页", "腾讯 AI 桌面工作台（OpenClaw 系）": "网页",
    "工具": "网页", "LaTeX": "文档", "竞赛平台": "网页",
}


def category_of(site_name: str) -> str:
    """返回站点归属的类别目录名。"""
    return SITE_CATEGORY.get(site_name, DEFAULT_CATEGORY)


def normalize_category(raw: str) -> str:
    """把细分类归一化为 6 大类。"""
    return CATEGORY_MAP.get(raw, DEFAULT_CATEGORY)


def all_categories() -> list[str]:
    """返回所有类别名（去重排序）。"""
    return sorted(set(SITE_CATEGORY.values()))
