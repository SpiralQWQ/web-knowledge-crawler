"""Hugging Face (huggingface.co) Cookie 获取脚本

需要登录态的原因：下载需登录的模型/数据集（gated）、收藏、个人空间；
未登录 gated 资源会被 401。浏览器登录一次 → 导出 Cookie → 采集复用。

用法:
  python tools/get_cookie/get_huggingface.py
  python tools/get_cookie/get_huggingface.py --browser chrome
  python tools/get_cookie/get_huggingface.py --profile "Profile 1"

前置: 已用浏览器登录 huggingface.co 并关闭浏览器（需能访问）
输出: data/cookies/huggingface.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("huggingface", ["huggingface.co", "www.huggingface.co"]))
