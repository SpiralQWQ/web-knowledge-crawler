"""HackerNoon (hackernoon.com) Cookie 获取脚本

需要登录态的原因：收藏/点赞/评论需登录；未登录部分文章被截断。

用法:
  python app/get_cookie/get_hackernoon.py
  python app/get_cookie/get_hackernoon.py --browser chrome
  python app/get_cookie/get_hackernoon.py --profile "Profile 1"

前置: 在调试 Edge 里登录 hackernoon.com 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/hackernoon.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("hackernoon", ["hackernoon.com", "www.hackernoon.com"]))
