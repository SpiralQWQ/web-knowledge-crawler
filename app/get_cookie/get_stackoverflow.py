"""Stack Overflow (stackoverflow.com) Cookie 获取脚本

需要登录态的原因：收藏/投票/评论需登录；未登录采集会被反爬限流（403/验证）。

用法:
  python tools/get_cookie/get_stackoverflow.py
  python tools/get_cookie/get_stackoverflow.py --browser chrome
  python tools/get_cookie/get_stackoverflow.py --profile "Profile 1"

前置: 已用浏览器登录 stackoverflow.com 并关闭浏览器（需能访问）
输出: data/cookies/stackoverflow.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("stackoverflow", ["stackoverflow.com", "www.stackoverflow.com"]))
