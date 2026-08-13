"""Flaticon (flaticon.com) Cookie 获取脚本

需要登录态的原因：图标下载需登录（免费账号），未登录不能下载 PNG/SVG。

用法:
  python app/get_cookie/get_flaticon.py
  python app/get_cookie/get_flaticon.py --browser chrome
  python app/get_cookie/get_flaticon.py --profile "Profile 1"

前置: 在调试 Edge 里登录 flaticon.com 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/flaticon.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("flaticon", ["flaticon.com", "www.flaticon.com"]))
