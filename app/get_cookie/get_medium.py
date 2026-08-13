"""Medium (medium.com) Cookie 获取脚本

需要登录态的原因：部分文章全文需登录（会员软墙）；登录态可多抓几篇全文。
浏览器登录一次 → 导出 Cookie → 采集复用。

用法:
  python app/get_cookie/get_medium.py
  python app/get_cookie/get_medium.py --browser chrome
  python app/get_cookie/get_medium.py --profile "Profile 1"

前置: 已用浏览器登录 medium.com 并关闭浏览器（需能访问）
输出: data/cookies/medium.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("medium", ["medium.com", "www.medium.com"]))
