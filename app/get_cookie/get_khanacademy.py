"""Khan Academy 可汗学院 (khanacademy.org) Cookie 获取脚本

需要登录态的原因：保存学习进度/练习记录需登录；未登录也能看视频但无进度记录。

用法:
  python app/get_cookie/get_khanacademy.py
  python app/get_cookie/get_khanacademy.py --browser chrome
  python app/get_cookie/get_khanacademy.py --profile "Profile 1"

前置: 在调试 Edge 里登录 khanacademy.org 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/khanacademy.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("khanacademy", ["khanacademy.org", "www.khanacademy.org"]))
