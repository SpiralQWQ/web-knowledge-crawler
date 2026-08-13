"""飞桨 AI Studio (aistudio.baidu.com) Cookie 获取脚本

需要登录态的原因：数据集下载、项目 fork/运行、算力资源需登录；未登录只能看公开页。

用法:
  python tools/get_cookie/get_aistudio.py
  python tools/get_cookie/get_aistudio.py --browser chrome
  python tools/get_cookie/get_aistudio.py --profile "Profile 1"

前置: 在调试 Edge 里登录 aistudio.baidu.com 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/aistudio.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("aistudio", ["aistudio.baidu.com"]))
