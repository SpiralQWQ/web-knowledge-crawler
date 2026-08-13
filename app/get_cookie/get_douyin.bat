@echo off
title 抖音 Cookie 获取（扫码登录）
rem 抖音不走浏览器导出：弹浏览器 → App 扫码 → 保存 Cookie 到 jiji262 config.yml
set "BASE=%~dp0..\.."
set "ENV=%BASE%\.env"
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
