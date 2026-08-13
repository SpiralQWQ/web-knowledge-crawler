"""LMSYS Chatbot Arena (lmarena.ai) Cookie 获取脚本

需要登录态的原因：登录后投票/参与评测/保存偏好；未登录可匿名看榜单。

用法:
  python tools/get_cookie/get_lmarena.py
  python tools/get_cookie/get_lmarena.py --browser chrome
  python tools/get_cookie/get_lmarena.py --profile "Profile 1"

前置: 在调试 Edge 里登录 lmarena.ai 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/lmarena.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("lmarena", ["lmarena.ai", "www.lmarena.ai"]))
