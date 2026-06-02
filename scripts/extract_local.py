# -*- coding: utf-8 -*-
"""切 程高(cgb.md) 与 癸酉(docx) 各 1–80 回 -> data/processed/{cg,gy}/。"""
import re, os, json, html
from docx import Document
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CN = {'零':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,'百':100}
def cn2num(s):
    s = s.strip()
    if s.isdigit(): return int(s)
    val = 0; section = 0
    for ch in s:
        if ch == '零': continue
        d = CN.get(ch)
        if d is None: return None
        if d in (10, 100):
            section = (section or 1) * d; val += section; section = 0
        else:
            section = d
    val += section
    return val
# === 程高本：cgb.md ===
# 章节标记可能是 "### 第N回" / "### 【第N回】" / "第N章" / 等。先用宽松正则一次过。
# 如果你 head 一下发现实际格式不同，调下面这行 RE_HEAD 即可。
RE_HEAD = re.compile(
    r'(?m)^\s*#{0,3}\s*【?\s*第\s*([一二三四五六七八九十百零\d]+)\s*[回章]\s*】?\s*(.*?)\s*$'
)
def extract_chenggao():
    md = open(os.path.join(ROOT, 'data', 'raw', 'chenggao.md'), encoding='utf-8').read()
    matches = list(RE_HEAD.finditer(md))
    dst = os.path.join(ROOT, 'data', 'processed', 'cg')
    os.makedirs(dst, exist_ok=True)
    titles = {}
    for i, m in enumerate(matches):
        n = cn2num(m.group(1))
        if not n or not (1 <= n <= 80): continue
        body_start = m.end()
        body_end = matches[i+1].start() if i+1 < len(matches) else len(md)
        body = md[body_start:body_end]
        # 去 ----、HTML 标签（ch_cgb 正文是 <p>…</p> 包裹）、(本章完)、首尾空行
        body = re.sub(r'(?m)^-{3,}\s*$', '', body)
        body = re.sub(r'<br\s*/?>|</p>|</blockquote>', '\n', body)  # 块级收尾转换行
        body = re.sub(r'<[^>]+>', '', body)                        # 去其余标签
        body = html.unescape(body)
        body = re.sub(r'\(本章完\)|（本章完）', '', body)
        body = re.sub(r'(?m)^\s*$\n', '', body)
        body = body.strip()
        title = (m.group(2) or '').strip()
        titles[n] = '第%d回 %s' % (n, title)
        open(os.path.join(dst, 'cg_ch%d.txt' % n), 'w', encoding='utf-8').write(body)
    out = sorted(int(f.replace('cg_ch','').replace('.txt','')) for f in os.listdir(dst))
    print('程高切出回数:', len(out), '范围:', out[:3], '...', out[-3:])
    if len(out) < 80:
        print('⚠️  程高回数不足 80。请 head -100 data/raw/chenggao.md 查看实际章节标记格式，调整 RE_HEAD。')
    return titles
# === 癸酉本：docx ===
def extract_guiyou():
    doc = Document(os.path.join(ROOT, 'data', 'raw', 'guiyou.docx'))
    ne = [p.text for p in doc.paragraphs if p.text.strip()]
    body = []
    for i, p in enumerate(ne):
        m = re.match(r'^第\s*([一二三四五六七八九十百零]+)\s*回', p)
        # 正文回目无页码（不以 \t数字 结尾）；并过滤一个误判（正文中"第四回中…"开头的句子）
        if m and not re.search(r'\t\s*\d+\s*$', p) and not p.startswith('第四回中'):
            num = cn2num(m.group(1))
            if num: body.append((i, num, p.strip()))
    body.append((len(ne), 999, ''))
    dst = os.path.join(ROOT, 'data', 'processed', 'gy')
    os.makedirs(dst, exist_ok=True)
    titles = {}
    for k in range(len(body)-1):
        i0, n, title = body[k]; i1 = body[k+1][0]
        if not (1 <= n <= 80): continue
        titles[n] = title
        paras = ne[i0+1:i1]
        open(os.path.join(dst, 'gy_ch%d.txt' % n), 'w', encoding='utf-8').write('\n'.join(paras))
    out = sorted(int(f.replace('gy_ch','').replace('.txt','')) for f in os.listdir(dst))
    print('癸酉切出回数:', len(out))
    return titles
def main():
    os.makedirs(os.path.join(ROOT, 'data', 'processed'), exist_ok=True)
    ct = extract_chenggao()
    gt = extract_guiyou()
    json.dump(
        {'cg': {str(k): v for k, v in ct.items()},
         'gy': {str(k): v for k, v in gt.items()}},
        open(os.path.join(ROOT, 'data', 'processed', 'titles_local.json'), 'w', encoding='utf-8'),
        ensure_ascii=False
    )
if __name__ == '__main__':
    main()
