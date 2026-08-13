"""小红书 (xiaohongshu.com) Cookie 获取脚本

需要登录态的原因：小红书反爬极强，未登录匿名 IP 高频触发滑块/风控；登录态 +
Cookie 才能稳定抓取笔记正文/图片/评论。浏览器登录一次 → 导出 Cookie → 采集复用。

用法:
  python tools/get_cookie/get_xiaohongshu.py
  python tools/get_cookie/get_xiaohongshu.py --browser chrome
  python tools/get_cookie/get_xiaohongshu.py --profile "Profile 1"

前置: 已用浏览器登录 xiaohongshu.com 并关闭浏览器
输出: data/cookies/xiaohongshu.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("xiaohongshu", ["xiaohongshu.com", "www.xiaohongshu.com", "xhslink.com"]))
