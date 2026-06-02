# -*- coding: utf-8 -*-
"""原子化与字符级 diff 的底层模块。
- atomize: 把文本切成 text/punct/annot/nl 原子
- text 原子带归一化 key（OpenCC t2s + NFKC + 少量异体合并），用于 diff 匹配
- 【】〈〉 和半/全角圆括号一律按批注，剥离不进 diff
"""
import re, unicodedata, difflib
from opencc import OpenCC
_cc = OpenCC('t2s')
VARIANT = {
    '著':'着', '嬛':'鬟', '裏':'里', '迴':'回', '廻':'回', '麽':'么',
    '甦':'苏', '姊':'姐', '飡':'餐', '湌':'餐',
}
PUNCT = set('，。！？：；、""''（）()《》〈〉「」『』…—·,.!?:;~""''〝〞﹏．　 \t')
def _norm_char(ch):
    ch = _cc.convert(ch)
    ch = unicodedata.normalize('NFKC', ch)
    ch = VARIANT.get(ch, ch)
    return ch
# 批注：【】 〈〉 全角（） 半角() —— 古本圆括号均后人所加
_RE_ANNOT = re.compile(r'【[^】]*】|〈[^〉]*〉|（[^）]*）|\([^)]*\)')
_RE_FN = re.compile(r'\[\d+\]')
_RE_DROP = re.compile(r'\(本章完\)|（本章完）')
def atomize(text):
    text = _RE_DROP.sub('', text)
    atoms = []
    i, n = 0, len(text)
    while i < n:
        m = _RE_ANNOT.match(text, i)
        if m:
            atoms.append({'o': m.group(), 't': 'annot'})
            i = m.end()
            continue
        m = _RE_FN.match(text, i)
        if m:
            i = m.end()
            continue
        ch = text[i]
        if ch in ('\n', '\r'):
            atoms.append({'o': '\n', 't': 'nl'})
            i += 1
            continue
        if ch.isspace() or ch == '　':
            i += 1
            continue
        if ch in PUNCT:
            atoms.append({'o': ch, 't': 'punct'})
            i += 1
            continue
        atoms.append({'o': ch, 't': 'text', 'k': _norm_char(ch)})
        i += 1
    return atoms
def text_seq(atoms):
    keys, idx = [], []
    for j, a in enumerate(atoms):
        if a['t'] == 'text':
            keys.append(a['k'])
            idx.append(j)
    return keys, idx
def diff_base_side(base_keys, side_keys):
    return difflib.SequenceMatcher(a=base_keys, b=side_keys, autojunk=False).get_opcodes()
