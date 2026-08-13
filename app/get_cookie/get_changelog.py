"""The Changelog (changelog.com) Cookie 获取脚本

需要登录态的原因：订阅/收藏/评论播客需登录；未登录只能试听片段。

用法:
  python app/get_cookie/get_changelog.py
  python app/get_cookie/get_changelog.py --browser chrome
  python app/get_cookie/get_changelog.py --profile "Profile 1"

前置: 在调试 Edge 里登录 changelog.com 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/changelog.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("changelog", ["changelog.com", "www.changelog.com"]))
