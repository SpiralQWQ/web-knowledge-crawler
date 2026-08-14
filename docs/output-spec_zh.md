# 输出规范 · web-knowledge-crawler 采集结果落盘标准

> 依据：`core/download/preserver.py`（落盘器实现）
> 输出目录固定为 **`知识库/`**（中文名，采集输出）。

---

## 一、落盘根目录

| 入口 | 默认根目录 | 覆盖方式 |
|---|---|---|
| 大规模爬取 | `知识库/{词}/` | `crawl_all --out-dir <路径>` |
| 指定爬取 | `知识库/指定爬取/` | 引导内选自定义路径 |
| 整站爬取 | `知识库/{站点名}/` | — |

## 二、目录结构（三层规范）

```
知识库/
└── {词或"指定爬取"}/
    └── {类型}/                  # 视频/网页/论文/代码/数据集/文档/课程/题库/音频...
        └── {站名}/
            └── 00_20260812_标题_2.1M/   # ★ 序号_日期_标题_大小
                ├── 原始文件.mp4/.pdf/.html
                ├── 标题_正文.txt        # HTML 站的双份：去噪正文（trafilatura）
                └── meta.json            # 元数据
```

## 三、命名规范（`preserver.py`）

- **子文件夹名**：`{序号:02d}_{日期YYYYMMDD}_{关键标题}_{大小}`（如 `00_20260812_Attention_is_all_you_need_2.1M`）
  - 序号：同目录内自增（`00`, `01`, `02`...），断点续爬不重复
  - 标题：取前 30 字符，非法字符 `\/:*?"<>|` → `_`，空则 `untitled`
  - 大小：≥1MB 显示 `X.XM`，≥1KB 显示 `X.XK`，否则 `X.B`
- **文件名清洗**：`_safe_filename` 最多 120 字符，非法字符替换
- **词/站名**：空格 → `_`，清洗后最多 60/40 字符

## 四、meta.json 字段

每次落盘写一份，记录该条内容的元数据：

| 字段 | 含义 |
|---|---|
| url | 原始来源 URL |
| title | 标题 |
| original_term | 触发采集的词 |
| file_type | 类型（pdf/video/html/repo...） |
| size | 字节数 |
| saved_path | 落盘路径 |
| site | 站点名 |
| timestamp | 采集时间 |

（具体字段以 `preserver.save_metadata` 为准，按类型略有差异）

## 五、类型分发（下载策略）

```
repo→git clone | video→yt-dlp(mp4) | pdf→直连 | archive→zip
html→Crawl4AI/Scrapling渲染(markdown/正文) | audio→RSS+yt-dlp
json/md→真实文件 | 网页→原始.html + 去噪正文.txt 双份
```

## 六、相关代码

- `core/download/preserver.py`：落盘器（命名/meta/双份）
- `core/download/deduper.py`：SQLite 去重（URL×词 唯一键，防止重复落盘）
- `core/download/downloader.py`：下载策略分流
