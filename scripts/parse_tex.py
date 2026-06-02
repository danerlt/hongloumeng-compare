# -*- coding: utf-8 -*-
"""解析 lingr7 .tex -> 纯文本(正文 + 【脂批】)。"""
import re, json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
def _remove_balanced(s, cmd):
    """删除 \\cmd{...}，花括号配平。"""
    out = []; i = 0; n = len(s); tok = '\\' + cmd
    while i < n:
        if s.startswith(tok, i) and i+len(tok) < n and s[i+len(tok)] == '{':
            j = i + len(tok) + 1; depth = 1
            while j < n and depth > 0:
                if s[j] == '{': depth += 1
                elif s[j] == '}': depth -= 1
                j += 1
            i = j
        else:
            out.append(s[i]); i += 1
    return ''.join(out)
def get_title(tex):
    k = tex.find('\\chapter{')
    if k < 0: return ''
    i = k + len('\\chapter{'); depth = 1; buf = []
    while i < len(tex) and depth > 0:
        c = tex[i]
        if c == '{': depth += 1
        elif c == '}': depth -= 1
        if depth > 0: buf.append(c)
        i += 1
    t = ''.join(buf)
    t = re.sub(r'\\hspace\{[^}]*\}', '　', t)
    t = re.sub(r'\\[a-zA-Z]+\s*', '', t)
    t = t.replace('{', '').replace('}', '').replace('*', '')
    return t.strip()
def preprocess(tex):
    s = tex
    s = re.sub(r'(?m)^%.*$', '', s)                             # 注释行
    s = _remove_balanced(s, 'footnote')                         # 校勘脚注
    s = _remove_balanced(s, 'chapter')                          # 章标题(另取)
    s = re.sub(r'\\includegraphics(\[[^\]]*\])?\{[^}]*\}', '', s)
    s = re.sub(r'\\hspace\{[^}]*\}', '', s)
    s = re.sub(r'\{\([^(){}]*\)\}', '', s)                      # {(底本误字)}
    s = s.replace('{[}', '').replace('{]}', '')                 # 校改字括号去壳
    s = re.sub(r'\{?\$\\diamond\$\}?', '　', s)                 # 批语分隔符
    s = s.replace('\\ldots{}', '……').replace('\\ldots', '……')
    s = s.replace('~', '').replace('\\,', '')
    return s
def split_pi(grp):
    """一个 \\kaishu 组里可能有多条批，按 \\kaishu 切。"""
    parts = re.split(r'\\kaishu', grp)
    res = []
    for p in parts[1:]:
        t = re.sub(r'\\[a-zA-Z]+', '', p)
        t = t.replace('{', '').replace('}', '')
        t = t.strip().strip('　').strip()
        if t: res.append(t)
    return res
def parse(s):
    """递归解析：depth=0 的 {...} 含 \\kaishu 即批语；其余字符为正文。"""
    out = []; i = 0; n = len(s); buf = []
    def flush():
        if buf:
            out.append(('zw', ''.join(buf))); buf.clear()
    while i < n:
        c = s[i]
        if c == '\\':
            m = re.match(r'\\([a-zA-Z]+)', s[i:])
            if m:
                i += m.end()
                while i < n and s[i] == ' ': i += 1
                continue
            i += 1; continue
        if c == '{':
            depth = 1; j = i+1
            while j < n and depth > 0:
                if s[j] == '{': depth += 1
                elif s[j] == '}': depth -= 1
                j += 1
            grp = s[i+1:j-1]; i = j
            if 'kaishu' in grp:
                if '开卷第一回也' in grp:
                    flush(); out.extend(parse(grp))     # 楔子归正文
                else:
                    flush()
                    for b in split_pi(grp):
                        out.append(('annot', b))
            else:
                flush(); out.extend(parse(grp))
            continue
        if c == '}':
            i += 1; continue
        buf.append(c); i += 1
    flush()
    return out
def tex_to_text(tex):
    title = get_title(tex)
    s = preprocess(tex)
    segs = parse(s)
    parts = []
    for kind, t in segs:
        if kind == 'annot':
            t = t.strip()
            if t: parts.append('【' + t + '】')
        else:
            parts.append(t)
    raw = ''.join(parts)
    raw = re.sub(r'[ \t　]*\n[ \t　]*', '\n', raw)
    raw = re.sub(r'\n{2,}', '\n', raw)
    raw = re.sub(r'[ \t]+', '', raw)
    return title, raw.strip()
def main():
    src = os.path.join(ROOT, 'data', 'zhi')
    dst = os.path.join(ROOT, 'data', 'processed', 'zhi')
    os.makedirs(dst, exist_ok=True)
    titles = {}
    for n in range(1, 81):
        path = os.path.join(src, 'chapter%02d.tex' % n)
        if not os.path.exists(path):
            print('缺失:', path); continue
        tex = open(path, encoding='utf-8').read()
        title, raw = tex_to_text(tex)
        titles[n] = title
        open(os.path.join(dst, 'zhi_ch%d.txt' % n), 'w', encoding='utf-8').write(raw)
        resid = len(re.findall(r'\\[a-zA-Z]+', raw)) + raw.count('{') + raw.count('}')
        print('第%d回 %s | 字%d 批%d 残留%d' % (n, title[:30], len(raw), raw.count('【'), resid))
    json.dump(titles,
              open(os.path.join(ROOT, 'data', 'processed', 'zhi_titles.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    print('完成 80 回脂本解析。')
if __name__ == '__main__':
    main()
