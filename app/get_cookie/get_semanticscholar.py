"""Semantic Scholar (semanticscholar.org) Cookie 获取脚本

需要登录态的原因：收藏论文/保存列表/个人库需登录；未登录可搜索但无法收藏。

用法:
  python tools/get_cookie/get_semanticscholar.py
  python tools/get_cookie/get_semanticscholar.py --browser chrome
  python tools/get_cookie/get_semanticscholar.py --profile "Profile 1"

前置: 在调试 Edge 里登录 semanticscholar.org 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/semanticscholar.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("semanticscholar", ["semanticscholar.org", "www.semanticscholar.org"]))
