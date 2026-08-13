"""中国大学MOOC (icourse163.org) Cookie 获取脚本

需要登录态的原因：课程学习、视频播放、测验/讨论区需登录；未登录只能看课程介绍页。

用法:
  python tools/get_cookie/get_icourse163.py
  python tools/get_cookie/get_icourse163.py --browser chrome
  python tools/get_cookie/get_icourse163.py --profile "Profile 1"

前置: 已用浏览器登录 icourse163.org 并关闭浏览器
输出: data/cookies/icourse163.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("icourse163", ["icourse163.org", "www.icourse163.org", "icourse163.com", "www.icourse163.com"]))
