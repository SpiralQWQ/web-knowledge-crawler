"""Kimi 月之暗面 (moonshot.cn) Cookie 获取脚本

需要登录态的原因：开放平台控制台、API 密钥管理需登录；未登录无法访问控制台数据。

用法:
  python tools/get_cookie/get_moonshot.py
  python tools/get_cookie/get_moonshot.py --browser chrome
  python tools/get_cookie/get_moonshot.py --profile "Profile 1"

前置: 已用浏览器登录 moonshot.cn 并关闭浏览器
输出: data/cookies/moonshot.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("moonshot", ["moonshot.cn", "platform.moonshot.cn"]))
