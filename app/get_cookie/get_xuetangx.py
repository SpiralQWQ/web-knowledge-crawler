"""学堂在线 (xuetangx.com) Cookie 获取脚本

需要登录态的原因：课程学习、视频播放、作业/考试需登录；未登录只能看课程封面与简介。

用法:
  python app/get_cookie/get_xuetangx.py
  python app/get_cookie/get_xuetangx.py --browser chrome
  python app/get_cookie/get_xuetangx.py --profile "Profile 1"

前置: 已用浏览器登录 xuetangx.com 并关闭浏览器
输出: data/cookies/xuetangx.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("xuetangx", ["xuetangx.com", "www.xuetangx.com"]))
