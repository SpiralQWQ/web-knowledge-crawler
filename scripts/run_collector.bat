@echo off
title web-knowledge-crawler 采集器
rem ============================================================
rem  web-knowledge-crawler 运行入口（Windows）
rem  用法: run_collector.bat <参数...>
rem  示例:
rem    run_collector.bat --stats
rem    run_collector.bat --web config\seeds\web_seeds.txt
rem    run_collector.bat --paper config\seeds\paper_queries.txt
rem    run_collector.bat --discover-repos --min-stars 500
rem ============================================================
cd /d "%~dp0.."
python -m app.cli %*
pause
