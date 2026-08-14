# 使用指南

> 日常怎么用 `web-knowledge-crawler` —— 从第一次运行到大规模爬取。所有输出默认落在 `知识库/`（见 `docs/output-spec.md`）。

## 快速开始

```bash
# 1. 开箱即用配置向导（推荐）
python setup.py          # 回答几个问题 → 装依赖 + 生成 .env

# 2. 运行智能引导
python app/crawl_guide.py
```

手动安装：`pip install -r requirements.txt`，再复制 `.env.example` 为 `.env` 填写路径。

---

## 模式一 —— 指定爬取（贴链接下载）

`python app/crawl_guide.py` → 选 **1**。

1. 粘贴链接 —— 分享口令 / 短链 / 普通 URL 都行，自动提取真实链接。
2. 自动认出网站（抖音 / B站 / YouTube / 微博 / 小红书 / …）。
3. 选择是否**连根爬**（顺带下载作者最近的系列）。
4. 选速度：🐇快速 / 🚶标准 / 🐢全量。
5. 选保存位置（默认 `知识库/指定爬取/`，可自定义）。
6. 大白话确认将做什么 —— 回车开跑。

> 提示：误按 Ctrl+C / Ctrl+D 不会崩。非法输入自动回退默认。

---

## 模式二 —— 大规模爬取（选词选站批量搜）

`python app/crawl_guide.py` → 选 **2**。

1. **词来源** —— 手输 / 导入乱格式词库（自动整理）/ 内置 2740 词表。
2. 词自动识别**性格**（学术 / 教程 / 热点 / 代码）→ 推荐内容类型。
3. 选内容类型（论文 / 视频 / 文章 / … 可加可减）。
4. 选网站（跳过 → 按推荐）。
5. 细节：时间范围 / 每站条数 / 多集 / 附件。
6. 选速度：🐇快速=安全稍快，🚶标准，🐢全量。
7. 选保存位置。
8. 大白话确认前做**就绪检查** —— 逐站显示浏览器 / 登录态，检测到浏览器没开会自动启动调试浏览器。然后开跑，逐条进度日志。

> 速度影响并发（默认 3 词同时）与站间延迟 —— 调校为安全不封号。

---

## 直接命令行（进阶）

```bash
# 从词表文件爬取指定站（--terms 是词表文件路径，每行一个词）
python app/crawl_all.py --terms config/seeds/vocab_terms.txt --sites arxiv --max-results 5

# 自定义输出目录
python app/crawl_all.py --terms config/seeds/vocab_terms.txt --sites arxiv,bilibili \
    --max-results 5 --out-dir /你的输出目录

# 整站爬取
python app/crawl_sites.py

# 导出需登录站的 cookie
python app/export_cookies.py
python app/export_all_cookies.py
```

`python app/crawl_all.py --help` 列出全部参数。

---

## 速度预设

| 预设 | 并发 | 站间延迟 | 何时用 |
|---|---|---|---|
| 🐇 快速 | 高 | 小 | 赶时间且信任站点 |
| 🚶 标准 | 3 词 | 适中 | 默认，安全均衡 |
| 🐢 全量 | 低 | 更大 | 大批量 / 谨慎防封 |

---

## 常见情况处理

### "为什么某个网站返回 0 条？"
1. 该站需登录 —— 引导会自动弹登录页；登录一次后自动收集 cookie。
2. 外部工具缺失（yt-dlp / Crawl4AI / Playwright…）—— 明确警告并跳过该站。
3. 被列入禁用清单（反爬极强）—— 明确记录，绝不清零假装成功。
4. 限流 —— 程序自动跳过重试。

### YouTube 下不了？
YouTube 需本地代理（如 Clash，端口 7897）；程序自动探测。

### 抖音 / 小红书要登录？
引导自动检测登录态：未登录 → 自动开浏览器登录页 → 登录 → 自动收集 cookie → 二次校验。

### 数据存在哪？
`知识库/{词}/{类型}/{站}/00_日期_标题_大小/` + `meta.json`，外加 HTML 双份便于浏览。可用 `--out-dir` 换位置。

### 中途 Ctrl+C？
安全 —— 已下载的已落盘，其余跳过。中断无妨。

---

## 排障速查

| 现象 | 可能原因 | 处理 |
|---|---|---|
| 某站 `403` / 空结果 | cookie 过期 | 引导里重新登录，或 `python app/export_cookies.py` |
| 就绪检查提示"浏览器没开" | 调试浏览器未启动 | 引导自动启动（或手动开 Chrome `--remote-debugging-port=9222`） |
| 某登录站提示"未登录" | 缺 cookie | 先做一次指定爬取完成登录 |
| 视频下载失败 | yt-dlp 缺失 / YouTube 需代理 | 装 yt-dlp，或开本地代理 |
| GitHub/Gitee 限流 | 没配 token | 在 `.env` 里设 `GH_TOKEN` |
