"""Weights & Biases (wandb.ai) Cookie 获取脚本

需要登录态的原因：实验追踪/可视化面板/团队空间需登录；未登录只能看公开报告。

用法:
  python tools/get_cookie/get_wandb.py
  python tools/get_cookie/get_wandb.py --browser chrome
  python tools/get_cookie/get_wandb.py --profile "Profile 1"

前置: 在调试 Edge 里登录 wandb.ai 并保持打开（或浏览器已登录后关闭）
输出: data/cookies/wandb.txt
"""
import sys

from _base import export_site

if __name__ == "__main__":
    sys.exit(export_site("wandb", ["wandb.ai", "www.wandb.ai"]))
