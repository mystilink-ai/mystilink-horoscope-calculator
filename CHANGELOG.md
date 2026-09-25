# Changelog

## 0.2.3

- Natal `to_serializable` also emits `zodiac_system` (alias of `zodiac_mode`)
- Tests against sibling schemas for natal / daily / monthly when present

## 0.2.2

- CLI natal/daily/monthly `--envelope` / `--locale`
- Python binding resolves short CLI `horoscope` before `mystilink-horoscope`
- Default stdout remains bare chart JSON

## 0.2.1

- Primary CLI entry point is `horoscope`; alias `mystilink-horoscope` remains installed
- Bindings default to spawning `horoscope` (override with `MYSTILINK_HOROSCOPE_CLI`)


## 0.2.1

- Primary CLI command is now `horoscope` (long alias `mystilink-horoscope` still installed)
- Bindings default to resolving `horoscope` on `PATH`

## 0.2.0

- Natal / daily / monthly JSON include `schema_version`
- Natal adds `planets` as alias of `points` (mystilink.horoscope.natal/0.1)
- CLI accepts optional `--birth-json` (mystilink.birth/0.1 BirthProfile) on natal/daily/monthly
- Legacy `--datetime` / `--timezone` / `--lat` / `--lon` remain supported

## 0.1.0

- Initial natal, daily, and monthly JSON CLI
