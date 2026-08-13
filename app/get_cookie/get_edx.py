"""edX (edx.org) Cookie 获取脚本

需要登录态的原因：课程学习/作业/证书、下载课件需登录；未登录只能看课程介绍页。

用法:
  python app/get_cookie/get_edx.py
  python app/get_cookie/get_edx.py --browser chrome
  python app/get_cookie/get_edx.py --profile "Profile 1"

前置: 在调试 Edge 里登录 edx.org 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/edx.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("edx", ["edx.org", "www.edx.org"]))
