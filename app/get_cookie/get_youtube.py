"""YouTube (youtube.com) Cookie 获取脚本

需要登录态的原因：部分视频（会员/年龄限制/地区限制）需登录；登录态还能让
yt-dlp 拉取更高清晰度与完整字幕。浏览器登录一次 → 导出 Cookie → 采集复用。

用法:
  python tools/get_cookie/get_youtube.py
  python tools/get_cookie/get_youtube.py --browser chrome
  python tools/get_cookie/get_youtube.py --profile "Profile 1"

前置: 已用浏览器登录 youtube.com 并关闭浏览器（国内需先配好代理登录）
输出: data/cookies/youtube.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("youtube", ["youtube.com", "www.youtube.com", "m.youtube.com"]))
