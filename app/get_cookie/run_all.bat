@echo off
rem 前置：
rem   [推荐] 先运行「启动Edge调试模式.bat」，登录站点后保持 Edge 打开，再运行本脚本
rem   [备选] 若未用调试模式，请关闭浏览器后再运行（读取 profile）
set "BASE=%~dp0..\.."
set "ENV=%BASE%\.env"
if exist "%ENV%" (
  for /f "usebackq tokens=1,* delims==" %%a in ("%ENV%") do (
    if /i "%%a"=="CRAWL4AI_PY" if not defined CRAWL4AI_PY set "CRAWL4AI_PY=%%b"
  )
)
if "%CRAWL4AI_PY%"=="" set "CRAWL4AI_PY=python"

title 一键导出全部站点 Cookie（抖音需单独扫码）
echo 开始串行导出全部站点 Cookie...
echo.
echo.
echo ===== 36氪 (36kr.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_36kr.py"
echo.
echo ===== 51CTO (51cto.com) + AI前线 (ai.51cto.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_51cto.py"
echo.
echo ===== 飞桨 AI Studio (aistudio.baidu.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_aistudio.py"
echo.
echo ===== AI Alignment Forum (alignmentforum.org) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_alignmentforum.py"
echo.
echo ===== 阿里云开发者社区 (developer.aliyun.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_aliyun_dev.py"
echo.
echo ===== 智源社区 (hub.baai.ac.cn) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_baai.py"
echo.
echo ===== 智谱 GLM 开放平台 (open.bigmodel.cn) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_bigmodel.py"
echo.
echo ===== B站 (bilibili.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_bilibili.py"
echo.
echo ===== The Changelog (changelog.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_changelog.py"
echo.
echo ===== 博客园 (cnblogs.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_cnblogs.py"
echo.
echo ===== CNode (cnodejs.org) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_cnodejs.py"
echo.
echo ===== 腾讯 WorkBuddy (codebuddy.cn) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_codebuddy.py"
echo.
echo ===== Connected Papers (connectedpapers.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_connectedpapers.py"
echo.
echo ===== Coursera (coursera.org) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_coursera.py"
echo.
echo ===== CSDN (csdn.net) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_csdn.py"
echo.
echo ===== Datawhale 开源学习社区 (datawhale.cn) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_datawhale.py"
echo.
echo ===== Dev.to (dev.to) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_devto.py"
echo.
echo ===== edX (edx.org) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_edx.py"
echo.
echo ===== Flaticon (flaticon.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_flaticon.py"
echo.
echo ===== 极客时间 (time.geekbang.org) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_geekbang.py"
echo.
echo ===== Gitee 码云 (gitee.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_gitee.py"
echo.
echo ===== GitHub (github.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_github.py"
echo.
echo ===== Google Docs (docs.google.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_googledocs.py"
echo.
echo ===== Hacker News (news.ycombinator.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_hackernews.py"
echo.
echo ===== HackerNoon (hackernoon.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_hackernoon.py"
echo.
echo ===== Hugging Face (huggingface.co) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_huggingface.py"
echo.
echo ===== 虎嗅 (huxiu.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_huxiu.py"
echo.
echo ===== Iconfont 阿里巴巴图标库 (iconfont.cn) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_iconfont.py"
echo.
echo ===== 中国大学MOOC (icourse163.org) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_icourse163.py"
echo.
echo ===== 中国大学MOOC (icourse163.org) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_icourse163_org.py"
echo.
echo ===== 慕课网 (imooc.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_imooc.py"
echo.
echo ===== InfoQ 中文 (infoq.cn) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_infoq.py"
echo.
echo ===== 极客学院 (jikexueyuan.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_jikexueyuan.py"
echo.
echo ===== 机器之心 (jiqizhixin.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_jiqizhixin.py"
echo.
echo ===== 掘金 (juejin.cn) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_juejin.py"
echo.
echo ===== Kaggle (kaggle.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_kaggle.py"
echo.
echo ===== 看雪论坛 (bbs.kanxue.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_kanxue.py"
echo.
echo ===== Khan Academy 可汗学院 (khanacademy.org) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_khanacademy.py"
echo.
echo ===== LeetCode 力扣 (leetcode.cn) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_leetcode.py"
echo.
echo ===== LiblibAI (liblib.art) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_liblib.py"
echo.
echo ===== LMSYS Chatbot Arena (lmarena.ai) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_lmarena.py"
echo.
echo ===== Lobsters (lobste.rs) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_lobsters.py"
echo.
echo ===== Medium (medium.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_medium.py"
echo.
echo ===== ModelScope 魔搭 (modelscope.cn) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_modelscope.py"
echo.
echo ===== Kimi 月之暗面 (moonshot.cn) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_moonshot.py"
echo.
echo ===== The Noun Project (thenounproject.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_nounproject.py"
echo.
echo ===== OpenRouter (openrouter.ai) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_openrouter.py"
echo.
echo ===== 开源中国 (oschina.net) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_oschina.py"
echo.
echo ===== Overleaf (overleaf.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_overleaf.py"
echo.
echo ===== 量子位 (qbitai.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_qbitai.py"
echo.
echo ===== Qoder 通义灵码 (qoder.com.cn) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_qoder.py"
echo.
echo ===== Roboflow Universe (universe.roboflow.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_roboflow.py"
echo.
echo ===== 思否 SegmentFault (segmentfault.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_segmentfault.py"
echo.
echo ===== Semantic Scholar (semanticscholar.org) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_semanticscholar.py"
echo.
echo ===== SoundCloud (soundcloud.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_soundcloud.py"
echo.
echo ===== 少数派 (sspai.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_sspai.py"
echo.
echo ===== Stack Overflow (stackoverflow.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_stackoverflow.py"
echo.
echo ===== 网易云课堂 (study.163.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_study163.py"
echo.
echo ===== 阿里云天池 (tianchi.aliyun.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_tianchi.py"
echo.
echo ===== 钛媒体 (tmtpost.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_tmtpost.py"
echo.
echo ===== 通义千问 (tongyi.aliyun.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_tongyi.py"
echo.
echo ===== TryHackMe (tryhackme.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_tryhackme.py"
echo.
echo ===== V2EX (v2ex.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_v2ex.py"
echo.
echo ===== Weights & Biases (wandb.ai) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_wandb.py"
echo.
echo ===== 微信公众号 (mp.weixin.qq.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_wechat.py"
echo.
echo ===== 小红书 (xiaohongshu.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_xiaohongshu.py"
echo.
echo ===== 学堂在线 (xuetangx.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_xuetangx.py"
echo.
echo ===== YouTube (youtube.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_youtube.py"
echo.
echo ===== 知乎 (zhihu.com) Cookie 获取脚本 =====
"%CRAWL4AI_PY%" "%~dp0get_zhihu.py"
echo.
echo 全部导出完成！
echo 抖音 Cookie 请单独运行 get_douyin.bat 扫码登录
echo 建议先运行「启动Edge调试模式.bat」并保持 Edge 打开，导出更完整
pause