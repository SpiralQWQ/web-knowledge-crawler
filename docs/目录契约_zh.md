# 目录契约 · web-knowledge-crawler

> 作用：本项目文件组织的唯一标准。任何新代码都应遵循它。
> 选型：范式 C 变体（分层 + 业务域混合），Python 采集项目。

---

## 1. 目标结构

```
web-knowledge-crawler/
├── app/                  # ★ 入口层：对外命令入口
│   ├── crawl_guide.py    #   智能爬取引导
│   ├── crawl_all.py      #   大规模爬取
│   ├── crawl_sites.py    #   整站爬取
│   └── export_all_cookies.py / export_cookies.py
├── core/                 # ★ 引擎层
│   ├── engines/          #   站点搜索器
│   ├── bridges/          #   渲染器/浏览器子进程桥
│   ├── download/         #   下载 / 落盘 / 去重 / 调度
│   ├── auth/             #   cookie / 登录
│   ├── filter/           #   相关 / 噪音过滤
│   ├── interaction/      #   交互与偏好
│   └── domain/           #   词库 / 词性格 / 站映射 / 登录规则
├── config/               # 静态配置（collector.yaml / seeds/）
├── data/                 # 运行时数据（cookie / db / acl 数据）
├── 知识库/               # 采集输出（知识库）
├── tests/                # 测试（穷举 / 逐Task / 冒烟）
├── docs/                 # 文档（本契约 / 输出规范）
└── 根：README.md / CHANGELOG.md / LICENSE / requirements.txt
```

## 2. 职责边界（高内聚 · 低耦合）

| 目录 | 只允许放 | 禁止放 |
|---|---|---|
| app/ | 入口编排、参数解析、调用 core | 业务逻辑 |
| core/engines/ | 站点搜索器 | 下载/落盘 |
| core/bridges/ | 子进程桥（渲染器/浏览器包装） | 业务逻辑 |
| core/download/ | 下载 / 落盘 / 去重 / 调度 | 搜索器 |
| core/auth/ | cookie 读取 / 登录 | 下载 |
| core/filter/ | 相关 / 噪音过滤 | 下载 |
| core/interaction/ | 交互函数（问用户） | 下载实现 |
| core/domain/ | 词库/词性格/站映射纯逻辑 | 网络 / IO |
| config/ | 静态配置 | 运行时状态 |
| data/ | 运行时数据 | 代码 |
| 知识库/ | 采集输出 | 代码 |
| tests/ | 测试脚本 | 临时文件 |

## 3. 单向依赖规则

```
app → core.{engines,bridges,download,auth,filter,interaction,domain}
                    ↑
       （core 内部：interaction/domain → download → bridges/engines）
```

- **禁止反向依赖**：core 不能 import app；app/core 不依赖 data/ 等运行时目录
- **core 内部**：逻辑层（interaction/domain）可调执行层（download/auth/engines/bridges）；执行层禁止调交互层
- 跨目录调用走公开入口（`__init__.py` 或明确函数），禁止 import 私有内部

## 4. 禁止项（Hard Rules）

- ❌ 禁止按文件后缀建目录（`*.py`、`helpers/` 平铺散落）
- ❌ 禁止业务逻辑散落 utils/（纯函数放 core/ 内对应子模块）
- ❌ 禁止目录嵌套超过 3 层
- ❌ 禁止测试/配置/部署文件混入 core/
- ❌ 禁止 `.env` 真实文件入库（只入 `.env.example`）
- ❌ 禁止跨目录 import 内部文件（必须走公开 API）
- ❌ 禁止运行时状态（prefs/缓存）与静态配置混放 config/

## 5. 新增代码约定

- 新增搜索器 → `core/engines/`
- 新增下载类型 → `core/download/`
- 新增交互 → `core/interaction/`
- 新增纯工具 → `core/` 内对应子模块（禁止建顶层 `shared/`）
- **永不改变既有结构，只在对应域内新增。**
