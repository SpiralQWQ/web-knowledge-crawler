"""CDP 引擎站内搜索 — 借用户真实浏览器（调试端口）攻坚反爬强的站。

为什么用它：抖音/微博/B站等站对独立浏览器（Scrapling/Playwright 新建）一搜就弹验证码
或崩页。而 CDP 附加**用户已登录的真实浏览器窗口**，指纹/登录态全是真人 → 不弹验证码，
直接出真实内容。调 core/bridges/cdp_helper.py 子进程桥。

覆盖：douyin（抖音，替代旧 Playwright 搜索器）。
"""
import asyncio
import json
import os
import re

from urllib.parse import quote

from .base import BaseSearcher, register
from core.config import tool, BASE

# 抖音卡片标题里的噪音行：时长 / 播放量 / 合集标签 / 作者@ / 相对时间
_CRUFT = re.compile(
    r"^(\d{1,2}:\d{2}(:\d{2})?$"      # 时长 18:53 / 1:02:03
    r"|合集|追番|精选$"                # 卡片角标
    r"|@.*$"                          # 作者
    r"|^\d{1,3}(,\d{3})*(\.\d+)?[万Kk]?$"   # 播放量/引用数（2.0万 / 34,583）
    r"|^\d*[年月天周小时分]前$"          # 相对时间
    r")$")


def _clean_title(text: str) -> str:
    """从卡片文本里抽标题（去掉时长/播放量/作者/时间/导航等噪音）。

    策略：过滤纯杂项行后取最长行 —— 标题通常最长，作者/日期/点赞/导航都短。
    """
    if not text:
        return ""
    lines = [l.strip() for l in str(text).split("\n") if l.strip()]
    cands = [l for l in lines if not _CRUFT.match(l)]
    if not cands:
        return (lines[-1][:200] if lines else "")
    return max(cands, key=len)[:200]


class CdpSearcher(BaseSearcher):
    """借真实浏览器(CDP)渲染搜索页的搜索器基类。子类定义 URL 模板/链接正则。"""

    search_url_template = ""
    link_pattern = ""       # 结果链接正则（如 /video/）
    result_type = "html"
    wait_ms = 12000         # 渲染等待毫秒
    title_sel = ""          # 标题 CSS 选择器（可选）
    scroll_rounds = 0       # 额外滚动轮数（懒加载站）
    retry = 2               # 验证码拦截重试次数
    title_blacklist = ()    # 命中的标题直接丢弃（站内导航/固定栏目名）
    cdp_env = "playwright_py"  # 跑 cdp_helper 的 python（AAATool 环境）

    @property
    def name(self) -> str:
        return self.__class__.__dict__.get("name", "")

    @property
    def domain(self) -> str:
        return self.link_pattern.strip("/") if self.link_pattern else ""

    def _port(self) -> int:
        try:
            return int(os.environ.get("KC_CDP_PORT", "").strip() or 9222)
        except ValueError:
            return 9222

    async def search(self, term: str, max_results: int = 50) -> list[dict]:
        py = tool(self.cdp_env)
        if not py or not os.path.exists(py):
            raise RuntimeError(f"{self.name}: 未配置 {self.cdp_env} 环境")
        helper = os.path.join(BASE, "core", "bridges", "cdp_helper.py")
        url = self.search_url_template.replace("{term}", quote(term))
        cmd = [py, helper, url, "--wait", str(self.wait_ms),
               "--link-pattern", self.link_pattern,
               "--max-links", str(max_results),
               "--title-sel", self.title_sel,
               "--scroll", str(self.scroll_rounds),
               "--retry", str(self.retry),
               "--port", str(self._port())]
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env)
        try:
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=150)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:  # noqa: BLE001
                pass
            return []
        data = {}
        for line in reversed(out.decode("utf-8", errors="replace").strip().split("\n")):
            if line.strip().startswith("{"):
                try:
                    data = json.loads(line)
                except Exception:  # noqa: BLE001
                    data = {}
                break
        if not data.get("success"):
            err = data.get("error", "CDP 渲染失败")
            # CDP 不可用是环境问题，不静默假装空结果 —— 明确抛出让上层记录
            raise RuntimeError(f"{self.name}: {err}")
        results = []
        for it in data.get("items", []):
            u = (it.get("url") or "").strip()
            if not u:
                continue
            title = _clean_title(it.get("title", ""))
            if not title or any(b in title for b in self.title_blacklist):
                continue
            results.append({
                "url": u,
                "title": title,
                "type": self.result_type,
                "summary": "",
                "original_term": term,
            })
            if len(results) >= max_results:
                break
        return results


@register
class DouyinCdpSearcher(CdpSearcher):
    """抖音网页版搜索 — 借真实浏览器绕验证码。搜索页 type=video 出视频。"""
    name = "douyin"
    search_url_template = "https://www.douyin.com/search/{term}?type=video"
    link_pattern = "/video/"
    result_type = "video"
    wait_ms = 12000


