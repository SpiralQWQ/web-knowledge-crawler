"""阿里云天池 (tianchi.aliyun.com) Cookie 获取脚本

需要登录态的原因：竞赛报名、数据集下载、Notebook 需登录；未登录只能看竞赛公告。

用法:
  python tools/get_cookie/get_tianchi.py
  python tools/get_cookie/get_tianchi.py --browser chrome
  python tools/get_cookie/get_tianchi.py --profile "Profile 1"

前置: 在调试 Edge 里登录 tianchi.aliyun.com 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/tianchi.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("tianchi", ["tianchi.aliyun.com"]))
