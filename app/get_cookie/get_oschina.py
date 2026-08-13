"""开源中国 (oschina.net) Cookie 获取脚本

需要登录态的原因：翻译/收藏/关注、部分资讯与问答需登录；未登录采集会被反爬限流。

用法:
  python app/get_cookie/get_oschina.py
  python app/get_cookie/get_oschina.py --browser chrome
  python app/get_cookie/get_oschina.py --profile "Profile 1"

前置: 已用浏览器登录 oschina.net 并关闭浏览器
输出: data/cookies/oschina.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("oschina", ["oschina.net", "www.oschina.net", "my.oschina.net"]))
