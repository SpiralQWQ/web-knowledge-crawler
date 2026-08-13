"""掘金 (juejin.cn) Cookie 获取脚本

需要登录态的原因：收藏/点赞/关注列表、部分专栏与稀土掘金会员内容需登录；
登录态采集社区热帖/专栏更完整。浏览器登录一次 → 导出 Cookie → 采集复用。

用法:
  python tools/get_cookie/get_juejin.py
  python tools/get_cookie/get_juejin.py --browser chrome
  python tools/get_cookie/get_juejin.py --profile "Profile 1"

前置: 已用浏览器登录 juejin.cn 并关闭浏览器
输出: data/cookies/juejin.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("juejin", ["juejin.cn", "www.juejin.cn"]))
