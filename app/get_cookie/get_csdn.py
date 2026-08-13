"""CSDN (csdn.net) Cookie 获取脚本

需要登录态的原因：部分博客正文需登录查看完整内容（含代码块折叠）、下载需登录；
未登录采集会被反爬限流。浏览器登录一次 → 导出 Cookie → 采集复用。

用法:
  python tools/get_cookie/get_csdn.py
  python tools/get_cookie/get_csdn.py --browser chrome
  python tools/get_cookie/get_csdn.py --profile "Profile 1"

前置: 已用浏览器登录 csdn.net 并关闭浏览器
输出: data/cookies/csdn.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("csdn", ["csdn.net", "www.csdn.net", "blog.csdn.net"]))
