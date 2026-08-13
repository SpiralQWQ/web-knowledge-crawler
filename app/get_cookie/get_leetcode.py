"""LeetCode 力扣 (leetcode.cn) Cookie 获取脚本

需要登录态的原因：查看完整题目/题解/提交记录需登录；未登录只能看题目摘要。

用法:
  python tools/get_cookie/get_leetcode.py
  python tools/get_cookie/get_leetcode.py --browser chrome
  python tools/get_cookie/get_leetcode.py --profile "Profile 1"

前置: 已用浏览器登录 leetcode.cn 并关闭浏览器
输出: data/cookies/leetcode.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("leetcode", ["leetcode.cn", "www.leetcode.cn"]))
