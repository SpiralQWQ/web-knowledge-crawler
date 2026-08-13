"""思否 SegmentFault (segmentfault.com) Cookie 获取脚本

需要登录态的原因：关注/收藏/点赞需登录；未登录采集会被反爬限流。

用法:
  python tools/get_cookie/get_segmentfault.py
  python tools/get_cookie/get_segmentfault.py --browser chrome
  python tools/get_cookie/get_segmentfault.py --profile "Profile 1"

前置: 已用浏览器登录 segmentfault.com 并关闭浏览器
输出: data/cookies/segmentfault.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("segmentfault", ["segmentfault.com", "www.segmentfault.com"]))
