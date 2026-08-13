"""Dev.to (dev.to) Cookie 获取脚本

需要登录态的原因：点赞/收藏/评论需登录；未登录采集会被限流。

用法:
  python app/get_cookie/get_devto.py
  python app/get_cookie/get_devto.py --browser chrome
  python app/get_cookie/get_devto.py --profile "Profile 1"

前置: 已用浏览器登录 dev.to 并关闭浏览器
输出: data/cookies/devto.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("devto", ["dev.to", "www.dev.to"]))
