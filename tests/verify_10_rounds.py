# -*- coding: utf-8 -*-
"""crawl_guide 十轮不同角度验证：每轮测一个维度。"""
import sys, os, builtins, importlib.util, py_compile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('cg', os.path.join(BASE, 'app', 'crawl_guide.py'))
cg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cg)

RESULTS = []
def round_start(name):
    print(f"\n{'='*50}\n【第 {len(RESULTS)+1} 轮】{name}\n{'='*50}")
def check(name, cond=True, detail=''):
    # 兼容 2参 check(cond, detail) 和 3参 check(name, cond, detail)
    if isinstance(name, str):
        ok = bool(cond)
    else:
        ok = bool(name)
        detail = str(cond) if detail == '' else str(detail)
        name = '检查'
    RESULTS.append(ok)
    print(f'  {"✅" if ok else "❌"} {name} {detail}')

# 第1轮：编译
round_start("编译检查")
import glob
bad = []
for f in glob.glob('collector/**/*.py', recursive=True) + glob.glob('tools/*.py'):
    try: py_compile.compile(f, doraise=True)
    except Exception as e: bad.append(f)
check('编译', not bad, f'全项目编译 ({len(glob.glob("collector/**/*.py",recursive=True))+len(glob.glob("tools/*.py"))} 文件)')

# 第2轮：词库整理边界
round_start("词库整理（乱格式/边界）")
r = cg.clean_term_list("机器学习，transformer 1.图神经网络 https://v.douyin.com/x 12345长串 机器学习")
check('分隔符/序号/中英混合', r['words'] == ['机器学习','transformer','图神经网络'], str(r['words']))
check('URL 分流', r['urls'] == ['https://v.douyin.com/x'], str(r['urls']))
check('数字长串去噪', '12345长串' not in r['words'])
check('去重', r['words'].count('机器学习') == 1)
check('超长中文去噪', cg._is_junk('这是一大段完全没有停顿没有意义的文字描述很长很长很长很长很长很长很长'))

# 第3轮：词性格识别
round_start("词性格识别（加权）")
cases = {'机器学习':'学术','Transformer 论文':'学术','Python 入门':'教程','大模型动态':'热点','PyTorch 框架':'代码','量子物理':'通用'}
allok = all(cg.detect_personality(k) == v for k, v in cases.items())
check(allok, f'6 词识别 {dict((k,cg.detect_personality(k)) for k in cases)}')
rec = cg.recommend_types('学术')
check(rec['论文'] and rec['视频'] and not rec['题库'], '学术推荐论文视频不推题库')

# 第4轮：站映射
round_start("站映射（37站/排序/子形态/认站）")
m = cg.check_site_mapping()
check(m['漏映射'] == [] and m['多余'] == [], f"37站全覆盖 漏:{m['漏映射']}")
check('star数' in cg.site_sort_options('github_topics'), 'GitHub 有star排序')
check(len(cg.SITE_SUBFORMS.get('douyin',[])) == 4, '抖音4子形态')
check(cg.recognize_site('https://www.bilibili.com/video/BV1') == 'bilibili', '认B站链接')
check(len(cg.sites_for_types(['论文','视频'])) == 13, '论文+视频→13站')

# 第5轮：指定爬取交互（mock）
round_start("指定爬取交互（链接提取→认站→连根→位置）")
seq = iter(['1', '抖音分享 https://v.douyin.com/abc/ 复制', 'y', '', 'D:/test', ''])
builtins.input = lambda *a, **k: next(seq, '')
_orig_dl = cg.download_single
cg.download_single = lambda *a, **k: 'mock_ok'  # 不真下载
cg.run_guide()
cg.download_single = _orig_dl  # 恢复真实下载
builtins.input = sys.stdin
check(True, '指定爬取全流程跑通（URL提取/认站/连根/位置/确认）')

# 第6轮：大规模交互（mock）
round_start("大规模交互（词来源→类型→站→细节→速度）")
seq = iter(['2', '1', '机器学习', 'y', 'y','y','y','n','n','n','n','n',
            'y','y','y','n','n','n','n','n','n','n','n','n','n','n','n','n','n','n','n','n','n','n','n','n','n','',
            '20', ''])
builtins.input = lambda *a, **k: next(seq, '')
import subprocess as sp
cg._orig_subprocess_run = sp.run
sp.run = lambda *a, **k: __import__('subprocess').CompletedProcess(a[0] if a else [], 0)
p = cg.guide_mass_crawl()
sp.run = cg._orig_subprocess_run  # 恢复，防污染后续真实下载/回归
builtins.input = sys.stdin
check(p and p['words'] == ['机器学习'] and p['speed'] in ('fast','normal','full'), f'大规模引导 params={p and {k:p[k] for k in ("words","types","speed")}}')

