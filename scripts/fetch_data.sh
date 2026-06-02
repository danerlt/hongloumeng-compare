#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p data/zhi data/raw
echo "=== 1) 脂本：git clone lingr7（脂评汇校本） ==="
if [ ! -d /tmp/zpb ]; then
    git clone --depth=1 https://github.com/lingr7/HongLouMeng-ZhiPingBen.git /tmp/zpb
fi
cp /tmp/zpb/tex_src/book/TeX_files/chapter*.tex data/zhi/
echo "脂本 .tex 个数: $(ls data/zhi/chapter*.tex | wc -l)  (期望 80)"
echo "=== 2) 程高本：EaconTang gitbook 的 ch_cgb/*.md（合并为 chenggao.md） ==="
# 注意：仓库根目录的 cgb.md 只是简介页；正文按回拆在 ch_cgb/001.md..120.md，
# 每回 "### 第N回 回目" + <p>正文</p>。这里 clone 后按回号合并成单文件供解析。
if [ ! -d /tmp/cgb ]; then
    git clone --depth=1 https://github.com/EaconTang/gitbook-hongloumeng.git /tmp/cgb
fi
: > data/raw/chenggao.md
for f in $(ls /tmp/cgb/ch_cgb/*.md | sort); do
    cat "$f" >> data/raw/chenggao.md
    printf '\n' >> data/raw/chenggao.md
done
echo "cgb 合并字节: $(wc -c < data/raw/chenggao.md)"
echo "=== 3) 癸酉本：取仓库根目录的 docx ==="
# 癸酉本 docx（吴氏石头记 108 回 2020 版）直接随仓库提交，放在仓库根目录。
# 服务器 git clone 后即在根目录，无需再下载。也可用 GUIYOU_DOCX_URL 覆盖。
GUIYOU_SRC="$ROOT/108回癸酉本石头记（2020版）.docx"
if [ -n "${GUIYOU_DOCX_URL:-}" ]; then
    curl -fsSL "$GUIYOU_DOCX_URL" -o data/raw/guiyou.docx
elif [ -f "$GUIYOU_SRC" ]; then
    cp "$GUIYOU_SRC" data/raw/guiyou.docx
else
    echo "找不到癸酉 docx：既无 GUIYOU_DOCX_URL，根目录也无 $GUIYOU_SRC" >&2
    exit 1
fi
echo "guiyou.docx 字节: $(wc -c < data/raw/guiyou.docx)  (期望 ~2.3MB)"
echo "=== 全部数据就位 ==="
