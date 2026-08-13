"""camofox 可选 Firefox 隐形浏览器封装 — REST 调用 AAATool 的 camofox server。

camofox 是 Firefox 系隐形浏览器（A级，与 patchright 的 Chromium 系互补），
适合 Chromium 被检测的高反爬场景。本模块：
1. 确保 camofox server 运行（未启动则拉起 `node server.js`）
2. POST /tabs 建标签页 → evaluate 取真实标题 + 页面 HTML
3. stdout 输出 {url, success, title, html, error}（与其他 helper 一致）

可选后端：默认不接入下载器自动回退链，供高反爬站手动调用。
用法:
    python collector/camofox_helper.py <url> [--stop]
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request

# 脚本直接运行（python collector/camofox_helper.py）时，把项目根加入 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import BASE, tool  # noqa: E402

_CAMOFOX_DIR = tool("camofox_dir") or ""
_SERVER = "http://localhost:9377"
_START_WAIT = 15  # server 启动等待秒数


def _emit(data: dict):
    print(json.dumps(data, ensure_ascii=False, default=str))


def _req(method: str, path: str, body: dict | None = None) -> dict | None:
    """REST 调用 camofox server，返回 JSON 或 None。"""
    url = _SERVER + path
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:  # noqa: BLE001
        return None


def _health() -> bool:
    d = _req("GET", "/health")
    return bool(d and d.get("ok"))


def _start_server() -> bool:
    """启动 camofox server（后台），等待就绪。"""
    if not _CAMOFOX_DIR or not os.path.isdir(_CAMOFOX_DIR):
        return False
    env = dict(os.environ, PYTHONUTF8="1", CAMOFOX_CRASH_REPORT_ENABLED="false")
    logf = open(os.path.join(BASE, "temp", "camofox_server.log"), "a", encoding="utf-8")
    subprocess.Popen(["node", "server.js"], cwd=_CAMOFOX_DIR,
                     stdout=logf, stderr=subprocess.STDOUT, env=env,
                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    for _ in range(_START_WAIT):
        time.sleep(1)
        if _health():
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description="camofox 隐形浏览器封装")
    parser.add_argument("url")
    parser.add_argument("--stop", action="store_true", help="结束时关闭 server")
    args = parser.parse_args()

    try:
        if not _CAMOFOX_DIR:
            _emit({"url": args.url, "success": False, "title": "", "html": "", "error": "未配置 camofox_dir"})
            return
        if not _health() and not _start_server():
            _emit({"url": args.url, "success": False, "title": "", "html": "",
                   "error": "camofox server 启动失败"})
            return
        # 建标签页
        tab = _req("POST", "/tabs", {"userId": "kc", "sessionKey": "helper", "url": args.url})
        if not tab or "tabId" not in tab:
            _emit({"url": args.url, "success": False, "title": "", "html": "", "error": "建标签页失败"})
            return
        tid = tab["tabId"]
        time.sleep(4)  # 等页面加载
        # evaluate 取标题 + HTML（userId 在请求体内）
        ev = _req("POST", f"/tabs/{tid}/evaluate",
                  {"userId": "kc", "expression": "document.title + '\\n' + document.documentElement.outerHTML"})
        result = (ev or {}).get("result") or (ev or {}).get("value") or ""
        if isinstance(result, str) and "\n" in result:
            title, html = result.split("\n", 1)
        else:
            title, html = "", str(result)
        _emit({"url": args.url, "success": bool(html), "title": (title or "").strip()[:200],
               "html": html, "error": ""})
    except Exception as e:  # noqa: BLE001
        _emit({"url": args.url, "success": False, "title": "", "html": "", "error": str(e)[:300]})
    finally:
        if args.stop:
            _req("POST", "/pressure/cleanup")


if __name__ == "__main__":
    main()
