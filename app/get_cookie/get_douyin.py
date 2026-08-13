"""抖音 (douyin.com) Cookie 获取脚本（扫码登录通道）

抖音不使用浏览器 Cookie 导出（反爬强、需 msToken/sessionid 等专用键），
走 jiji262/douyin-downloader 的扫码登录：自动弹浏览器 → App 扫码 → 保存 Cookie。

用法:
  python app/get_cookie/get_douyin.py
  python app/get_cookie/get_douyin.py --config "<自定义config.yml路径>"

前置: .env 已配置 DD_DL_SRC（jiji262 源码目录）与 DD_DL_PY（其虚拟环境 python）
输出: 默认写入 DD_DL_SRC/config.yml（或 KC_DOUYIN_CONFIG 指定路径）
"""
import os
import subprocess
import sys

if not sys.stdout.isatty():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(BASE, "data", "cookies")


def _parse_env() -> dict:
    env = {}
    env_file = os.path.join(BASE, ".env")
    if os.path.isfile(env_file):
        try:
            for line in open(env_file, encoding="utf-8", errors="replace"):
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
        except Exception:  # noqa: BLE001
            pass
    return env


def _pick(key: str, env: dict) -> str:
    return (os.environ.get(key, "").strip() or env.get(key, "")).strip()


def _mask(p: str) -> str:
    try:
        s = str(p)
        s = s.replace(BASE, "<repo>").replace(BASE.replace("\\", "/"), "<repo>")
        home = os.path.expanduser("~")
        s = s.replace(home, "<home>").replace(home.replace("\\", "/"), "<home>")
        return s
    except Exception:  # noqa: BLE001
        return str(p)


def main() -> int:
    env = _parse_env()
    src = _pick("DD_DL_SRC", env)
    py = _pick("DD_DL_PY", env)
    if not src:
        print("[错误] 未配置 DD_DL_SRC（请在 .env 指向 jiji262/douyin-downloader 源码目录）")
        return 1
    if not os.path.isfile(os.path.join(src, "tools", "cookie_fetcher.py")):
        print(f"[错误] 未找到 {_mask(os.path.join(src, 'tools', 'cookie_fetcher.py'))}")
        return 1
    if not py:
        print("[错误] 未配置 DD_DL_PY（请在 .env 配置抖音下载器环境的 python）")
        return 1

    args = sys.argv[1:]
    cfg = _pick("KC_DOUYIN_CONFIG", env)
    if "--config" in args:
        i = args.index("--config")
        if i + 1 < len(args):
            cfg = args[i + 1]
            args = args[:i] + args[i + 2:]
        else:
            args = args[:i]
    if not cfg:
        cfg = os.path.join(src, "config.yml")

    print("═══ 导出 抖音 Cookie（扫码登录）═══")
    print(f"  源码: {_mask(src)}")
    print(f"  配置: {_mask(cfg)}")
    print("  [1] 将弹出浏览器，打开抖音网页版")
    print("  [2] 请用「抖音App」扫码登录（没有账号就注册一个）")
    print("  [3] 登录成功、看到主页后，回到终端按回车")
    print("  [4] 提示 Saved ... 就成功了")
    print("  (若浏览器没自动打开，等 1 分钟重试)")

    sub_env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    r = subprocess.run([py, "-m", "tools.cookie_fetcher", "--config", cfg],
                       cwd=src, env=sub_env)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
