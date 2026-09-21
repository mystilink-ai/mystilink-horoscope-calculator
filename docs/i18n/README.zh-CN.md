# Mystilink 占星计算器

> Languages: [English](../../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Français](README.fr.md) | [Español](README.es.md)

## 概述

计算**本命盘**、**日运（行运相对本命）**与**月运概览**。输出为结构化 JSON。行星位置通过 `pyswisseph` 调用 Swiss Ephemeris（无星历文件时可回退 Moshier）。

本仓库是**计算库 / CLI**，不生成运势散文。

## 平台与语言

| 层级 | 交付 |
|------|------|
| Python | 可安装包 `mystilink-horoscope-calculator` + 库 API |
| CLI | `horoscope`（natal / daily / monthly / version） |
| C | 头文件 + 源码，子进程调用 CLI（`bindings/c`） |
| C++ | 对 C 绑定的薄封装（`bindings/cpp`） |
| C# | .NET 库，子进程调用 CLI（`bindings/csharp`） |
| Java | Maven 布局类，子进程调用 CLI（`bindings/java`） |
| JavaScript | npm 包：Node 子进程 + Browser 注入式 runner（`bindings/js`） |

示例位于 `examples/{c,cpp,csharp,java,js,node,python}/`。

各语言绑定优先使用环境变量 `MYSTILINK_HOROSCOPE_CLI`；未设置时查找 PATH 上的 `horoscope`。长别名 `mystilink-horoscope` 仍会安装。

## 环境要求

- Python 3.9+
- 依赖：`pyswisseph`（见 `pyproject.toml`）

## 安装

在仓库根目录执行：

```bash
pip install -e .
```

将安装库与控制台命令 `horoscope`。

## CLI

子命令均向 stdout 输出 UTF-8 JSON；失败时非 0 退出码，错误信息在 stderr。

### 本命盘

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
```

### 日运

本命出生数据 + 目标日期。行运时刻默认当地正午（`12:00`），可用 `--transit-time HH:MM` 覆盖。

```bash
horoscope daily \
  --datetime "1990-06-15 14:30" \
  --timezone Asia/Shanghai \
  --lat 31.2304 \
  --lon 121.4737 \
  --date 2026-09-12
```

主要字段：`transit_points`、`aspects_to_natal`、`summary.aspect_counts`、`summary.themes`、`summary.overall_tone`。

### 月运

对当月 1 日、月中（15 或月末）、月末正午采样，汇总太阳星座路径与相位压力。

```bash
horoscope monthly \
  --datetime "1990-06-15 14:30" \
  --timezone Asia/Shanghai \
  --lat 31.2304 \
  --lon 121.4737 \
  --year 2026 \
  --month 9
```

### 版本

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

也可：`python -m mystilink_horoscope ...`（同 CLI）。

## 绑定用法（摘要）

- **C / C++**：链接 `bindings/c/mystilink_horoscope.c`，调用 `mystilink_horoscope_run`。
- **C#**：引用 `bindings/csharp`，调用 `HoroscopeCli.Natal(...)`。
- **Java**：编译 `bindings/java`，调用 `HoroscopeCli.natal(...)`。
- **Node**：`import { natal } from './bindings/js/src/node.js'`。
- **Browser**：`createClient({ run })`，由宿主实现 `run(args)`（浏览器内无法直接起进程）。
- **Python 辅助**：`bindings/python/mystilink_horoscope_binding.py`（库 API + `run_cli`）。

可运行示例见 `examples/`（子进程类绑定需已安装 CLI）。

## Schema

请求/响应形状草稿见 `schema/`。

## 测试 / 用例

固定入参见 `tests/fixtures/`。安装后可运行：

```bash
python examples/python/example.py
```


可选 `--envelope` 将结果包装为 `mystilink.envelope/0.1`（默认仍为裸 JSON）。

## 限制

- 需要 `pyswisseph`。缺少 Swiss Ephemeris 数据文件时，可能回退 Moshier。
- 经纬度为地理度数；时区须为合法 IANA 名称。
- 日/月运中的主题分数由相位类型与容许度启发式得出，不是解读文案。

## 许可

MIT。见 [LICENSE](../../LICENSE)。
