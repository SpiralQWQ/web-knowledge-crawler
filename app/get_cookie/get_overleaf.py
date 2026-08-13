"""Overleaf (overleaf.com) Cookie 获取脚本

需要登录态的原因：LaTeX 项目编辑/保存/编译需登录；未登录不能创建或下载项目。

用法:
  python tools/get_cookie/get_overleaf.py
  python tools/get_cookie/get_overleaf.py --browser chrome
  python tools/get_cookie/get_overleaf.py --profile "Profile 1"

前置: 在调试 Edge 里登录 overleaf.com 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/overleaf.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("overleaf", ["overleaf.com", "www.overleaf.com"]))
