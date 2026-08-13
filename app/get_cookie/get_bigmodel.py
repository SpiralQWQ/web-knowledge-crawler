"""智谱 GLM 开放平台 (open.bigmodel.cn) Cookie 获取脚本

需要登录态的原因：开放平台控制台、API 密钥管理、模型广场需登录；
未登录无法访问控制台数据。浏览器登录一次 → 导出 Cookie → 采集复用。

用法:
  python app/get_cookie/get_bigmodel.py
  python app/get_cookie/get_bigmodel.py --browser chrome
  python app/get_cookie/get_bigmodel.py --profile "Profile 1"

前置: 已用浏览器登录 open.bigmodel.cn 并关闭浏览器
输出: data/cookies/bigmodel.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("bigmodel", ["open.bigmodel.cn"]))
