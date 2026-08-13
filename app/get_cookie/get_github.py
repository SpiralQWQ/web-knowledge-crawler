"""GitHub (github.com) Cookie 获取脚本

需要登录态的原因：私有仓库/关注/星标/搜索增强需登录；未登录 API 限流 60 次/时，
匿名采集仓库列表很快被限。浏览器登录一次 → 导出 Cookie → 采集复用。

用法:
  python tools/get_cookie/get_github.py
  python tools/get_cookie/get_github.py --browser chrome
  python tools/get_cookie/get_github.py --profile "Profile 1"

前置: 已用浏览器登录 github.com 并关闭浏览器（需能访问）
输出: data/cookies/github.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("github", ["github.com", "www.github.com", "api.github.com"]))
