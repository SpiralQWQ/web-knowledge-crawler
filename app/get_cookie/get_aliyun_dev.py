"""阿里云开发者社区 (developer.aliyun.com) Cookie 获取脚本

需要登录态的原因：社区文章/问答/训练营需登录；未登录部分内容被折叠或限流。

用法:
  python app/get_cookie/get_aliyun_dev.py
  python app/get_cookie/get_aliyun_dev.py --browser chrome
  python app/get_cookie/get_aliyun_dev.py --profile "Profile 1"

前置: 已用浏览器登录 developer.aliyun.com 并关闭浏览器
输出: data/cookies/aliyun_dev.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("aliyun_dev", ["developer.aliyun.com", "help.aliyun.com"]))
