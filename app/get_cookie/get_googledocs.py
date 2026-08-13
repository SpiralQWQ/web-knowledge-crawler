"""Google Docs (docs.google.com) Cookie 获取脚本

需要登录态的原因：私有文档/共享文档的编辑与下载需 Google 账号登录态；
未登录只能访问公开文档。浏览器登录一次 → 导出 Cookie → 采集复用。

用法:
  python app/get_cookie/get_googledocs.py
  python app/get_cookie/get_googledocs.py --browser chrome
  python app/get_cookie/get_googledocs.py --profile "Profile 1"

前置: 已用浏览器登录 docs.google.com（需能访问 Google）并关闭浏览器
输出: data/cookies/googledocs.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("googledocs", ["docs.google.com", "google.com", "accounts.google.com"]))
