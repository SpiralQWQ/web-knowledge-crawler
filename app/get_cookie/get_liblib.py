"""LiblibAI (liblib.art) Cookie 获取脚本

需要登录态的原因：下载模型/收藏/训练需登录；未登录部分模型不可下载。

用法:
  python app/get_cookie/get_liblib.py
  python app/get_cookie/get_liblib.py --browser chrome
  python app/get_cookie/get_liblib.py --profile "Profile 1"

前置: 已用浏览器登录 liblib.art 并关闭浏览器
输出: data/cookies/liblib.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("liblib", ["liblib.art", "www.liblib.art"]))
