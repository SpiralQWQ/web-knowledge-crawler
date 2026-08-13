"""Connected Papers (connectedpapers.com) Cookie 获取脚本

需要登录态的原因：保存图谱/构建自己的图需登录；未登录只能临时看图谱。

用法:
  python app/get_cookie/get_connectedpapers.py
  python app/get_cookie/get_connectedpapers.py --browser chrome
  python app/get_cookie/get_connectedpapers.py --profile "Profile 1"

前置: 在调试 Edge 里登录 connectedpapers.com 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/connectedpapers.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("connectedpapers", ["connectedpapers.com", "www.connectedpapers.com"]))
