# 架构说明

> `web-knowledge-crawler` 的内部结构、数据流与扩展点概览。文件放哪里见 `docs/目录契约.md`；输出格式见 `docs/输出规范.md`。

## 总体布局

```
app/                入口层 —— 薄，不含业务逻辑
  ├─ crawl_guide.py      🧭 智能交互引导（指定爬取 / 大规模爬取）
  ├─ crawl_all.py        大规模爬取 CLI（词 / 站 / 过滤）
  ├─ crawl_sites.py      整站爬取
  ├─ cli.py              共享 CLI 工具
  └─ export_cookies.py / export_all_cookies.py   Cookie 导出
      │
      ▼  （单向依赖：app → core.*）
core/               引擎层 —— 分层 + 无循环导入
  ├─ domain/           词库 / 词性格 / 站映射 / 登录规则
  ├─ interaction/      交互引导与用户偏好（记忆上次选择）
  ├─ auth/             登录自动化与 cookie 收集/校验
  ├─ download/         下载 / 落盘 / 去重（SQLite）/ 调度
  ├─ engines/          站点搜索器（每站一文件，@register 注册）
  ├─ filter/           相关性与噪音过滤
  ├─ bridges/          渲染 / CDP / 子进程桥（Crawl4AI、Playwright…）
  ├─ get_cookie/       浏览器 cookie 采集辅助
  └─ config.py         统一配置加载（.env + config/collector.yaml）
      │
      ▼
config/ → data/（cookie/db）→ 知识库/（采集输出）
```

依赖规则：`app → core.*`，**目录 ≤3 层**，无循环导入。`core/config.py` 是唯一配置入口，`core/engines/base.py` 是唯一搜索器基类。新模块必须遵守（由 `tests/post_refactor_smoke.py` 校验）。

## 管线 / 数据流

```
词 / 链接
   │
   ▼
[app] 智能引导 → 选内容类型与站点
   │
   ▼
[core/domain]   词性格 → 推荐类型；站映射 → 搜索器注册表
   │
   ▼
[core/engines]  并发搜索多站（asyncio），每站返回结构化结果
   │
   ▼
[core/filter]   相关度打分（BM25 / 关键词 / URL 启发式）、去噪
   │
   ▼
[core/download] SQLite 去重 → 类型分发下载器
   │                 ├─ 直连（HTTP）
   │                 ├─ yt-dlp（视频 / 音频）
   │                 └─ 渲染桥（JS 重 / 反爬页面）
   ▼
知识库/{词}/{类型}/{站}/00_日期_标题_大小/  +  meta.json
```

每一阶段都是 asyncio 协程；整条管线由 `core/download`（调度器）编排，默认低并发（3 词）+ 站间延迟 + 超时重试。

## 搜索器引擎（`core/engines/`）

每站一个文件，实现基类模式并自注册：

```python
from core.engines.base import BaseSearcher, register

@register
class ArxivSearcher(BaseSearcher):
    name = "arxiv"
    ...
```

按传输策略分组：

| 家族 | 文件（示例） | 技术 |
|---|---|---|
| **学术** | `arxiv.py`、`dblp.py`、`semanticscholar.py`、`openalex_search.py`、`paperswithcode.py`、`acl_anthology.py`、`conferences.py` | REST API / OAI-PMH / feed |
| **网页 / RSS** | `rss_search.py`、`sitemap_search.py`、`hackernews.py`、`tech_news.py` | RSS / sitemap / HTML |
| **视频** | `bilibili.py`、`video_search.py`（YouTube/抖音） | yt-dlp 提取 / CDP |
| **社区** | `zhihu.py`、`community_search.py`、`ai_platforms.py`、`code_platform.py` | HTML / API |
| **JS 重 / 反爬** | `crawl4ai_search.py`、`playwright_search.py`、`scrapling_search.py`、`cdp_search.py` | 渲染桥或 CDP 真实浏览器 |

搜索器可能依赖外部工具（Crawl4AI、Playwright、yt-dlp、MediaCrawler）。工具缺失时**明确警告并跳过该站** —— 绝不清零假装成功。

## 关键横切概念

### 词智能（`core/domain`）
- 自动整理乱格式词表。
- 识别"词性格"（学术 / 教程 / 热点 / 代码）以推荐内容类型。
- 通过 `SITE_TYPE_MAP` 把词映射到推荐站点。

### 登录与 Cookie（`core/auth` + `core/get_cookie`）
- 检测需登录站点，打开登录页；从配置浏览器（`KC_COOKIE_BROWSER`）采集 cookie；校验登录态。
- 需登录站必须匹配**关键 cookie 列**，避免登录态误判。

### 反爬策略
多引擎回退 → cookie 注入 → 隐形渲染器（Crawl4AI / Scrapling / patchright / Playwright）→ CDP 真实浏览器 → 低并发 + 延迟。

### 输出（`知识库/`）
每条按 `知识库/{词}/{类型}/{站}/00_日期_标题_大小/` 落盘，含 `meta.json`，外加 HTML 双份（原始 + 干净正文）便于浏览。详见 `docs/输出规范.md`。

## 扩展点

| 想… | 改哪里 |
|---|---|
| 加一个站 | `core/engines/` 新文件 + `@register` + `SITE_TYPE_MAP`（见 `CONTRIBUTING.md`） |
| 加一种内容类型 | `core/domain` 映射 + `core/download` 下载分发 |
| 加一条过滤规则 | `core/filter` |
| 加一个入口命令 | `app/` 新文件调用 `core.*` |
| 改输出格式 | `core/download/preserver.py` + `docs/输出规范.md` |

## 测试

| 套件 | 用途 |
|---|---|
| `tests/post_refactor_smoke.py` | 结构冒烟：全部文件可编译、import 无断链、引擎可实例化 |
| `tests/exhaustive_guide_test.py` | 交互引导穷举（200+ 变体） |
| `tests/fresh_exhaustive.py` | 全新穷举套件（T01–T19，102 项断言） |
| `tests/task_audit.py` | 逐 Task 审计（67 项） |

提 PR 前全部运行一遍。
