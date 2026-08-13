"""站内搜索适配器注册表。自动导入触发 @register 装饰器。"""
from .arxiv import ArxivSearcher              # arXiv API
from .semanticscholar import SemanticScholarSearcher  # Semantic Scholar API
from .dblp import DBLPSearcher                # DBLP Search API
from .paperswithcode import PapersWithCodeSearcher  # PapersWithCode API
from .acl_anthology import ACLAnthologySearcher   # ACL Anthology API
from .huggingface import HuggingFaceSearcher  # HF Models/Datasets API
from .kaggle import KaggleSearcher            # Kaggle Datasets API
from .github_topics import GitHubTopicsSearcher  # GitHub Topics/Search API
from .bilibili import BilibiliSearcher        # B站搜索 API
from .hackernews import HackerNewsSearcher    # HN Algolia API
from .conferences import NeurIPSConferenceSearcher, ICMLConferenceSearcher, ICLRConferenceSearcher, OpenReviewSearcher
from .playwright_search import PlaywrightSearcher  # 抽象基类(不注册)
# 社区/论坛(Playwright)
from .zhihu import ZhihuSearcher
from .community_search import JuejinSearcher, CSDNSearcher, SegfaultSearcher, OschinaSearcher, V2EXSearcher, DevToSearcher, MediumSearcher, HackernoonSearcher, LobstersSearcher, DatawhaleSearcher, AlignmentForumSearcher
# 视频(Playwright)
from .video_search import YouTubeSearcher, DouyinSearcher, XhsSearcher
# 学术(Playwright)
from .academic_search import GoogleScholarSearcher, ConnectedPapersSearcher, ScirateSearcher
# 代码平台(Playwright)
from .code_platform import GiteeSearcher, GitLabSearcher, LeetCodeSearcher
# AI工具(Playwright)
from .ai_tools import CursorSearcher, ClaudeCodeSearcher, OpenCodeSearcher, QoderSearcher
# 课程平台(Playwright)
from .course_platforms import CourseraSearcher, EdxSearcher, KhanAcademySearcher
# 科技资讯(Playwright)
from .tech_news import _36krSearcher, HuxiuSearcher, TmtpostSearcher, JiqizhixinSearcher, QbitaiSearcher, InfoqSearcher, SspaiSearcher
# AI平台(Playwright+API)
from .ai_platforms import ModelscopeSearcher

# Crawl4AI 抓取搜索页（放最后，覆盖同名 Playwright/API 搜索器）
from .crawl4ai_search import BilibiliCrawlSearcher, CSDNCrawlSearcher, JuejinCrawlSearcher, ZhihuCrawlSearcher, XhsCrawlSearcher

# Scrapling 渲染攻坚层（放在最后，覆盖 Crawl4AI/Playwright 同名的 JS 动态站搜索器）
# 用渲染后的真实 DOM 提取文章链接，解决"只爬到导航壳"的痛点
from .scrapling_search import (CSDNScraplingSearcher, JuejinScraplingSearcher,
                               ZhihuScraplingSearcher, BilibiliScraplingSearcher,
                               XhsScraplingSearcher, SegmentfaultScraplingSearcher,
                               V2exScraplingSearcher, DevToScraplingSearcher,
                               AlignmentforumScraplingSearcher, ClaudeCodeDocsScraplingSearcher,
                               CourseraScraplingSearcher, EdxScraplingSearcher)

# Sitemap 兜底（最后 import，覆盖被反爬/JS 挡住的站）
from .sitemap_search import (HuxiuSitemapSearcher, TmtpostSitemapSearcher,
                             CursorSitemapSearcher, OpencodeSitemapSearcher,
                             QoderSitemapSearcher)

# 专项工具（yt-dlp ytsearch，覆盖视频站）
from .special_tools import YoutubeYtdlpSearcher

# 拯救方法（高价值站，覆盖被反爬的旧版）
from .openalex_search import OpenAlexSearcher
from .acl_local_search import AclAnthologyLocalSearcher
from .rss_search import MediumRssSearcher, OschinaRssSearcher
from .hf_api_search import HfApiSearcher

# CDP 攻坚层（最后 import，借真实浏览器绕验证码，覆盖被反爬的站）
from .cdp_search import (DouyinCdpSearcher, WeiboCdpSearcher, BilibiliCdpSearcher,
                         InfoqCdpSearcher, Kr36CdpSearcher, SspaiCdpSearcher,
                         TmtpostCdpSearcher, LeetcodeCdpSearcher, GiteeCdpSearcher,
                         SemanticScholarCdpSearcher, KhanacademyCdpSearcher,
                         CsdnCdpSearcher)
