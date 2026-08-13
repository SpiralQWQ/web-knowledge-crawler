"""CNode (cnodejs.org) Cookie 获取脚本

需要登录态的原因：回复/收藏/创建话题需登录；未登录只能读公开话题与回复。

用法:
  python tools/get_cookie/get_cnodejs.py
  python tools/get_cookie/get_cnodejs.py --browser chrome
  python tools/get_cookie/get_cnodejs.py --profile "Profile 1"

前置: 已用浏览器登录 cnodejs.org 并关闭浏览器
输出: data/cookies/cnodejs.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("cnodejs", ["cnodejs.org", "www.cnodejs.org"]))
