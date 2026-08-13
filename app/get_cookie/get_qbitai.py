"""量子位 (qbitai.com) Cookie 获取脚本

需要登录态的原因：文章全文、评论需登录；未登录采集被限流或折叠。

用法:
  python tools/get_cookie/get_qbitai.py
  python tools/get_cookie/get_qbitai.py --browser chrome
  python tools/get_cookie/get_qbitai.py --profile "Profile 1"

前置: 已用浏览器登录 qbitai.com 并关闭浏览器
输出: data/cookies/qbitai.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("qbitai", ["qbitai.com", "www.qbitai.com"]))
