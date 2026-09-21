# Mystilink 占星計算器

> Languages: [English](../../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Français](README.fr.md) | [Español](README.es.md)

## 概述

計算**本命盤**、**日運（行運相對本命）**與**月運概覽**。輸出為結構化 JSON。行星位置透過 `pyswisseph` 呼叫 Swiss Ephemeris（無星曆檔案時可回退 Moshier）。

本倉庫是**計算庫 / CLI**。不產生運勢散文。

## 平台與語言

| 層級 | 交付 |
|------|------|
| Python | 可安裝套件 `mystilink-horoscope-calculator` + 函式庫 API |
| CLI | `horoscope`（natal / daily / monthly / version） |
| C | 標頭檔 + 原始碼，子行程呼叫 CLI（`bindings/c`） |
| C++ | 對 C 綁定的薄封裝（`bindings/cpp`） |
| C# | .NET 函式庫，子行程呼叫 CLI（`bindings/csharp`） |
| Java | Maven 佈局類別，子行程呼叫 CLI（`bindings/java`） |
| JavaScript | npm 套件：Node spawn + 瀏覽器注入式 runner（`bindings/js`） |

範例位於 `examples/{c,cpp,csharp,java,js,node,python}/`。

各語言綁定優先使用環境變數 `MYSTILINK_HOROSCOPE_CLI`；未設定時查找 `PATH` 上的 `horoscope`。別名 `mystilink-horoscope` 仍會安裝。

## 環境需求

- Python 3.9+
- 相依性：`pyswisseph`（見 `pyproject.toml`）

## 安裝

在倉庫根目錄執行：

```bash
pip install -e .
```

將安裝函式庫與主控台指令 `horoscope`。

## CLI

所有子命令向 stdout 輸出 UTF-8 JSON。非零結束碼時錯誤寫入 stderr。

### Natal

```bash
horoscope natal \
  --datetime "1990-06-15 14:30" \
  --timezone Asia/Shanghai \
  --lat 31.2304 \
  --lon 121.4737 \
  [--house-system P] \
  [--zodiac tropical|sidereal] \
  [--sidereal-mode lahiri] \
  [--true-solar-time] \
  [--no-aspects]

horoscope natal --birth-json tests/fixtures/birth.profile.v0.json [--no-aspects]
```

本命盤 JSON 含 `schema_version`：`mystilink.horoscope.natal/0.1`，以及舊欄位 `points` 與契約別名 `planets`。

### Daily

本命出生資料加上目標曆日。行運時刻預設當地正午（`12:00`）；可用 `--transit-time HH:MM` 覆寫。

```bash
horoscope daily \
  --datetime "1990-06-15 14:30" \
  --timezone Asia/Shanghai \
  --lat 31.2304 \
  --lon 121.4737 \
  --date 2026-09-12
```

回應重點：`transit_points`、`aspects_to_natal`、`summary.aspect_counts`、`summary.themes`、`summary.overall_tone`。

### Monthly

對當月 1 日、月中（15 或月末）、月末於當地正午取樣；彙總太陽星座路徑與相位壓力。

```bash
horoscope monthly \
  --datetime "1990-06-15 14:30" \
  --timezone Asia/Shanghai \
  --lat 31.2304 \
  --lon 121.4737 \
  --year 2026 \
  --month 9
```

### Version

```bash
horoscope version
```

## Python API

```python
from mystilink_horoscope.natal import calculate_chart, parse_local_datetime, to_serializable
from mystilink_horoscope.daily import calculate_daily
from mystilink_horoscope.monthly import calculate_monthly

dt = parse_local_datetime("1990-06-15 14:30", "Asia/Shanghai")
natal = to_serializable(calculate_chart(dt, 31.2304, 121.4737))
daily = calculate_daily(
    "1990-06-15 14:30", "Asia/Shanghai", 31.2304, 121.4737, "2026-09-12"
)
monthly = calculate_monthly(
    "1990-06-15 14:30", "Asia/Shanghai", 31.2304, 121.4737, 2026, 9
)
```

或：`python -m mystilink_horoscope ...`（同 CLI）。

## 綁定用法（摘要）

- **C / C++**：連結 `bindings/c/mystilink_horoscope.c` 並呼叫 `mystilink_horoscope_run`。
- **C#**：參考 `bindings/csharp` 並呼叫 `HoroscopeCli.Natal(...)`。
- **Java**：編譯 `bindings/java` 並呼叫 `HoroscopeCli.natal(...)`。
- **Node**：`import { natal } from './bindings/js/src/node.js'`。
- **Browser**：`createClient({ run })`，其中 `run(args)` 須由宿主提供（瀏覽器內無法直接起行程）。
- **Python 綁定輔助**：`bindings/python/mystilink_horoscope_binding.py`（函式庫 + `run_cli`）。

可執行範例見 `examples/`（以 spawn 為基礎的綁定需已安裝 CLI）。

## Schema

請求/回應形狀的 JSON Schema 草稿位於 `schema/`。

## 測試 / 用例

固定入參位於 `tests/fixtures/`。安裝後可執行 Python 範例：

```bash
python examples/python/example.py
```


可選 `--envelope` 將結果包裝為 `mystilink.envelope/0.1`（預設仍為裸 JSON）。

## 限制

- 需要 `pyswisseph`。缺少 Swiss Ephemeris 資料檔時，計算在可能時回退 Moshier。
- 座標為地理緯度/經度（度）；時區須為合法 IANA 名稱。
- 日/月運中的主題分數由相位類型與容許度啟發式得出，不是解讀文案。

## 授權

MIT。見 [LICENSE](../../LICENSE)。
