# -*- coding: utf-8 -*-
"""脂本句为行单位；字符级对齐定位侧栏；行内字符高亮。"""
import os, sys, html, difflib
sys.path.insert(0, os.path.dirname(__file__))
import cmp_lib as C
import cmp_sent as S
def _anchor(opcodes, side_n):
    """对每个 side text 原子，标出它对应脂本(base)的哪个 text 序号。
    equal 精确；replace/insert 归到 base 块起点 i1；delete 无侧栏字。"""
    anc = [None]*side_n
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal':
            for off in range(j2-j1):
                anc[j1+off] = i1+off
        elif tag in ('replace', 'insert'):
            for j in range(j1, j2):
                anc[j] = i1
    return anc
def _side_range_for(anc, lo, hi, side_n):
    """锚点落在 [lo, hi) 的侧栏 text 序号区间。"""
    js = [j for j in range(side_n) if anc[j] is not None and lo <= anc[j] < hi]
    if not js:
        return None
    return (js[0], js[-1]+1)
def _pair_classes(base_keys, side_keys):
    """句内字符级 diff，返回侧栏每字的高亮类（equal/replace/insert），
    以及基准每字是否被改/删。"""
    sm = difflib.SequenceMatcher(None, base_keys, side_keys, autojunk=False)
    side_cls = ['equal']*len(side_keys)
    base_diff = [False]*len(base_keys)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'replace':
            for j in range(j1, j2): side_cls[j] = 'replace'
            for i in range(i1, i2): base_diff[i] = True
        elif tag == 'insert':
            for j in range(j1, j2): side_cls[j] = 'insert'
        elif tag == 'delete':
            for i in range(i1, i2): base_diff[i] = True
    return side_cls, base_diff
def _render_side_atoms(atoms, lo_atom, hi_atom, cls_map, pos):
    out, buf = [], []
    cur = {'c': None}
    def flush():
        if buf:
            t = html.escape(''.join(buf)); c = cur['c']
            if c and c != 'equal':
                out.append('<span class="hl-%s">%s</span>' % (c, t))
            else:
                out.append(t)
            buf.clear()
    for ai in range(lo_atom, hi_atom):
        a = atoms[ai]
        if a['t'] == 'annot':
            flush(); cur['c'] = None
            out.append('<span class="annot">%s</span>' % html.escape(a['o']))
        elif a['t'] == 'text':
            c = cls_map.get(pos[ai], 'equal')
            if c != cur['c']:
                flush(); cur['c'] = c
            buf.append(a['o'])
        elif a['t'] == 'nl':
            continue
        else:  # punct 不高亮
            if cur['c'] not in (None, 'equal'):
                flush(); cur['c'] = 'equal'
            buf.append(a['o'])
    flush()
    return ''.join(out)
def _render_base_sent(sent, lo, diff_union):
    """按整句原子渲染基准句（含句末标点、收尾引号）。lo=该句首字的全局 text 序号。"""
    out, buf = [], []
    cur = {'d': False}
    tc = [0]
    def flush():
        if buf:
            t = html.escape(''.join(buf))
            if cur['d']:
                out.append('<u class="base-diff">%s</u>' % t)
            else:
                out.append(t)
            buf.clear()
    for a in sent:
        if a['t'] == 'annot':
            flush(); cur['d'] = False
            out.append('<span class="annot">%s</span>' % html.escape(a['o']))
        elif a['t'] == 'text':
            gi = lo + tc[0]; tc[0] += 1
            d = diff_union.get(gi, False)
            if d != cur['d']:
                flush(); cur['d'] = d
            buf.append(a['o'])
        elif a['t'] == 'nl':
            continue
        else:  # punct 不参与下划线，遇到时先结束当前下划线块
            if cur['d']:
                flush(); cur['d'] = False
            buf.append(a['o'])
    flush()
    return ''.join(out)
