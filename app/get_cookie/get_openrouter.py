"""OpenRouter (openrouter.ai) Cookie 获取脚本

需要登录态的原因：控制台、API 密钥、用量统计需登录；未登录无法访问个人数据。

用法:
  python app/get_cookie/get_openrouter.py
  python app/get_cookie/get_openrouter.py --browser chrome
  python app/get_cookie/get_openrouter.py --profile "Profile 1"

前置: 已用浏览器登录 openrouter.ai 并关闭浏览器（需能访问）
输出: data/cookies/openrouter.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("openrouter", ["openrouter.ai", "www.openrouter.ai"]))
