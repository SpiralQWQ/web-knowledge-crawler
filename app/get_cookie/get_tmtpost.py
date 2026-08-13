"""钛媒体 (tmtpost.com) Cookie 获取脚本

需要登录态的原因：文章全文、收藏、评论需登录；未登录采集被限流或折叠。

用法:
  python tools/get_cookie/get_tmtpost.py
  python tools/get_cookie/get_tmtpost.py --browser chrome
  python tools/get_cookie/get_tmtpost.py --profile "Profile 1"

前置: 已用浏览器登录 tmtpost.com 并关闭浏览器
输出: data/cookies/tmtpost.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("tmtpost", ["tmtpost.com", "www.tmtpost.com"]))
