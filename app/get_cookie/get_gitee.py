"""Gitee 码云 (gitee.com) Cookie 获取脚本

需要登录态的原因：私有仓库/关注/星标、API 访问需登录；未登录采集被限流。

用法:
  python tools/get_cookie/get_gitee.py
  python tools/get_cookie/get_gitee.py --browser chrome
  python tools/get_cookie/get_gitee.py --profile "Profile 1"

前置: 已用浏览器登录 gitee.com 并关闭浏览器
输出: data/cookies/gitee.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("gitee", ["gitee.com", "www.gitee.com"]))
