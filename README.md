# hongloumeng-compare

《红楼梦》三版本字符级对比工具（前 80 回）。以**脂评汇校本（lingr7）为基准**按句切行，左栏**程高本**、右栏**癸酉本**逐字对齐，行内字符级高亮，产出单页 `dist/index.html`。

## 在线访问

启用 GitHub Pages 后：**https://danerlt.github.io/hongloumeng-compare/**
（每次推送到 `main` 由 GitHub Actions 自动构建并部署，见下文「自动部署」。）

## 读图

- **行** = 脂本（基准）的一句话。
- **黄底** = 与脂本同位置的改字；**绿底** = 该版本相对脂本多出的字。
- **中栏下划线** = 脂本此处字词被改或被删。
- **（程高无 / 癸酉无）** = 整句缺失。
- **【…】** 灰色小字 = 脂批，**不参与**比对（顶部开关可整体隐藏）。
- 顶部还有「仅看差异行」开关，便于聚焦异文。

## 本地预览（最快：仓库已自带数据）

`data/` 已随仓库提交，clone 下来直接构建即可，**无需联网现取**：

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_all.py          # 读 data/processed/，产出 dist/index.html
python3 -m http.server 8080 --directory dist
# 浏览器打开 http://localhost:8080
```

## 重新抓取 / 更新源数据（可选）

仅当要刷新底本时才需要。脂本、程高从公网现取，癸酉 docx 已随仓库在 `data/raw/guiyou.docx`：

```bash
bash scripts/fetch_data.sh           # clone 脂本+程高；癸酉用仓库内 docx（缺失时可 export GUIYOU_DOCX_URL 补齐）
python scripts/parse_tex.py          # 解析脂本 .tex -> data/processed/zhi/（80 回，0 LaTeX 残留）
python scripts/extract_local.py      # 切程高(ch_cgb)+癸酉(docx) -> data/processed/{cg,gy}/（各 80 回）
python scripts/build_all.py          # 渲染 80 回 -> dist/index.html
```

## 数据来源

- **脂本（基准）**：`lingr7/HongLouMeng-ZhiPingBen` 的 `tex_src/book/TeX_files/chapter01..80.tex`（脂评汇校本，含甲戌/庚辰/蒙府批语，正文已简体清洁）。
- **程高本**：`EaconTang/gitbook-hongloumeng` 的 `ch_cgb/001..120.md`（仓库根目录的 `cgb.md` 只是简介页，正文按回拆在 `ch_cgb/`，`fetch_data.sh` 会合并为 `data/raw/chenggao.md`）。
- **癸酉本**：吴氏石头记 108 回 2020 版 docx，随仓库提交在 `data/raw/guiyou.docx`，仅取前 80 回。

## 自动部署（GitHub Actions + Pages）

`.github/workflows/pages.yml`：每次 push 到 `main` 自动 `pip install` → `python scripts/build_all.py` → 发布到 GitHub Pages（`data/` 已在仓库，无需现取外部源，整个流程约 1~2 分钟）。

**首次需一次性设置**：仓库 **Settings → Pages → Build and deployment → Source 选「GitHub Actions」**。

## 项目结构

```
scripts/
  fetch_data.sh        # 现取脂本/程高（癸酉随仓库），写入 data/
  parse_tex.py         # 解析 lingr7 .tex（去 footnote/字体命令、校勘标记、脂批包成【】）
  extract_local.py     # 切程高 ch_cgb + 癸酉 docx 各 1–80 回
  build_all.py         # 组装单页 HTML（懒加载模板 + 侧栏导航）
lib/
  cmp_lib.py           # 原子化 + 归一化(OpenCC t2s) + 字符级 diff
  cmp_sent.py          # 按 。！？ 切句（不在【】内断）
  render_basesent.py   # 句级对齐 + 三栏行内高亮渲染
templates/page.html    # 单页骨架（CSS + JS + 占位符）
data/                  # 原始与处理后文本 + 癸酉 docx（随仓库提交；dist/ 不进 git）
```

## 依赖

- `opencc`（简繁归一化，仅用于 diff 比对的 key，展示仍按各版本原文）
- `python-docx`（解析癸酉 docx）

## 说明：版本底本差异（非 bug）

各版本回目/用字差异源于所选公开底本，属事实差异，不应「修正」：

- 程高第 3 回回目为「贾雨村夤缘复旧职　林黛玉抛父进京都」，第 6 回作「刘姥姥」。
- 脂本（汇校本）第 5 回回目为庚辰系「开生面梦演红楼梦　立新场情传幻境情」。
- 第 79、80 回回目相同（lingr7 给 80 加「续」标记，反映庚辰本原不分回）。
- 癸酉本正文中夹有「第N回中…」式旁注，会被识别为癸酉新增字（绿底），系事实差异。
