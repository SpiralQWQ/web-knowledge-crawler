"""V2EX (v2ex.com) Cookie 获取脚本

需要登录态的原因：主题/回复正文完整显示、节点收藏需登录；未登录会被限流。

用法:
  python tools/get_cookie/get_v2ex.py
  python tools/get_cookie/get_v2ex.py --browser chrome
  python tools/get_cookie/get_v2ex.py --profile "Profile 1"

前置: 已用浏览器登录 v2ex.com 并关闭浏览器
输出: data/cookies/v2ex.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("v2ex", ["v2ex.com", "www.v2ex.com"]))
