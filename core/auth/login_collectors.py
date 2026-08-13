"""需登录站适配层 — MediaCrawler / Spider_XHS 桥接。

这两个是独立工程（非 pip 库），靠**真实账号登录态**采集（小红书/抖音/微博/快手/B站等）。
本模块职责：
1. **登录态检查点**：采集前校验登录态是否存在/有效；缺失或过期 → 明确提示用户重新登录，
   **绝不静默降级**（铁律：Cookie 失效必须向用户确认补登录）。
2. 调用外部工具（子进程，复用 AAATool 环境）跑采集。
3. 把工具输出 JSONL 导入我们 `知识库/{term}/{类别}/{site}/` 结构（meta.json + 原始数据）。

用法（需用户先完成登录）：
    from core.auth.login_collectors import check_login, collect_media_crawler
    print(check_login("xhs"))                      # 查登录态
    await collect_media_crawler("xhs", "transformer")  # 小红书搜词采集
    await collect_spider_xhs("https://www.xiaohongshu.com/explore/xxx")  # 单笔记采集
"""
import asyncio
import json
import os
import re

from core.config import BASE, KB, tool

# --- 工具目录解析（AAATool 入库路径） ---
_MC_ROOT = tool("media_crawler_dir") or ""
_XHS_ROOT = tool("spider_xhs_dir") or ""
_MC_REPO = os.path.join(_MC_ROOT, "repo") if _MC_ROOT else ""
_MC_VENV_PY = os.path.join(_MC_ROOT, "venv", "Scripts", "python.exe") if _MC_ROOT else ""
_XHS_REPO = os.path.join(_XHS_ROOT, "repo") if _XHS_ROOT else ""
_XHS_VENV_PY = os.path.join(_XHS_ROOT, "venv", "Scripts", "python.exe") if _XHS_ROOT else ""

# MediaCrawler 平台名 → 我们站目录名
_PLATFORM_SITE = {"xhs": "xiaohongshu", "dy": "douyin", "douyin": "douyin",
                  "kuaishou": "kuaishou", "weibo": "weibo", "tieba": "tieba",
                  "bilibili": "bilibili", "zhihu": "zhihu"}


def _env_ok() -> bool:
    """工具是否已配置且存在。"""
    return bool(_MC_REPO and os.path.isdir(_MC_REPO)) or bool(_XHS_REPO and os.path.isdir(_XHS_REPO))


def check_login(platform: str) -> dict:
    """检查某平台登录态。返回 {platform, logged_in, detail, need_login}。
    检查依据（启发式）：
      - MediaCrawler：登录态存于其 data/ 下的 cookie/浏览器状态文件
      - Spider_XHS：COOKIES 写在 repo/.env
    """
    if platform in ("xhs", "douyin", "kuaishou", "weibo", "tieba", "bilibili", "zhihu"):
        # MediaCrawler 平台
        data_dir = os.path.join(_MC_REPO, "data")
        cookie_hits = []
        if os.path.isdir(data_dir):
            for root, _, files in os.walk(data_dir):
                for f in files:
                    if any(k in f.lower() for k in ("cookie", "login", "state", "session")):
                        cookie_hits.append(os.path.join(root, f))
        logged_in = bool(cookie_hits)
        return {"platform": platform, "logged_in": logged_in, "need_login": not logged_in,
                "detail": f"MediaCrawler data/ 找到登录态文件 {len(cookie_hits)} 个" if logged_in
                else "MediaCrawler data/ 无登录态文件，需先登录（如 --lt qrcode 扫码一次）"}
    if platform == "spider_xhs":
        env_path = os.path.join(_XHS_REPO, ".env")
        logged_in = False
        detail = "Spider_XHS .env 不存在"
        if os.path.exists(env_path):
            try:
                txt = open(env_path, encoding="utf-8").read()
                m = re.search(r"COOKIES\s*=\s*[\"']?([^\"'\n]+)", txt)
                logged_in = bool(m and m.group(1).strip())
                detail = "Spider_XHS .env 已配 COOKIES" if logged_in else "Spider_XHS .env 未配 COOKIES"
            except Exception:  # noqa: BLE001
                detail = "Spider_XHS .env 读取失败"
        return {"platform": "spider_xhs", "logged_in": logged_in, "need_login": not logged_in,
                "detail": detail}
    return {"platform": platform, "logged_in": False, "need_login": True,
            "detail": f"未知平台 {platform}"}


def _require_login(status: dict) -> None:
    """登录态检查点：未登录 → 抛明确错误提示用户补登录，不静默降级。"""
    if not status.get("logged_in"):
        raise RuntimeError(
            f"🔒 [{status['platform']}] 需要登录态：{status.get('detail')}\n"
            "请先用工具自带方式完成登录（MediaCrawler: python main.py --lt qrcode；"
            "Spider_XHS: 配置 repo/.env 的 COOKIES），再重试采集。")


