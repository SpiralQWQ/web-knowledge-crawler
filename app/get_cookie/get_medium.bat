@echo off
rem 前置：
rem   [推荐] 先运行「start_edge_debug_mode.bat」，登录站点后保持 Edge 打开，再运行本脚本
rem   [备选] 若未用调试模式，请关闭浏览器后再运行（读取 profile）
set "BASE=%~dp0..\.."
set "ENV=%BASE%\.env"
if exist "%ENV%" (
  for /f "usebackq tokens=1,* delims==" %%a in ("%ENV%") do (
    if /i "%%a"=="CRAWL4AI_PY" if not defined CRAWL4AI_PY set "CRAWL4AI_PY=%%b"
  )
)
if "%CRAWL4AI_PY%"=="" set "CRAWL4AI_PY=python"
title Medium (medium.com) Cookie 获取脚本
echo 正在导出 Medium (medium.com) Cookie 获取脚本 ...
"%CRAWL4AI_PY%" "%~dp0get_medium.py" %*

if errorlevel 1 (
  echo [失败] 导出出错。常见原因：
  echo   1. 浏览器还开着（profile 锁）→ 关掉浏览器再试
  echo   2. 没登录该站点 → 先登录再导出
  echo   3. CRAWL4AI_PY 没配置 → 在 .env 里配置 crawl4ai 环境 python
)
pause
