"""批量生成逐站 Cookie 获取脚本的 .bat 快捷入口 + 一键全部 .bat。

用法:
  python tools/get_cookie/_gen_bats.py

产出（覆盖写入 tools/get_cookie/*.bat）:
  get_<site>.bat    每个站点一个（双击 → 调 get_<site>.py）
  run_all.bat       一键全部（串行跑所有 export_site 型站点；抖音扫码需手动单独跑）
"""
import os
import re
import sys

if not sys.stdout.isatty():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(HERE))

# 从 docstring 第一行取站点中文名
def site_title(py_path: str) -> str:
    s = open(py_path, encoding="utf-8").read()
    m = re.search(r'"""(.+?)\n', s)
    return m.group(1).strip() if m else os.path.basename(py_path)

# 脚本文件名 → 站点名（去掉 get_ 前缀与 .py）
def site_name(fn: str) -> str:
    return fn[len("get_"):-len(".py")]

EXCLUDE = {"_base.py", "_gen_bats.py", "_cdp.py"}
SKIP_ALL = {"get_douyin.py"}  # 扫码交互，不进一键全部

pys = sorted(f for f in os.listdir(HERE) if f.endswith(".py") and f not in EXCLUDE)

HEADER = """@echo off
rem 前置：
rem   [推荐] 先运行「启动Edge调试模式.bat」，登录站点后保持 Edge 打开，再运行本脚本
rem   [备选] 若未用调试模式，请关闭浏览器后再运行（读取 profile）
set "BASE=%~dp0..\\.."
set "ENV=%BASE%\\.env"
if exist "%ENV%" (
  for /f "usebackq tokens=1,* delims==" %%a in ("%ENV%") do (
    if /i "%%a"=="CRAWL4AI_PY" if not defined CRAWL4AI_PY set "CRAWL4AI_PY=%%b"
  )
)
if "%CRAWL4AI_PY%"=="" set "CRAWL4AI_PY=python"
"""

FOOTER = """
if errorlevel 1 (
  echo [失败] 导出出错。常见原因：
  echo   1. 浏览器还开着（profile 锁）→ 关掉浏览器再试
  echo   2. 没登录该站点 → 先登录再导出
  echo   3. CRAWL4AI_PY 没配置 → 在 .env 里配置 crawl4ai 环境 python
)
pause
"""

def gen_single_bat(fn: str) -> str:
    title = site_title(os.path.join(HERE, fn))
    return (HEADER + f'title {title}\n'
            f'echo 正在导出 {title} ...\n'
            f'"%CRAWL4AI_PY%" "%~dp0{fn}" %*\n'
            + FOOTER)

def gen_all_bat() -> str:
    lines = [HEADER, "title 一键导出全部站点 Cookie（抖音需单独扫码）", "echo 开始串行导出全部站点 Cookie...", "echo."]
    for fn in pys:
        if fn in SKIP_ALL:
            continue
        lines.append(f'echo.\necho ===== {site_title(os.path.join(HERE, fn))} =====\n'
                     f'"%CRAWL4AI_PY%" "%~dp0{fn}"')
    lines.append("echo.")
    lines.append("echo 全部导出完成！")
    lines.append("echo 抖音 Cookie 请单独运行 get_douyin.bat 扫码登录")
    lines.append("echo 建议先运行「启动Edge调试模式.bat」并保持 Edge 打开，导出更完整")
    lines.append("pause")
    return "\n".join(lines)

def gen_douyin_bat() -> str:
    return ("""@echo off
title 抖音 Cookie 获取（扫码登录）
rem 抖音不走浏览器导出：弹浏览器 → App 扫码 → 保存 Cookie 到 jiji262 config.yml
set "BASE=%~dp0..\\.."
set "ENV=%BASE%\\.env"
if exist "%ENV%" (
  for /f "usebackq tokens=1,* delims==" %%a in ("%ENV%") do (
    if /i "%%a"=="CRAWL4AI_PY" if not defined CRAWL4AI_PY set "CRAWL4AI_PY=%%b"
  )
)
if "%CRAWL4AI_PY%"=="" set "CRAWL4AI_PY=python"
echo 正在打开抖音登录页面（请用抖音App扫码）...
echo 登录成功、看到主页后，回到本窗口按回车
"%CRAWL4AI_PY%" "%~dp0get_douyin.py" %*
pause
""")

n = 0
for fn in pys:
    bat = os.path.join(HERE, fn[: -len(".py")] + ".bat")
    content = gen_douyin_bat() if fn == "get_douyin.py" else gen_single_bat(fn)
    # 中文 Windows：bat 用 GBK 编码 + CRLF 换行，避免 UTF-8 被 cmd 误读
    with open(bat, "wb") as f:
        f.write(content.replace("\n", "\r\n").encode("gbk", errors="replace"))
    n += 1

with open(os.path.join(HERE, "run_all.bat"), "wb") as f:
    f.write(gen_all_bat().replace("\n", "\r\n").encode("gbk", errors="replace"))

print(f"✅ 生成 {n} 个站点 bat + run_all.bat → {HERE}（GBK/CRLF 编码）")
