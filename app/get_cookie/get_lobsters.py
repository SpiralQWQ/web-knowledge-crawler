"""Lobsters (lobste.rs) Cookie 获取脚本

需要登录态的原因：阅读全文/收藏/评论需登录；未登录只能看标题摘要与列表。

用法:
  python app/get_cookie/get_lobsters.py
  python app/get_cookie/get_lobsters.py --browser chrome
  python app/get_cookie/get_lobsters.py --profile "Profile 1"

前置: 已用浏览器登录 lobste.rs 并关闭浏览器
输出: data/cookies/lobsters.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("lobsters", ["lobste.rs", "www.lobste.rs"]))
