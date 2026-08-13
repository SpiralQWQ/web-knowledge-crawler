"""虎嗅 (huxiu.com) Cookie 获取脚本

需要登录态的原因：文章全文、收藏、评论需登录；未登录采集被限流或折叠。

用法:
  python app/get_cookie/get_huxiu.py
  python app/get_cookie/get_huxiu.py --browser chrome
  python app/get_cookie/get_huxiu.py --profile "Profile 1"

前置: 已用浏览器登录 huxiu.com 并关闭浏览器
输出: data/cookies/huxiu.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("huxiu", ["huxiu.com", "www.huxiu.com"]))
