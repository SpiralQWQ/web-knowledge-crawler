"""ModelScope 魔搭 (modelscope.cn) Cookie 获取脚本

需要登录态的原因：下载需登录的模型/数据集、收藏、个人空间；未登录部分资源受限。

用法:
  python tools/get_cookie/get_modelscope.py
  python tools/get_cookie/get_modelscope.py --browser chrome
  python tools/get_cookie/get_modelscope.py --profile "Profile 1"

前置: 已用浏览器登录 modelscope.cn 并关闭浏览器
输出: data/cookies/modelscope.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("modelscope", ["modelscope.cn", "www.modelscope.cn"]))
