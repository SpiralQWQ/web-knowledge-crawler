"""Iconfont 阿里巴巴图标库 (iconfont.cn) Cookie 获取脚本

需要登录态的原因：下载图标/创建项目/管理图标库需登录；未登录只能浏览预览。

用法:
  python tools/get_cookie/get_iconfont.py
  python tools/get_cookie/get_iconfont.py --browser chrome
  python tools/get_cookie/get_iconfont.py --profile "Profile 1"

前置: 已用浏览器登录 iconfont.cn 并关闭浏览器
输出: data/cookies/iconfont.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("iconfont", ["iconfont.cn", "www.iconfont.cn"]))
