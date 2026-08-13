"""网易云课堂 (study.163.com) Cookie 获取脚本

需要登录态的原因：免费课程进度、试听、部分课程内容需登录；登录态采集课程页更完整。

用法:
  python app/get_cookie/get_study163.py
  python app/get_cookie/get_study163.py --browser chrome
  python app/get_cookie/get_study163.py --profile "Profile 1"

前置: 已用浏览器登录 study.163.com 并关闭浏览器
输出: data/cookies/study163.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("study163", ["study.163.com", "www.study.163.com"]))
