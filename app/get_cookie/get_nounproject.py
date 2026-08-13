"""The Noun Project (thenounproject.com) Cookie 获取脚本

需要登录态的原因：图标下载（免费账号每日限额）、收藏需登录；未登录不能下载 PNG。

用法:
  python tools/get_cookie/get_nounproject.py
  python tools/get_cookie/get_nounproject.py --browser chrome
  python tools/get_cookie/get_nounproject.py --profile "Profile 1"

前置: 在调试 Edge 里登录 thenounproject.com 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/nounproject.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("nounproject", ["thenounproject.com", "www.thenounproject.com"]))
