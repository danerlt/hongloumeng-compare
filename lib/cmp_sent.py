# -*- coding: utf-8 -*-
"""按 。！？ 切句；不在【】内断；遇换行也断。"""
ENDERS = set('。！？')
CLOSERS = set('"』」）)')
def split_sentences(atoms):
    sents, cur = [], []
    i, n = 0, len(atoms)
    while i < n:
        a = atoms[i]
        if a['t'] == 'nl':
            if cur:
                sents.append(cur); cur = []
            i += 1
            continue
        cur.append(a)
        i += 1
        if a['t'] == 'punct' and a['o'] in ENDERS:
            while i < n and atoms[i]['t'] == 'punct' and atoms[i]['o'] in CLOSERS:
                cur.append(atoms[i]); i += 1
            sents.append(cur); cur = []
    if cur:
        sents.append(cur)
    return sents
