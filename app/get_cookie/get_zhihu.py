"""知乎 (zhihu.com) Cookie 获取脚本

需要登录态的原因：知乎反爬强，未登录匿名 IP 高频触发验证码（滑块/选字）；
登录态 + Cookie 可稳定抓取回答/文章/专栏全文。浏览器登录一次 → 导出 Cookie → 采集复用。

用法:
  python tools/get_cookie/get_zhihu.py
  python tools/get_cookie/get_zhihu.py --browser chrome
  python tools/get_cookie/get_zhihu.py --profile "Profile 1"

前置: 已用浏览器登录 zhihu.com 并关闭浏览器
输出: data/cookies/zhihu.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("zhihu", ["zhihu.com", "www.zhihu.com", "api.zhihu.com"]))