def render_chapter(zhi, cg, gy):
    za = C.atomize(zhi); ca = C.atomize(cg); ga = C.atomize(gy)
    bk, bidx = C.text_seq(za); ck, cidx = C.text_seq(ca); gk, gidx = C.text_seq(ga)
    cpos = {al: t for t, al in enumerate(cidx)}
    gpos = {al: t for t, al in enumerate(gidx)}
    cg_anchor = _anchor(C.diff_base_side(bk, ck), len(ck))
    gy_anchor = _anchor(C.diff_base_side(bk, gk), len(gk))
    zs = S.split_sentences(za)
    rows_html = []
    n_same = n_diff = n_cgmiss = n_gymiss = 0
    t = 0
    nsent = len(zs)
    for si, sent in enumerate(zs):
        ntext = sum(1 for a in sent if a['t'] == 'text')
        lo, hi = t, t + ntext
        t = hi
        if ntext == 0:
            # 纯脂批/无正文行：脂批不参与比对，左右留空、不计缺句
            base_html = _render_base_sent(sent, lo, {})
            rows_html.append(
                '<tr class="r-same"><td class="col-cg">&nbsp;</td>'
                '<td class="col-mid">%s</td><td class="col-gy">&nbsp;</td></tr>'
                % (base_html or '&nbsp;'))
            n_same += 1
            continue
        hi_q = hi if si < nsent-1 else len(bk)+1  # 末句把尾随 insert 也并入
        cj = _side_range_for(cg_anchor, lo, hi_q, len(ck))
        gj = _side_range_for(gy_anchor, lo, hi_q, len(gk))
        diff_union = {}
        if cj:
            cg_cls_list, bdc = _pair_classes(bk[lo:hi], ck[cj[0]:cj[1]])
            cg_cls = {cj[0]+k: v for k, v in enumerate(cg_cls_list)}
            for k, v in enumerate(bdc):
                if v: diff_union[lo+k] = True
        else:
            cg_cls = {}
        if gj:
            gy_cls_list, bdg = _pair_classes(bk[lo:hi], gk[gj[0]:gj[1]])
            gy_cls = {gj[0]+k: v for k, v in enumerate(gy_cls_list)}
            for k, v in enumerate(bdg):
                if v: diff_union[lo+k] = True
        else:
            gy_cls = {}
        base_html = _render_base_sent(sent, lo, diff_union)
        def side_html(atoms, idxmap, pos, jr, cls):
            if not jr: return None
            lo_atom = idxmap[jr[0]]
            hi_atom = idxmap[jr[1]] if jr[1] < len(idxmap) else len(atoms)
            return _render_side_atoms(atoms, lo_atom, hi_atom, cls, pos)
        cg_html = side_html(ca, cidx, cpos, cj, cg_cls)
        gy_html = side_html(ga, gidx, gpos, gj, gy_cls)
        any_diff = bool(diff_union) or (cj is None) or (gj is None)
        if cj is None: n_cgmiss += 1
        if gj is None: n_gymiss += 1
        if any_diff: n_diff += 1
        else: n_same += 1
        cls = 'r-diff' if any_diff else 'r-same'
        if cg_html is None:
            cg_td = '<td class="col-cg col-del"><span class="gap">（程高无）</span></td>'
        else:
            cg_td = '<td class="col-cg">%s</td>' % (cg_html or '&nbsp;')
        if gy_html is None:
            gy_td = '<td class="col-gy col-del"><span class="gap">（癸酉无）</span></td>'
        else:
            gy_td = '<td class="col-gy">%s</td>' % (gy_html or '&nbsp;')
        mid_td = '<td class="col-mid">%s</td>' % (base_html or '&nbsp;')
        rows_html.append('<tr class="%s">%s%s%s</tr>' % (cls, cg_td, mid_td, gy_td))
    stats = dict(base_sents=nsent, same=n_same, diff=n_diff,
                 cg_miss=n_cgmiss, gy_miss=n_gymiss)
    return '\n'.join(rows_html), stats
