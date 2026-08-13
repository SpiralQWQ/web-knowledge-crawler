"""混合调度器 — 3~5个词汇并行，每个词内站间串行。

每站支持搜索的：使用 search_engine.BaseSearcher
每站无搜索但提供 seed 的：使用 seed_collector
纯静态资源（已知 URL）：使用 static_fetcher

整体流程:
    词队列 (2740 terms) → 按词拆分为 N 个子任务
    子任务1: term A → site1(search) → site2(seed) → site3(static) ...
    子任务2: term B → site1(search) → site2(seed) → site3(static) ...
    ...

    同一时刻最多运行 CONCURRENCY (默认 3) 个子任务
    每个子任务内部严格串行处理各站
"""
import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CrawlStats:
    """爬取统计。"""
    total_terms: int = 0
    total_sites: int = 0
    current_term: str = ""
    current_site: str = ""
    terms_done: int = 0
    sites_done: int = 0
    downloads_done: int = 0
    skipped_dedup: int = 0
    started_at: float = field(default_factory=time.time)
    errors: int = 0

    @property
    def elapsed_seconds(self) -> float:
        return time.time() - self.started_at

    @property
    def eta_seconds(self) -> float | None:
        if self.terms_done == 0:
            return None
        avg_per_term = self.elapsed_seconds / self.terms_done
        remaining = (self.total_terms - self.terms_done) * avg_per_term
        return remaining

    def progress_pct(self) -> float:
        if self.total_terms == 0:
            return 0.0
        return self.terms_done / self.total_terms * 100

    def summary(self) -> str:
        parts = [
            f"进度: {self.progress_pct():.1f}%",
            f"已完成: {self.terms_done}/{self.total_terms} 词",
            f"当前: {self.current_term} → {self.current_site}",
        ]
        if self.eta_seconds is not None:
            hours = int(self.eta_seconds // 3600)
            mins = int((self.eta_seconds % 3600) // 60)
            parts.append(f"预计剩余: ~{hours}h {mins}m")
        parts.append(f"下载: {self.downloads_done} | 跳过去重: {self.skipped_dedup} | 错误: {self.errors}")
        return " · ".join(parts)


class MixedScheduler:
    """混合调度器 — 词级并发(3-5) + 站内串行。"""

    def __init__(self, concurrency: int = 3, delay_between_sites: float = 1.0):
        self.concurrency = max(1, min(10, concurrency))
        self.delay = delay_between_sites
        self.semaphore = asyncio.Semaphore(concurrency)
        self.stats = CrawlStats()

    async def run(self, terms: list[str], sites_config: list[dict]):
        """
        执行全部爬取任务。

        Args:
            terms: 要搜索的专业词汇列表
            sites_config: 站点配置列表
                [{"name": "arxiv", "type": "search"},
                 {"name": "github_repos", "type": "seed"},
                 {"name": "static_pdfs", "type": "static"}]
        """
        self.stats.total_terms = len(terms)
        self.stats.total_sites = len(sites_config)

        tasks = []
        # 将词汇分配为多个子任务(每次取 concurrency 个词为一组)
        for i in range(0, len(terms), self.concurrency):
            batch = terms[i:i + self.concurrency]
            tasks.append(asyncio.create_task(self._process_batch(batch, sites_config)))

        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("✅ 全部完成: %s", self.stats.summary())

    async def _process_batch(self, batch_terms: list[str],
                             sites_config: list[dict]):
        """处理一批词汇(同批内的词互不阻塞，各自串行遍历所有站点)。"""
        async with self.semaphore:
            for term in batch_terms:
                self.stats.current_term = term
                self.stats.terms_done += 1
                self.stats.skipped_dedup_local = 0

                for sc in sites_config:
                    try:
                        await self._crawl_site(term, sc)
                        self.stats.sites_done += 1
                    except Exception as e:
                        self.stats.errors += 1
                        logger.error("✗ %s → %s: %s", term, sc["name"], e)

                    # 站间延迟，避免被限流
                    if self.delay > 0:
                        await asyncio.sleep(self.delay)

    async def _crawl_site(self, term: str, sc: dict):
        """
        对单个词的单个站执行爬取。

        sc 类型决定执行路径:
        - type="search": 调用 search_engines
        - type="seed": 调用 seed_collectors
        - type="static": 调用 static_fetchers
        """
        self.stats.current_site = sc["name"]

        stype = sc.get("type", "search")

        if stype == "search":
            await self._crawl_search(term, sc)
        elif stype == "seed":
            await self._crawl_seed(term, sc)
        elif stype == "static":
            await self._crawl_static(term, sc)
        else:
            logger.warning("未知站点类型: %s (%s)", sc["name"], stype)

    async def _crawl_search(self, term: str, sc: dict):
        """类型=搜索: 站内搜索 → 下载原始结果。"""
        from core.engines.base import get_searcher
        searcher = get_searcher(sc["name"])
        if searcher is None:
            logger.debug("未注册搜索器: %s, 跳过", sc["name"])
            return
        results = await searcher.search(term, max_results=sc.get("max_results", 20))
        self.stats.downloads_done += len(results)

    async def _crawl_seed(self, term: str, sc: dict):
        """类型=seed: 从预定义种子列表匹配包含该词的条目。"""
        logger.debug("Seed采集: %s [%s]", sc["name"], term)
        # 具体实现见 seed_collector/

    async def _crawl_static(self, term: str, sc: dict):
        """类型=static: 下载已知URL的原始文件。"""
        logger.debug("Static采集: %s [%s]", sc["name"], term)
        # 具体实现见 static_fetcher/
