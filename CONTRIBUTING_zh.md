# 为 web-knowledge-crawler 做贡献

感谢你对本项目的兴趣！无论是 bug 报告、新增搜索器、文档改进还是新功能 —— 每份贡献都受欢迎。

## 开发环境搭建

```bash
git clone https://github.com/SpiralQWQ/web-knowledge-crawler
cd web-knowledge-crawler
pip install -r requirements.txt
python setup.py    # 可选：一键配置向导
```

## 代码风格

- **Python 3.10+**，遵循现有代码风格（先读周围代码再动手）
- 函数保持小而聚焦；`core/` 不写业务逻辑
- 新公开函数写 docstring（中文或英文，与所在文件一致）
- 禁止硬编码路径 / 密钥 —— 一律从 `config/` 或环境变量读取
- 新代码放哪里遵循 `docs/目录契约.md`

## 提交 PR 前

1. **跑通测试套件** —— 必须全绿：
   ```bash
   python tests/post_refactor_smoke.py    # 结构冒烟
   python tests/exhaustive_guide_test.py  # 交互穷举
   python tests/task_audit.py             # 任务审计
   python tests/fresh_exhaustive.py       # 全量穷举
   ```
2. **无回归** —— 动了 `core/` 代码，确认既有功能仍正常
3. **更新文档** —— 行为有变化，同步更新 README / CHANGELOG

## 如何贡献

### 报告 bug
- 提 [Issue](https://github.com/SpiralQWQ/web-knowledge-crawler/issues)，附上：
  - 复现步骤
  - 期望 vs 实际行为
  - Python 版本 / 操作系统 / 工具版本
  - 相关日志输出

### 新增搜索器
1. 参照现有搜索器，新建 `core/engines/你的站.py`
2. 用 `@register` 装饰器注册
3. 把站点加进 `core/domain/__init__.py` 的 `SITE_TYPE_MAP`
4. 用真实查询测试；加进冒烟检查

### 提交 PR
1. Fork 仓库，建功能分支：`git checkout -b feat/你的功能`
2. 改代码，跑上面测试
3. 提交信息清晰（如 `feat(engines): 新增 X 站搜索器`）
4. 开 PR 说明改了什么、为什么、测试结果

## 许可

贡献即表示你同意你的贡献按 [AGPL-3.0](LICENSE) 授权。
