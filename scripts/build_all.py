# -*- coding: utf-8 -*-
"""组装单页 HTML：80 回模板懒加载 + 左侧导航 + 三栏对比。"""
import os, sys, json, re, html
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'lib'))
import render_basesent as R
PROC = os.path.join(ROOT, 'data', 'processed')
zhi_titles = json.load(open(os.path.join(PROC, 'zhi_titles.json'), encoding='utf-8'))
loc = json.load(open(os.path.join(PROC, 'titles_local.json'), encoding='utf-8'))
cg_titles = loc['cg']; gy_titles = loc['gy']
def clean_title(t):
    return (t or '').replace('*', '').replace('　　', '　').strip()
def cg_clean(n):
    t = cg_titles.get(str(n), '')
    return re.sub(r'^第\s*[一二三四五六七八九十百零\d]+\s*[回章]\s*', '', t).strip()
def gy_clean(n):
    t = gy_titles.get(str(n), '')
    return re.sub(r'^第\s*[一二三四五六七八九十百零]+\s*回\s*', '', t).strip()
templates = []
navitems = []
total_diff = total_cg_miss = total_gy_miss = 0
for n in range(1, 81):
    zhi = open(os.path.join(PROC, 'zhi', 'zhi_ch%d.txt' % n), encoding='utf-8').read()
    cg = open(os.path.join(PROC, 'cg', 'cg_ch%d.txt' % n), encoding='utf-8').read()
    gy = open(os.path.join(PROC, 'gy', 'gy_ch%d.txt' % n), encoding='utf-8').read()
    rows_html, st = R.render_chapter(zhi, cg, gy)
    total_diff += st['diff']
    total_cg_miss += st['cg_miss']
    total_gy_miss += st['gy_miss']
    zt = clean_title(zhi_titles.get(str(n), ''))
    ct = cg_clean(n); gt = gy_clean(n)
    table = ('<table><thead><tr>'
             '<th>程高本<span class="sub">%s</span></th>'
             '<th>脂本（基准）<span class="sub">%s</span></th>'
             '<th>癸酉本<span class="sub">%s</span></th>'
             '</tr></thead><tbody>%s</tbody></table>'
             % (html.escape(ct), html.escape(zt), html.escape(gt), rows_html))
    stat = ('脂本句 %d ｜ 有差异行 %d ｜ 程高缺句 %d ｜ 癸酉缺句 %d'
            % (st['base_sents'], st['diff'], st['cg_miss'], st['gy_miss']))
    templates.append(
        '<script type="text/template" id="tpl%d" data-zt="%s" data-ct="%s" data-gt="%s" data-stat="%s">%s</script>'
        % (n, html.escape(zt, quote=True), html.escape(ct, quote=True),
           html.escape(gt, quote=True), html.escape(stat, quote=True), table)
    )
    navitems.append(
        '<li data-ch="%d"%s><span class="navnum">第%d回</span><span class="navttl">%s</span></li>'
        % (n, ' class="active"' if n == 1 else '', n, html.escape(zt))
    )
tpl = open(os.path.join(ROOT, 'templates', 'page.html'), encoding='utf-8').read()
page = (tpl.replace('__NAV__', '\n'.join(navitems))
           .replace('__TEMPLATES__', '\n'.join(templates)))
dist = os.path.join(ROOT, 'dist')
os.makedirs(dist, exist_ok=True)
out = os.path.join(dist, 'index.html')
open(out, 'w', encoding='utf-8').write(page)
print('written:', out, '%.1f MB' % (len(page)/1048576))
print('TOTAL: 差异行=%d 程高缺句=%d 癸酉缺句=%d' % (total_diff, total_cg_miss, total_gy_miss))
