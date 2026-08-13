"""Qoder 通义灵码 (qoder.com.cn) Cookie 获取脚本

需要登录态的原因：编码助手文档/控制台需登录；未登录无法访问个人数据。

用法:
  python tools/get_cookie/get_qoder.py
  python tools/get_cookie/get_qoder.py --browser chrome
  python tools/get_cookie/get_qoder.py --profile "Profile 1"

前置: 已用浏览器登录 qoder.com.cn 并关闭浏览器
输出: data/cookies/qoder.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("qoder", ["qoder.com.cn", "www.qoder.com.cn", "docs.qoder.cn"]))
