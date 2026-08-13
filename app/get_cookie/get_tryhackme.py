"""TryHackMe (tryhackme.com) Cookie 获取脚本

需要登录态的原因：安全靶场房间/攻防练习需登录；未登录只能看房间介绍。

用法:
  python app/get_cookie/get_tryhackme.py
  python app/get_cookie/get_tryhackme.py --browser chrome
  python app/get_cookie/get_tryhackme.py --profile "Profile 1"

前置: 在调试 Edge 里登录 tryhackme.com 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/tryhackme.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("tryhackme", ["tryhackme.com", "www.tryhackme.com"]))
