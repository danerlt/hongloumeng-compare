# hongloumeng-compare
《红楼梦》三版本字符级对比工具（前 80 回）。基准=脂评汇校本（lingr7），侧栏=程高本、癸酉本。
## 快速开始
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    export GUIYOU_DOCX_URL="<本仓 Release 中 guiyou.docx 的直链>"
    bash scripts/fetch_data.sh
    python scripts/parse_tex.py
    python scripts/extract_local.py
    python scripts/build_all.py
    # 用浏览器打开 dist/index.html
## 数据来源
- 脂本：`lingr7/HongLouMeng-ZhiPingBen`（脂评汇校本，含甲戌/庚辰/蒙府批语）
- 程高本：`EaconTang/gitbook-hongloumeng` 的 `cgb.md`
- 癸酉本：本仓 Release（吴氏石头记 108 回 2020 版，仅取前 80 回）
## 读图
- 行 = 脂本一句。
- 黄底 = 与脂本同位置改字；绿底 = 该版本相对脂本多出的字。
- 中栏下划线 = 此处字词被改或被删。
- （程高无 / 癸酉无） = 整句缺失。
- 【…】 灰色小字 = 脂批，**不参与**比对。
## 服务器部署
    git clone https://github.com/danerlt/hongloumeng-compare.git
    cd hongloumeng-compare
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    export GUIYOU_DOCX_URL="..."
    bash scripts/fetch_data.sh
    python scripts/parse_tex.py
    python scripts/extract_local.py
    python scripts/build_all.py
    python3 -m http.server 8080 --directory dist
