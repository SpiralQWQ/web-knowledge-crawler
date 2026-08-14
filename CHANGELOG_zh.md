# 变更日志

本项目所有显著变更。格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [2.5.3] - 2026-08-13

### 新增

- 开源文档全面规范化（W01-W12）：中英双语 README（徽章/FAQ/示例）、Keep a Changelog 规范的 CHANGELOG、CONTRIBUTING、CODE_OF_CONDUCT、SECURITY、docs/ARCHITECTURE、docs/GUIDE、GitHub Issue/PR 模板

## [2.5.2] - 2026-08-12

### 新增

- `setup.py` 一键配置向导：回答几个问题 → 自动安装依赖 + 生成 `.env`

### 变更

- 以 AGPL-3.0 开源，中英双语文档 + 打赏码
- 隐私清洗：无 `.env` / `data/` / `知识库/`，配置路径全部占位符

## [2.5.1] - 2026-08-12

### 新增

- `docs/output-spec.md` — 采集输出格式标准（目录结构 / 命名 / meta.json / HTML 双份）

### 变更

- `知识库/` 定为输出目录名（放弃早期规划的 `output/`）
- README / CHANGELOG / docs 对齐 app/core 结构，中英双语

## [2.5.0] - 2026-08-12

### 新增

- `tests/fresh_exhaustive.py` — 全新穷举套件（T01-T19，102 项断言，含提示完整性检查），从零编写不复用

## [2.4.1] - 2026-08-12

### 新增

- `tests/post_refactor_smoke.py` — 重构后结构冒烟测试（146 文件编译 / 入口+模块 import / 51 搜索器实例化 / 断链 0）

## [2.4.0] - 2026-08-12

### 变更

- 架构重构为 `app/` + `core/`（目录契约）：`crawl_guide.py` 拆分到 `core/{domain,interaction,auth,download}`；helper → `core/bridges`；`shared` → `core/{download,auth,filter,domain}`；`search_engine` → `core/engines`；`tools` → `app`

## [2.3.1] - 2026-08-12

### 修复

- 真机实测 26 个缺陷：抖音连根借浏览器收集、登录判定防误判（关键 cookie 列匹配）、YouTube 代理、防呆（EOF/Ctrl+C）、大白话执行计划+就绪检查、逐条下载日志、大规模 `--out-dir`

## [2.3.0] - 2026-08-11

### 新增

- 智能爬取引导（`crawl_guide.py`）：点菜式交互 —— 词库整理、词性格、37 站映射、登录自动化、下载进度、连根爬

## [2.2.0] - 2026-08-10

### 变更

- 补丁重构（基于 100 仓库调研）：Sitemap 按词检索（rank_bm25）、正文去噪（trafilatura）、自动关键词（yake）、管线过滤、语义扩展（text2vec）— 相关率 76% → 80%

## [2.0.1] - 2026-08-10

### 修复

- claude_code_docs 域名失效 → 改 `platform.claude.com` sitemap 兜底

### 变更

- Cookie 硬性规则：需登录站必须注入 cookie，严禁匿名降级
- 剔除 6 个不可用站（禁用清单 6 → 12）

## [2.0.0] - 2026-08-10

### 新增

- CDP 借真实浏览器反爬（调试浏览器 9222）— 救活 10 站（抖音/微博/B站/力扣/码云/可汗/InfoQ/36氪/少数派/钛媒体），27 → 34 站真实内容

## [1.9] - 2026-08-10

### 测试

- 全站 200+ 实测：50 搜索器 3 词测试 27 站真实内容；195 整站 177 可达；10 轮回归通过

## [1.8] - 2026-08-10

### 新增

- 高价值站拯救（救活 5 站）：OpenAlex 替代 Google Scholar、ACL 本地 XML 搜索、medium/oschina 走 RSS、paperswithcode 并入 HuggingFace API — 真实内容 23 → 28 站

## [1.7] - 2026-08-10

### 修复

- 全站修复战役：通用 Sitemap 搜索器（救活 huxiu/opencode/cursor）、dblp 与会议站 API 修复、zhihu cookie 解锁 — 真实内容 9 → 23 站

## [1.6] - 2026-08-09

### 新增

- 隐形浏览器层（patchright / camofox）：HTML 回退链升级四级、搜索标题真实化

## [1.5.0] - 2026-08-09

### 新增

- JS 动态站攻坚层（Scrapling 桥）、下载器回退链、需登录站适配

## [1.4] - 2026-08-08

### 变更

- README 完整架构重写：三层架构、逐站反爬策略映射、数字校正（195 整站 / 8 大类 / 2740 词）

## [1.3] - 2026-08-08

### 新增

- 多类型扩展机制（网页自动挖内嵌资源）、播客 RSS 音频采集、音频类别（yt-dlp 下载）

## [1.2] - 2026-08-08

### 新增

- 多格式类型分发：按 URL 扩展名分流 30+ 格式（repo→git clone、video→yt-dlp、archive→zip…）

## [1.1] - 2026-08-08

### 修复

- 知乎反爬（Playwright + Edge 伪装）、cookie 导出 0 条、bat/.env 编码修复

## [1.0.0] - 2026-08-07

### 新增

- 首发：三分类采集系统、50 站搜索器、cookie 导出、SQLite 去重、规范落盘
