<p align="center">
  <kbd><a href="README.md">English</a></kbd> · <kbd>简体中文</kbd>
</p>

<p align="center">
  <a href="https://github.com/SpiralQWQ/web-knowledge-crawler"><img src="https://img.shields.io/github/stars/SpiralQWQ/web-knowledge-crawler" alt="GitHub stars"></a>
  <a href="https://github.com/SpiralQWQ/web-knowledge-crawler/releases"><img src="https://img.shields.io/github/v/release/SpiralQWQ/web-knowledge-crawler" alt="版本"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-3776AB" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-AGPL%203.0-blue" alt="协议"></a>
  <a href="#"><img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey" alt="平台"></a>
  <a href="https://github.com/SpiralQWQ/web-knowledge-crawler/commits"><img src="https://img.shields.io/github/last-commit/SpiralQWQ/web-knowledge-crawler" alt="最近提交"></a>
  <a href="https://github.com/SpiralQWQ/web-knowledge-crawler/issues"><img src="https://img.shields.io/github/issues/SpiralQWQ/web-knowledge-crawler" alt="Issues"></a>
</p>

<h1 align="center">web-knowledge-crawler</h1>

<p align="center">按专业词汇系统性爬取全网知识 — 论文、视频、文章、代码、数据集、课程，一站下载。</p>
<p align="center">给它一个词或一个链接，它搜索 51 个网站、下载原始文件，并整理成可直接浏览的知识库。</p>
<p align="center"><b>只爬取原始数据，不做解析/OCR — 后续（MinerU / ASR / RAG）由你接管。</b></p>


## Table of Contents

