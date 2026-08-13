@echo off
title 启动 Edge 调试模式（Cookie 读取前置）
rem ============================================================
rem  启动 Edge 调试模式（专用 profile）
rem  只负责打开专用 Edge 浏览器，网址请自己复制粘贴到地址栏
rem
rem  用法：
rem    1. 双击本脚本（弹出专用 Edge 窗口）
rem    2. 把下面网址复制到地址栏打开，登录站点
rem    3. 保持 Edge 开着，运行 get_xxx.bat 或 一键导出全部.bat 导出 Cookie
rem    4. 关掉窗口 = 关闭调试 Edge（登录态保留在专用 profile）
rem ============================================================
set "EDGE="
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" set "EDGE=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if "%EDGE%"=="" if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" set "EDGE=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
if "%EDGE%"=="" (
  echo [错误] 找不到 Edge，请先安装 Microsoft Edge
  pause
  exit /b 1
)
set "BASE=%~dp0..\.."
set "PROFILE=%BASE%\data\edge_profile"
if not exist "%PROFILE%" mkdir "%PROFILE%"
echo ============================================================
echo  即将打开专用 Edge 浏览器（调试模式）
echo  网址清单见：config\login_sites.txt
echo  或：config\login_sites.txt
echo  把网址复制到 Edge 地址栏打开，逐个登录即可
echo ============================================================
echo.
start "" "%EDGE%" --remote-debugging-port=9222 --user-data-dir="%PROFILE%" --restore-last-session
echo  已启动！请保持 Edge 窗口开着，然后打开网址逐个登录
echo.
echo  验证：浏览器地址栏输入  http://localhost:9222/json/version
echo  能看到 JSON 就说明调试端口 OK
echo ============================================================
pause
