"""看雪论坛 (bbs.kanxue.com) Cookie 获取脚本

需要登录态的原因：帖子正文完整显示（部分资源帖需回复可见）、下载附件需登录；
未登录采集被限流。浏览器登录一次 → 导出 Cookie → 采集复用。

用法:
  python tools/get_cookie/get_kanxue.py
  python tools/get_cookie/get_kanxue.py --browser chrome
  python tools/get_cookie/get_kanxue.py --profile "Profile 1"

前置: 已用浏览器登录 bbs.kanxue.com 并关闭浏览器
输出: data/cookies/kanxue.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("kanxue", ["bbs.kanxue.com", "www.bbs.kanxue.com", "kanxue.com"]))
