"""51CTO (51cto.com) + AI前线 (ai.51cto.com) Cookie 获取脚本

需要登录态的原因：文章全文、视频课程、评论需登录；未登录采集被限流。

用法:
  python app/get_cookie/get_51cto.py
  python app/get_cookie/get_51cto.py --browser chrome
  python app/get_cookie/get_51cto.py --profile "Profile 1"

前置: 已用浏览器登录 51cto.com 并关闭浏览器
输出: data/cookies/51cto.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("51cto", ["51cto.com", "www.51cto.com", "ai.51cto.com"]))
