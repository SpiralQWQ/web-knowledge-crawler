"""InfoQ 中文 (infoq.cn) Cookie 获取脚本

需要登录态的原因：文章全文、视频回放、收藏需登录；未登录部分内容折叠。

用法:
  python app/get_cookie/get_infoq.py
  python app/get_cookie/get_infoq.py --browser chrome
  python app/get_cookie/get_infoq.py --profile "Profile 1"

前置: 已用浏览器登录 infoq.cn 并关闭浏览器
输出: data/cookies/infoq.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("infoq", ["infoq.cn", "www.infoq.cn"]))
