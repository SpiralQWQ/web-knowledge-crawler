"""极客时间 (time.geekbang.org) Cookie 获取脚本

需要登录态的原因：付费专栏/课程内容需登录账号鉴权；未登录只能看文章列表/摘要，
正文与视频课程多为登录态专属。浏览器登录一次 → 导出 Cookie → 采集复用。

用法:
  python app/get_cookie/get_geekbang.py
  python app/get_cookie/get_geekbang.py --browser chrome
  python app/get_cookie/get_geekbang.py --profile "Profile 1"

前置: 已用浏览器登录 time.geekbang.org 并关闭浏览器
输出: data/cookies/geekbang.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("geekbang", ["time.geekbang.org", "geekbang.org"]))