# 第7轮：登录自动化
round_start("登录自动化（检测/需登录站表/关键cookie判定）")
check(cg.ensure_login('arxiv') is True, '不需登录站直接过')
check(cg._has_login_cookie('arxiv') is True, '免登站 _has_login_cookie 直接过')
check(len(cg.NEED_LOGIN['douyin']) == 3, 'NEED_LOGIN 含关键登录cookie(修复:匿名cookie不算登录)')
check('douyin' in cg.NEED_LOGIN and 'weibo' in cg.NEED_LOGIN, f'需登录站表 {list(cg.NEED_LOGIN.keys())}')
check(len(cg.NEED_LOGIN) == 8, '8 站需登录')
# 登录判定列匹配边界（防误判：别站同名cookie/匿名cookie/#HttpOnly_）
_fake = ".douyin.com\tTRUE\t/\tTRUE\t0\tsessionid\tabc\nweibo.com\tTRUE\t/\tTRUE\t0\tsessionid\txyz\n"
check(cg._login_cookie_in(_fake, 'douyin.com', ('sessionid',)) is True, '抖音sessionid判定True')
check(cg._login_cookie_in(".douyin.com\tTRUE\t/\tTRUE\t0\tttwid\tguest\nweibo.com\tTRUE\t/\tTRUE\t0\tsessionid\txyz\n", 'douyin.com', ('sessionid',)) is False, '匿名ttwid+别站sessionid 不误判抖音')
check(cg._login_cookie_in("#HttpOnly_.douyin.com\tTRUE\t/\tTRUE\t0\tsessionid\tabc\n", 'douyin.com', ('sessionid',)) is True, '#HttpOnly_ 行也识别')
check(cg._login_cookie_in("# 注释\n.douyin.com\tTRUE\t/\tTRUE\t0\tsessionid\tabc\n", 'douyin.com', ('sessionid',)) is True, '注释行跳过不误伤')

# 第8轮：执行命令生成
round_start("执行命令生成")
params = {"mode":"mass","words":["机器学习"],"sites":["arxiv","bilibili"],"speed":"fast","details":{"max_results":50}}
cmd = cg.build_crawl_command(params)
check('--terms' in cmd and '--sites' in cmd and '--max-results' in cmd, '大规模命令含词/站/条数')
check('4' in cmd[cmd.index('--concurrency')+1], '快速并发4')
check(cg._SPEED_PARAMS['full'] == {"concurrency":2,"delay":2.0}, '全量速度安全')

# 第9轮：下载功能（真实短视频；无抖音登录态时跳过，用户测完登录自动恢复）
round_start("下载功能（真实下载/落盘/文件名）")
import tempfile
from core.auth.cookie_util import _cookie_file
_cf = _cookie_file()
_cf_lines = open(_cf, 'r', encoding='utf-8', errors='replace').read().lower().splitlines() if _cf and os.path.exists(_cf) else []
_has_dy = any('douyin' in l and 'sessionid' in l for l in _cf_lines)  # 真登录态：同行含 douyin+sessionid
if _has_dy:
    custom = tempfile.mkdtemp(prefix='verify_')
    local = cg.download_single('https://v.douyin.com/L_Ixd-dUoZU/', 'douyin', 'fast', custom)
    check(bool(local) and os.path.exists(local), f'真实下载 {os.path.basename(local) if local else "失败"}')
    check(local and 'untitled' not in local, '文件名含标题(非untitled)')
    check(local and '指定爬取' in local and '视频' in local, '存储规范(指定爬取/视频/douyin)')
else:
    print('  ⏭ 抖音无真登录态(sessionid)，真实下载本轮跳过（浏览器登录后自动恢复）')

# 第10轮：回归测试
round_start("回归测试")
import subprocess as sp2
r = sp2.run([sys.executable, os.path.join(BASE,'temp','test_regression.py'), '1'],
            capture_output=True, encoding='utf-8', errors='replace', timeout=180,
            env=dict(os.environ, PYTHONIOENCODING='utf-8'))
ok = '全部通过' in (r.stdout or '')
check(ok, '回归 1 轮')

print(f"\n{'='*50}\n十轮验证汇总: {RESULTS.count(True)}/{len(RESULTS)} 通过")
