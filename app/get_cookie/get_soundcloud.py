"""SoundCloud (soundcloud.com) Cookie 获取脚本

需要登录态的原因：完整音频试听/收藏/歌单需登录；未登录部分音轨只给预览。

用法:
  python tools/get_cookie/get_soundcloud.py
  python tools/get_cookie/get_soundcloud.py --browser chrome
  python tools/get_cookie/get_soundcloud.py --profile "Profile 1"

前置: 在调试 Edge 里登录 soundcloud.com 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/soundcloud.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("soundcloud", ["soundcloud.com", "www.soundcloud.com"]))
