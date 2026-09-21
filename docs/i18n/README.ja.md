# Mystilink 占星計算機

> Languages: [English](../../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Français](README.fr.md) | [Español](README.es.md)

## 概要

**ネイタルチャート**、**日次トランジット**要約（トランジット惑星 vs ネイタル）、および**月次**トランジット概要を計算します。出力は構造化 JSON です。惑星位置は `pyswisseph` 経由の Swiss Ephemeris を使用します（星暦ファイルがない場合は Moshier にフォールバック）。

本リポジトリは**計算ライブラリ / CLI**です。運勢の散文は生成しません。

## プラットフォームと言語

| 層 | 提供物 |
|----|--------|
| Python | インストール可能なパッケージ `mystilink-horoscope-calculator` + ライブラリ API |
| CLI | `horoscope`（natal / daily / monthly / version） |
| C | CLI を spawn するヘッダ + ソース（`bindings/c`） |
| C++ | C バインディング上の薄いラッパー（`bindings/cpp`） |
| C# | CLI を spawn する .NET ライブラリ（`bindings/csharp`） |
| Java | CLI を spawn する Maven レイアウトクラス（`bindings/java`） |
| JavaScript | npm パッケージ：Node spawn + 注入ランナー付きブラウザファクトリ（`bindings/js`） |

例は `examples/{c,cpp,csharp,java,js,node,python}/` にあります。

言語バインディングは、設定されていれば `MYSTILINK_HOROSCOPE_CLI`、それ以外は `PATH` 上の `horoscope` を解決します。別名 `mystilink-horoscope` もインストールされます。

## 要件

- Python 3.9+
- 依存：`pyswisseph`（`pyproject.toml` に宣言）

## インストール

リポジトリルートから：

```bash
pip install -e .
```

ライブラリとコンソールスクリプト `horoscope` がインストールされます。

## CLI

すべてのサブコマンドは UTF-8 JSON を stdout に出力します。非ゼロ終了コード時はエラーを stderr に書き込みます。

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

ネイタル JSON には `schema_version`：`mystilink.horoscope.natal/0.1`、レガシー `points`、契約エイリアス `planets` が含まれます。

### Daily

ネイタル出生データに対象カレンダー日を加えます。トランジット時刻はデフォルトで現地正午（`12:00`）；`--transit-time HH:MM` で上書きできます。

```bash
horoscope daily \
  --datetime "1990-06-15 14:30" \
  --timezone Asia/Shanghai \
  --lat 31.2304 \
  --lon 121.4737 \
  --date 2026-09-12
```

応答の要点：`transit_points`、`aspects_to_natal`、`summary.aspect_counts`、`summary.themes`、`summary.overall_tone`。

### Monthly

月の 1 日、中旬（15 日または末日）、末日を現地正午でサンプリングし、太陽星座の経路とアスペクト圧力を集計します。

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

または：`python -m mystilink_horoscope ...`（同じ CLI）。

## バインディング用法（概略）

- **C / C++**：`bindings/c/mystilink_horoscope.c` をリンクし `mystilink_horoscope_run` を呼び出します。
- **C#**：`bindings/csharp` を参照し `HoroscopeCli.Natal(...)` を呼び出します。
- **Java**：`bindings/java` をコンパイルし `HoroscopeCli.natal(...)` を呼び出します。
- **Node**：`import { natal } from './bindings/js/src/node.js'`。
- **Browser**：`createClient({ run })`。`run(args)` はホストが提供する必要があります（ブラウザ内プロセス spawn なし）。
- **Python バインディング補助**：`bindings/python/mystilink_horoscope_binding.py`（ライブラリ + `run_cli`）。

実行可能サンプルは `examples/` を参照（spawn 系バインディングには CLI のインストールが必要）。

## Schema

リクエスト/レスポンス形状の JSON Schema 草案は `schema/` にあります。

## テスト / フィクスチャ

サンプルのゴールデン入力は `tests/fixtures/` にあります。インストール後に Python 例を実行：

```bash
python examples/python/example.py
```


任意の `--envelope` は結果を `mystilink.envelope/0.1` で包みます（デフォルトは裸の JSON）。

## 制限

- `pyswisseph` が必要です。Swiss Ephemeris データファイルがない場合、可能なときは Moshier 方式にフォールバックします。
- 座標は地理緯度/経度（度）；タイムゾーンは有効な IANA 名である必要があります。
- 日次/月次出力のテーマスコアはアスペクト種類とオーブからの構造化ヒューリスティックであり、解釈文ではありません。

## ライセンス

MIT。[LICENSE](../../LICENSE) を参照。
