"""腾讯 WorkBuddy (codebuddy.cn) Cookie 获取脚本

需要登录态的原因：桌面工作台网页版文档/登录态需账号；未登录无法访问。

用法:
  python tools/get_cookie/get_codebuddy.py
  python tools/get_cookie/get_codebuddy.py --browser chrome
  python tools/get_cookie/get_codebuddy.py --profile "Profile 1"

前置: 已用浏览器登录 codebuddy.cn 并关闭浏览器
输出: data/cookies/codebuddy.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("codebuddy", ["codebuddy.cn", "www.codebuddy.cn"]))
