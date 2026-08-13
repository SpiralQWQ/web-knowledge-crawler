"""智源社区 (hub.baai.ac.cn) Cookie 获取脚本

需要登录态的原因：社区文章/论文库/数据集下载需登录；未登录部分内容被折叠。

用法:
  python app/get_cookie/get_baai.py
  python app/get_cookie/get_baai.py --browser chrome
  python app/get_cookie/get_baai.py --profile "Profile 1"

前置: 已用浏览器登录 hub.baai.ac.cn 并关闭浏览器
输出: data/cookies/baai.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("baai", ["hub.baai.ac.cn"]))