@register
class CsdnCdpSearcher(CdpSearcher):
    """CSDN — 借真实浏览器（Scrapling 被反爬拦截返回封禁页）。so.csdn.net 文章卡片。"""
    name = "csdn"
    search_url_template = "https://so.csdn.net/so/search?q={term}"
    link_pattern = r"/article/details/\d+"
    result_type = "html"
    wait_ms = 10000


@register
class WeiboCdpSearcher(CdpSearcher):
    """微博搜索 — 借真实浏览器带登录态。s.weibo.com 网页版搜索，正文在 p.txt。"""
    name = "weibo"
    search_url_template = "https://s.weibo.com/weibo?q={term}"
    link_pattern = r"weibo\.com/\d+/[A-Za-z]"   # uid/mid 内容链接（排除用户主页 u/ 与 game.weibo.com）
    title_sel = "p.txt, .txt"                   # 微博正文段落
    result_type = "html"
    wait_ms = 10000


@register
class BilibiliCdpSearcher(CdpSearcher):
    """B站搜索 — 借真实浏览器。search.bilibili.com 视频卡片，标题在 .bili-video-card__info--tit。"""
    name = "bilibili"
    search_url_template = "https://search.bilibili.com/all?keyword={term}"
    link_pattern = "/video/BV"
    title_sel = ".bili-video-card__info--tit"
    result_type = "video"
    wait_ms = 10000


@register
class InfoqCdpSearcher(CdpSearcher):
    """InfoQ 中文 — 借真实浏览器。搜索页 /article/ 文章卡片，标题在链接文本。"""
    name = "infoq"
    search_url_template = "https://www.infoq.cn/search?keyword={term}"
    link_pattern = "/article/"
    result_type = "html"
    wait_ms = 10000


@register
class Kr36CdpSearcher(CdpSearcher):
    """36氪 — 借真实浏览器。搜索页 /p/{数字} 文章卡片，标题在 .article-item-title。"""
    name = "36kr"
    search_url_template = "https://36kr.com/search/articles/{term}"
    link_pattern = r"/p/\d+"
    title_sel = ".article-item-title, .title-wrapper"
    title_blacklist = ("核心服务", "首页", "资讯")
    result_type = "html"
    wait_ms = 10000


@register
class SspaiCdpSearcher(CdpSearcher):
    """少数派 — 借真实浏览器。search?q= 文章卡片，标题是"作者/日期/标题"格式（最长行提取）。"""
    name = "sspai"
    search_url_template = "https://sspai.com/search?q={term}"
    link_pattern = r"/post/\d+"
    result_type = "html"
    wait_ms = 10000


@register
class TmtpostCdpSearcher(CdpSearcher):
    """钛媒体 — 借真实浏览器。WordPress ?s= 搜索，文章懒加载需滚动。"""
    name = "tmtpost"
    search_url_template = "https://www.tmtpost.com/?s={term}"
    link_pattern = r"/nictation/\d+"
    result_type = "html"
    wait_ms = 8000
    scroll_rounds = 4


@register
class LeetcodeCdpSearcher(CdpSearcher):
    """力扣 — 借真实浏览器（需登录）。/search/?q= 全局搜索，题目带 ?q= 参数。"""
    name = "leetcode"
    search_url_template = "https://leetcode.cn/search/?q={term}"
    link_pattern = r"/problems/[^?]+\?q="
    result_type = "html"
    wait_ms = 12000


@register
class GiteeCdpSearcher(CdpSearcher):
    """码云 Gitee — 借真实浏览器。search.gitee.com 新搜索，仓库卡片 {owner}/{repo}。"""
    name = "gitee"
    search_url_template = "https://search.gitee.com/?q={term}"
    link_pattern = r"gitee\.com/[^/]+/[^/]+$"
    title_blacklist = ("工作台", "探索", "帮助", "登录", "注册", "开源软件搜索")
    result_type = "repo"
    wait_ms = 10000


@register
class SemanticScholarCdpSearcher(CdpSearcher):
    """Semantic Scholar — 借真实浏览器（免 API key 限流）。/paper/ 论文卡片。"""
    name = "semanticscholar"
    search_url_template = "https://www.semanticscholar.org/search?q={term}"
    link_pattern = "/paper/"
    result_type = "paper"
    wait_ms = 12000


@register
class KhanacademyCdpSearcher(CdpSearcher):
    """可汗学院 — 借真实浏览器（原 API 400）。/search?page_search_query= 课程/视频。"""
    name = "khanacademy"
    search_url_template = "https://www.khanacademy.org/search?page_search_query={term}"
    link_pattern = "/math/"
    result_type = "html"
    wait_ms = 12000