- [它做什么](#它做什么)
- [🌐 支持的网站（51 站 / 8 类）](#支持的网站51-站-8-类)
- [🧭 智能引导怎么用（点菜式）](#智能引导怎么用点菜式)
- [功能一览](#功能一览)
- [🧪 使用示例](#使用示例)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [配置](#配置)
- [目录结构](#目录结构)
- [🏗 架构](#架构)
- [🧰 技术栈](#技术栈)
- [🙏 致谢](#致谢)
- [📌 Roadmap](#roadmap)
- [📮 反馈与贡献](#反馈与贡献)
- [❓ FAQ](#faq)
- [免责声明](#免责声明)
- [许可证](#许可证)
- [💛 支持 / 打赏](#支持-打赏)


## 它做什么

web-knowledge-crawler 是一个**领域知识爬虫**。你喂给它专业词汇（内置 2740 词）或一条分享链接，它会：

- 在 **51 个网站**、8 类内容（论文/视频/文章/代码/数据集/课程/文档/Q&A）中搜索
- **下载各种类型的原始文件** —— PDF、MP4、代码仓库、图片、音频、压缩包
- 整理进 `知识库/` 目录：`{词}/{类型}/{站}/00_日期_标题_大小/` + `meta.json`
- 过滤噪音、SQLite 去重、HTML 站双份落盘（原始 + 干净正文）

**只爬原始数据。** 不解析、不 OCR、不生成 AI 笔记 —— 那是另一条管线（如 MinerU / ASR / RAG）。

### 工作流程

```
词/链接 → 智能引导(推荐类型/选站) → 搜索器(51站) → 过滤+去重(SQLite)
        → 类型分发下载(yt-dlp/直连/渲染) → 知识库落盘 + meta.json
```

## 🌐 支持的网站（51 站 / 8 类）

| 类型 | 站点 |
|---|---|
| 📄 **论文 (12)** | arXiv · dblp（计算机文献）· Semantic Scholar · PapersWithCode · ACL Anthology（自然语言）· OpenReview · NeurIPS · ICML · ICLR · Google Scholar · Connected Papers · SciRate |
| 🎬 **视频 (3)** | Bilibili · YouTube · 抖音 Douyin |
| 📝 **文章 (22)** | 掘金 · CSDN · 知乎 · 思否 · InfoQ · 少数派 · 36氪 · Medium · 开源中国 · Hacker News · 微博 · Alignment Forum · 小红书 · Datawhale · DEV Community · Lobsters · HackerNoon · 虎嗅 · 机器之心 · 量子位 · 钛媒体 · V2EX |
| 💻 **代码 (3)** | GitHub Topics · Gitee 码云 · GitLab |
| 📊 **数据集 (3)** | Hugging Face · Kaggle · ModelScope 魔搭 |
| 🎓 **课程 (3)** | Coursera · edX · Khan Academy 可汗学院 |
| 📚 **文档 (4)** | Cursor · Claude Code Docs · OpenCode · Qoder Docs |
| ❓ **Q&A (1)** | LeetCode 力扣 |

> 部分站点需登录态或调试浏览器（见"配置"）；个别被禁用的站会在日志中明确跳过，绝不清零假装成功。

## 🧭 智能引导怎么用（点菜式）

`python app/crawl_guide.py` 进入引导。全程大白话询问，你只需要选数字/回车。

### ① 指定爬取（发链接下载）

```
1. 粘贴链接（视频/文章/网页/分享口令都行，会自动提取真正的链接）
2. 自动认出是哪个网站（抖音/B站/YouTube/微博/小红书...）
3. 问要不要连根（下载作者系列）
4. 选速度（快速/标准/全量）
5. 选保存位置（默认或自定义）
6. 大白话确认 → 下载（带进度条）→ 落盘
```

### ② 大规模爬取（选词选站批量搜）

```
1. 选词来源：手输 / 导入词库（乱格式自动整理）/ 内置 2740 词表
2. 输入词 → 自动识别"词性格"（学术/教程/热点/代码）→ 推荐内容类型
3. 选内容类型（论文/视频/文章/... 可加可减）
4. 选网站（可跳过 → 按推荐）
5. 细节：时间范围 / 每站条数 / 多集 / 附件
6. 选速度（🐇快速=安全稍快 / 🚶标准 / 🐢全量）
7. 选保存位置
8. 大白话确认（含就绪检查：浏览器/登录态逐站显示）→ 执行 → 逐条进度日志
```

> 误按 Ctrl+C/Ctrl+D 不会崩；非法输入自动回退默认；上次选择下次默认（偏好记忆）。

## 功能一览

| | 功能 | 说明 |
|---|---|---|
| 🔗 | 指定爬取 | 贴链接 → 认站 → 下载，可连根爬作者系列 |
| 🌳 | 连根爬 | 抖音/小红书/微博借浏览器收集系列；B站/YouTube 走 yt-dlp |
| 📚 | 大规模爬取 | 选词 → 类型 → 站 → 细节 → 速度 → 批量执行 |
| 🔐 | 登录自动化 | 检测需登录站、自动开登录页、登录后自动收集 cookie、二次校验 |
| 🧠 | 词智能 | 乱格式词自动整理、词性格识别、内容类型推荐 |
| 📊 | 排序 | GitHub 按 star、arXiv 按最新/相关（`--sort`） |
| 🗂️ | 规范落盘 | `知识库/{词}/{类型}/{站}/00_日期_标题_大小/` + meta.json + HTML 双份 |
| 🛡️ | 防封 | 多引擎回退、cookie 注入、隐形浏览器、限速、进度日志 |

## 🧪 使用示例

### 例 1：爬取 arXiv 上关于强化学习的论文

```bash
# `--terms` 是词表文件路径（每行一个词）；vocab_terms.txt 为内置精简词表
python app/crawl_all.py --terms config/seeds/vocab_terms.txt --sites arxiv --max-results 5
```

预期输出（逐条进度）：
```
📦 开始爬取词汇[1/1]: reinforcement learning
  • [arxiv] 搜索到 5 条 → 过滤后 5 条
  ⏳ 下载 [1/5] A Deep Reinforcement Learning Approach...
  ✔ [arxiv] 完成: 5/5 下载
✅ 爬取完成
落盘: 知识库/reinforcement_learning/arxiv/论文/00_20260812_.../xxx.pdf
```

### 例 2：指定爬取一条抖音视频（智能引导）

```bash
python app/crawl_guide.py
# 选 1 指定爬取 → 粘贴抖音分享口令 → 回车确认 → 自动下载到 知识库/指定爬取/
```

### 例 3：大规模爬取（引导全程点选）

```bash
python app/crawl_guide.py
# 选 2 大规模爬取 → 输词"transformer" → 按推荐选类型 → 选站 → 选速度 → 确认执行
```

## 环境要求

- **Python 3.10+**（Windows / Linux）
- 基础依赖：`pip install -r requirements.txt`
- 可选外部工具（缺失时优雅降级，见"配置"）：
  - **yt-dlp**（视频/音频下载）
  - **Crawl4AI / Scrapling / patchright / Playwright**（网页渲染/反爬）

## 快速开始

```bash
# 1. 克隆
git clone https://github.com/SpiralQWQ/web-knowledge-crawler
cd web-knowledge-crawler

# 2. 开箱即用配置向导（推荐）：
#    回答几个问题 → 自动安装依赖 + 生成 .env，无需看文档
python setup.py

# 3. 运行
python app/crawl_guide.py      # 🧭 智能引导（推荐）
python app/crawl_all.py        # 大规模爬取（高级）
python app/crawl_all.py --sites arxiv,bilibili --max-results 5 --out-dir /你的输出目录
python app/crawl_sites.py      # 整站爬取
```

> 也可以手动安装：`pip install -r requirements.txt`，再复制 `.env.example` 为 `.env` 填写路径。
> 首次运行：引导会检查网站依赖（浏览器/登录态）并带你走完。

## 配置

### 环境变量（`.env`，从 `.env.example` 复制）

全部可选 —— 缺省时读取 `config/collector.yaml`。

#### 核心

| 变量 | 作用 |
|---|---|
| `KC_BASE` | 仓库根目录 —— `data/`、`知识库/`、`temp/`、`logs/` 都建在这里 |
| `CRAWL4AI_PY` | Crawl4AI 环境的 Python 解释器 |
| `DD_DL_SRC` | 抖音下载器（jiji262 douyin-downloader）源码目录 |
| `DD_DL_PY` | 抖音下载器虚拟环境的 Python 解释器 |
| `DD_YTDLP` | yt-dlp 可执行文件（B站 / YouTube） |
| `FFMPEG` | ffmpeg/ffprobe 可执行文件（可选，暂未使用） |
| `GH_TOKEN` | （可选）GitHub API 令牌，提升搜索限流 |

#### 进阶（cookie / 代理）

| 变量 | 作用 |
|---|---|
| `KC_COOKIE_BROWSER` | cookie 注入用的浏览器（`edge` / `chrome` / `firefox`）；默认 `edge` |
| `KC_COOKIES_FILE` | Netscape 格式 cookie 文件路径（优先于浏览器） |
| `KC_DOUYIN_CONFIG` | 抖音 jiji262 `config.yml` 路径（默认随 `DD_DL_SRC`，一般无需设置） |
| `KC_COOKIE_DOMAINS` | 需登录态的域名（逗号分隔），覆盖 `collector.yaml` |
| `KC_COOKIE_PROFILE` | 浏览器非默认 profile（供 cookie 导出 / yt-dlp 用） |
| `KC_ALLOW_ANONYMOUS` | 浏览器 profile 锁定时是否允许匿名下载；`1` = 允许，默认拒绝 |
| `HTTP_PROXY` | HTTP 代理（可选） |
| `HTTPS_PROXY` | HTTPS 代理（可选） |

### 外部工具（`config/collector.yaml`）

| 工具 | 用途 | 缺失时 |
|---|---|---|
| Crawl4AI | 网页渲染 | 该站跳过并警告 |
| Scrapling / patchright | JS 重/反爬站 | 同上 |
| Playwright | CDP 自动化 / 登录 | 登录自动化不可用 |
| yt-dlp | 视频/音频下载 | 视频站跳过 |
| MediaCrawler / Spider_XHS | 需登录社交站 | 该站跳过 |

> 大多数工具可选。工具缺失时明确记录警告并跳过该站 —— **优雅降级，绝不静默失败**。

## 目录结构

```
app/                入口（crawl_guide / crawl_all / crawl_sites / export_cookies）
core/               引擎
  ├─ domain/        词库 / 词性格 / 站映射 / 登录规则
  ├─ interaction/   交互与偏好
  ├─ auth/          登录自动化 / cookie
  ├─ download/      下载 / 落盘 / 去重 / 调度
  ├─ engines/       51 个站搜索器
  ├─ filter/        相关与噪音过滤
  └─ bridges/       渲染器子进程桥
config/             静态配置（collector.yaml / seeds/ 2740 词）
data/               运行时数据（cookie / db / acl 数据）
知识库/             采集输出（知识库）
tests/              穷举 / 逐Task / 冒烟测试
docs/               directory-contract / output-spec
```

## 🏗 架构

```
app/        入口层（crawl_guide 智能引导 / crawl_all 批量 / crawl_sites 整站）
   │
   ▼
core/       引擎层（分层 + 单向依赖）
   ├─ interaction → domain（逻辑层：词库/性格/站映射）
   ├─ download / engines / filter（执行层：下载/搜索/过滤）
   ├─ auth（登录/cookie）  └─ bridges（渲染器桥）
   │
   ▼
config/ → data/（cookie/db）→ 知识库/（采集输出）
```

依赖方向：`app → core.*`，无循环引用，目录 ≤3 层（详见 `docs/directory-contract.md`）。

## 🧰 技术栈

- **Python 3.10+** / asyncio / SQLite（去重）
- **yt-dlp**：视频/音频下载
- **Crawl4AI / Scrapling / patchright / Playwright**：网页渲染、JS 攻坚、隐形浏览器
- **trafilatura**：正文去噪（HTML 双份落盘）
- **rank_bm25 / yake**：相关性与关键词过滤
- **text2vec**：语义扩展（可选）

## 🙏 致谢

本项目依赖以下开源项目，感谢它们的贡献：

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) · [Crawl4AI](https://github.com/unclecode/crawl4ai) · [Scrapling](https://github.com/D4Vinci/Scrapling) · [patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) · [Playwright](https://github.com/microsoft/playwright) · [trafilatura](https://github.com/adbar/trafilatura) · [rank-bm25](https://github.com/dorianbrown/rank_bm25) · [yake](https://github.com/LIAAD/yake)

## 📌 Roadmap

- [ ] 小红书/微博连根爬完善（借浏览器方案）
- [ ] 全量 2740 词跑批验证
- [ ] 更多内容类型的细化抓取（抖音图集/小红书图文等）
- [ ] 图形界面（网页/桌面端引导）

## 📮 反馈与贡献

欢迎各种形式的贡献 —— bug 报告、新增搜索器、文档、功能。

- 遇到问题：提 [Issue](https://github.com/SpiralQWQ/web-knowledge-crawler/issues)
- 欢迎 PR —— 请先读 [CONTRIBUTING_zh.md](CONTRIBUTING_zh.md)
- 安全问题？见 [SECURITY_zh.md](SECURITY_zh.md)
- 社区守则：[CODE_OF_CONDUCT_zh.md](CODE_OF_CONDUCT_zh.md)
- 变更历史：[CHANGELOG_zh.md](CHANGELOG_zh.md)
- 深入文档：[docs/ARCHITECTURE_zh.md](docs/ARCHITECTURE_zh.md) · [docs/GUIDE_zh.md](docs/GUIDE_zh.md) · [docs/directory-contract_zh.md](docs/directory-contract_zh.md) · [docs/output-spec_zh.md](docs/output-spec_zh.md)

提交前请运行 `tests/` 下的穷举/冒烟测试确认无回归。

## ❓ FAQ

**Q：为什么某个网站搜索不到/返回 0 条？**
可能是：①该站需登录（引导会自动弹登录页）；②外部工具缺失（日志会明确警告）；③被列入禁用清单（反爬极强）；④限流（程序自动跳过重试）。

**Q：必须装 yt-dlp / Crawl4AI 吗？**
不需要全装。工具缺失时对应网站会优雅降级（明确警告+跳过），其余网站正常。

**Q：爬取的数据存在哪？什么格式？**
默认 `知识库/{词}/{类型}/{站}/00_日期_标题_大小/` + `meta.json`。可用 `--out-dir` 换位置。详见 `docs/output-spec.md`。

**Q：大规模爬取会不会被封号？**
内置安全机制：低并发（默认 3 词）+ 站间延迟 + 超时重试，不碰反爬红线。

**Q：YouTube 下不了？**
YouTube 需本地代理（如 Clash，端口 7897），程序自动探测。

**Q：抖音/小红书要登录怎么办？**
引导会自动检测登录态：无登录 → 自动打开浏览器登录页 → 登录 → 自动收集 cookie → 二次校验。

**Q：能商用吗？**
AGPL-3.0 协议下可自由使用（衍生作品需开源）；闭源商用见 `COMMERCIAL.md`。

## 免责声明

本工具仅用于**个人对公开内容的研究与学习**。你需要自行负责：
- 遵守各网站服务条款与 `robots.txt`
- 遵守当地法律与版权规定
- 不得用于大规模抓取、DDoS 或任何非法用途

本项目不打包任何爬取的内容；爬取行为由使用者自行负责。

## 许可证

AGPL-3.0 — 见 [LICENSE](LICENSE)。如需商用，见 [COMMERCIAL.md](COMMERCIAL.md)。

## 💛 支持 / 打赏

如果这个项目对你有帮助，欢迎请我喝杯咖啡。完全自愿 —— 项目永远免费开源。对独立开发者来说，每一份小小的认可都意义重大。

<p align="center">
  <img src="assets/donate_wechat.jpg" alt="微信赞赏" width="200">
  <img src="assets/donate_alipay.jpg" alt="支付宝赞赏" width="200">
</p>

<p align="center"><i>谢谢你看到这里。🙏</i></p>
