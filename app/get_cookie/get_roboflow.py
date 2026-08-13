"""Roboflow Universe (universe.roboflow.com) Cookie 获取脚本

需要登录态的原因：数据集下载/版本导出/训练需登录；未登录只能看数据集预览。

用法:
  python tools/get_cookie/get_roboflow.py
  python tools/get_cookie/get_roboflow.py --browser chrome
  python tools/get_cookie/get_roboflow.py --profile "Profile 1"

前置: 在调试 Edge 里登录 universe.roboflow.com 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/roboflow.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("roboflow", ["universe.roboflow.com", "roboflow.com"]))
