"""博客园 (cnblogs.com) Cookie 获取脚本

需要登录态的原因：评论/点赞/收藏、园子与闪存需登录；未登录采集会触发反爬验证。

用法:
  python tools/get_cookie/get_cnblogs.py
  python tools/get_cookie/get_cnblogs.py --browser chrome
  python tools/get_cookie/get_cnblogs.py --profile "Profile 1"

前置: 已用浏览器登录 cnblogs.com 并关闭浏览器
输出: data/cookies/cnblogs.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("cnblogs", ["cnblogs.com", "www.cnblogs.com"]))
