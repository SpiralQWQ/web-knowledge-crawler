"""Kaggle (kaggle.com) Cookie 获取脚本

需要登录态的原因：下载数据集、运行 Notebook、加入竞赛需登录；未登录只能看列表。
浏览器登录一次 → 导出 Cookie → 采集复用。

用法:
  python tools/get_cookie/get_kaggle.py
  python tools/get_cookie/get_kaggle.py --browser chrome
  python tools/get_cookie/get_kaggle.py --profile "Profile 1"

前置: 已用浏览器登录 kaggle.com 并关闭浏览器（需能访问）
输出: data/cookies/kaggle.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("kaggle", ["kaggle.com", "www.kaggle.com"]))
