"""AI Alignment Forum (alignmentforum.org) Cookie 获取脚本

需要登录态的原因：阅读全文/评论/收藏需登录；未登录只能看标题与摘要。

用法:
  python tools/get_cookie/get_alignmentforum.py
  python tools/get_cookie/get_alignmentforum.py --browser chrome
  python tools/get_cookie/get_alignmentforum.py --profile "Profile 1"

前置: 在调试 Edge 里登录 alignmentforum.org 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/alignmentforum.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("alignmentforum", ["alignmentforum.org", "www.alignmentforum.org"]))
