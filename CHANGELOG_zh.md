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

- `docs/输出规范.md` — 采集输出格式标准（目录结构 / 命名 / meta.json / HTML 双份）

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

## [2.0.0] - 2026-08-10

### 新增

- CDP 借真实浏览器反爬（调试浏览器 9222）— 救活 10 站（抖音/微博/B站/力扣/码云/可汗/InfoQ/36氪/少数派/钛媒体），27 → 34 站真实内容

## [1.5.0] - 2026-08-09

### 新增

- JS 动态站攻坚层（Scrapling 桥）、下载器回退链、需登录站适配

## [1.0.0] - 2026-08-07

### 新增

- 首发：三分类采集系统、50 站搜索器、cookie 导出、SQLite 去重、规范落盘
