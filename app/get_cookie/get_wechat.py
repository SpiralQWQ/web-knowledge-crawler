"""微信公众号 (mp.weixin.qq.com) Cookie 获取脚本

需要登录态的原因：公众号文章正文/评论/历史文章需登录态；未登录会被微信风控拦截
（需验证）。浏览器登录一次 → 导出 Cookie → 采集复用。

用法:
  python app/get_cookie/get_wechat.py
  python app/get_cookie/get_wechat.py --browser chrome
  python app/get_cookie/get_wechat.py --profile "Profile 1"

前置: 已用浏览器登录 mp.weixin.qq.com（公众号后台或文章页）并关闭浏览器
输出: data/cookies/wechat.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("wechat", ["mp.weixin.qq.com", "weixin.qq.com"]))
