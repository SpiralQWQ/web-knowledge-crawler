"""Datawhale 开源学习社区 (datawhale.cn) Cookie 获取脚本

需要登录态的原因：社区发帖/评论/参与学习小组需登录；未登录只能看公开内容。

用法:
  python app/get_cookie/get_datawhale.py
  python app/get_cookie/get_datawhale.py --browser chrome
  python app/get_cookie/get_datawhale.py --profile "Profile 1"

前置: 在调试 Edge 里登录 datawhale.cn 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/datawhale.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("datawhale", ["datawhale.cn", "www.datawhale.cn"]))
