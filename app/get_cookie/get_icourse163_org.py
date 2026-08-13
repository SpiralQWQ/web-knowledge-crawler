"""中国大学MOOC (icourse163.org) Cookie 获取脚本

需要登录态的原因：课程学习/视频播放/测验/讨论区需登录；未登录只能看课程介绍页。
（.org 与 .com 域名并存，两个都要覆盖）

用法:
  python app/get_cookie/get_icourse163_org.py
  python app/get_cookie/get_icourse163_org.py --browser chrome
  python app/get_cookie/get_icourse163_org.py --profile "Profile 1"

前置: 在调试 Edge 里登录 icourse163.org 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/icourse163_org.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("icourse163_org", ["icourse163.org", "www.icourse163.org"]))
