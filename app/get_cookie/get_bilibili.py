"""B站 (bilibili.com) Cookie 获取脚本

需要登录态的原因：高清(1080P+)视频、收藏/关注列表、部分 UP 主内容需登录；
未登录只能看 480P。浏览器登录一次 → 导出 Cookie → 采集视频/文章复用。

用法:
  python tools/get_cookie/get_bilibili.py
  python tools/get_cookie/get_bilibili.py --browser chrome
  python tools/get_cookie/get_bilibili.py --profile "Profile 1"

前置: 已用浏览器登录 bilibili.com 并关闭浏览器
输出: data/cookies/bilibili.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("bilibili", ["bilibili.com", "www.bilibili.com", "api.bilibili.com"]))
