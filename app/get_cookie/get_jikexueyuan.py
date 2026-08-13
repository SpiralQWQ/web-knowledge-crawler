"""极客学院 (jikexueyuan.com) Cookie 获取脚本

需要登录态的原因：视频课程播放、学习进度需登录；未登录部分课程内容不可见。

用法:
  python tools/get_cookie/get_jikexueyuan.py
  python tools/get_cookie/get_jikexueyuan.py --browser chrome
  python tools/get_cookie/get_jikexueyuan.py --profile "Profile 1"

前置: 已用浏览器登录 jikexueyuan.com 并关闭浏览器
输出: data/cookies/jikexueyuan.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("jikexueyuan", ["jikexueyuan.com", "www.jikexueyuan.com"]))