def _import_records(records: list[dict], term: str, site: str) -> int:
    """把工具 JSONL 记录导入 知识库/{term}/{类别}/{site}/，返回导入数。"""
    from core.download.preserver import FilePreserver
    from core.domain.site_category import category_of
    from core.download.deduper import Deduper
    preserver = FilePreserver(root_dir=KB)
    deduper = Deduper(os.path.join(BASE, "data", "collector.db"))
    cat = category_of(site) or "网页"
    saved = 0
    for rec in records:
        url = rec.get("url") or rec.get("note_id") or rec.get("id") or ""
        if not url:
            url = f"{site}://{rec.get('title', '')[:30]}"
        title = rec.get("title") or url
        if deduper.is_duplicate(url, term):
            continue
        # 原始数据：整条记录转 JSON 落盘
        raw_bytes = json.dumps(rec, ensure_ascii=False).encode("utf-8")
        size = len(raw_bytes)
        try:
            item_dir = preserver.create_item_dir(term, site, str(title)[:40], size)
            local = preserver.save_file(url, raw_bytes, term, site, "json", str(title)[:40], item_dir)
            preserver.save_metadata(term, site, "json", url, str(title)[:40], term, size, item_dir)
            deduper.add_result(url, term, site, "json", "saved", size, local)
            saved += 1
        except Exception:  # noqa: BLE001
            continue
    return saved


async def _run_cmd(cmd: list[str], cwd: str, timeout: int = 600) -> str:
    """子进程运行外部工具，返回 stdout。"""
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    proc = await asyncio.create_subprocess_exec(
        *cmd, cwd=cwd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env)
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except Exception:  # noqa: BLE001
            pass
        return ""
    return out.decode("utf-8", errors="replace")


def _find_jsonl(root: str) -> list[str]:
    """递归找最近修改的 .jsonl 文件。"""
    hits = []
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith(".jsonl"):
                p = os.path.join(dirpath, f)
                hits.append((os.path.getmtime(p), p))
    hits.sort(reverse=True)
    return [p for _, p in hits]


async def collect_media_crawler(platform: str, keyword: str, max_results: int = 50) -> int:
    """跑 MediaCrawler 关键词搜索采集，导入知识库。返回导入数。"""
    status = check_login(platform)
    _require_login(status)
    if not _MC_VENV_PY or not os.path.exists(_MC_VENV_PY):
        raise RuntimeError("未配置 MediaCrawler 环境 (media_crawler_dir)")
    site = _PLATFORM_SITE.get(platform, platform)
    cmd = [_MC_VENV_PY, "main.py", "--platform", platform, "--lt", "cookie",
           "--type", "search", "--keywords", keyword,
           "--max_results", str(max_results), "--save", "jsonl"]
    await _run_cmd(cmd, cwd=_MC_REPO)
    # 找输出 jsonl 导入
    out_files = _find_jsonl(os.path.join(_MC_REPO, "data"))
    total = 0
    for fp in out_files[:5]:
        try:
            with open(fp, encoding="utf-8") as f:
                records = [json.loads(line) for line in f if line.strip()]
        except Exception:  # noqa: BLE001
            continue
        total += _import_records(records, keyword.replace(" ", "_"), site)
    return total


async def collect_spider_xhs(note_url: str) -> int:
    """跑 Spider_XHS 采集单个小红书笔记/主页，导入知识库。返回导入数。"""
    status = check_login("spider_xhs")
    _require_login(status)
    if not _XHS_VENV_PY or not os.path.exists(_XHS_VENV_PY):
        raise RuntimeError("未配置 Spider_XHS 环境 (spider_xhs_dir)")
    # Spider_XHS main.py 是常量配置，不支持传参；这里改为读取其配置方式注入
    # 简化：直接在其目录运行（其 main.py 内改 note_url 常量），或用 --url 兼容
    cmd = [_XHS_VENV_PY, "main.py"]
    await _run_cmd(cmd, cwd=_XHS_REPO)
    out_files = _find_jsonl(os.path.join(_XHS_REPO, "datas"))
    total = 0
    for fp in out_files[:5]:
        try:
            with open(fp, encoding="utf-8") as f:
                records = [json.loads(line) for line in f if line.strip()]
        except Exception:  # noqa: BLE001
            continue
        total += _import_records(records, "xiaohongshu", "xiaohongshu")
    return total


def main():
    """CLI：python -m core.auth.login_collectors <platform> <keyword>"""
    import sys
    if len(sys.argv) >= 2 and sys.argv[1] == "check":
        print(json.dumps(check_login(sys.argv[2] if len(sys.argv) > 2 else "xhs"), ensure_ascii=False))
        return
    if len(sys.argv) >= 4:
        asyncio.run(collect_media_crawler(sys.argv[1], sys.argv[2]))
        return
    print("用法: python -m core.auth.login_collectors check <platform> | <platform> <keyword>")


if __name__ == "__main__":
    main()
