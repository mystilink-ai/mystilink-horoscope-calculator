# Mystilink 점성 계산기

> Languages: [English](../../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Français](README.fr.md) | [Español](README.es.md)

## 개요

**네이탈 차트**, **일일 트랜짓** 요약(트랜짓 행성 vs 네이탈), **월간** 트랜짓 개요를 계산합니다. 출력은 구조화 JSON 입니다. 행성 위치는 `pyswisseph` 를 통한 Swiss Ephemeris 를 사용합니다(천문력 파일이 없으면 Moshier 로 폴백).

이 저장소는 **계산 라이브러리 / CLI** 입니다. 운세 산문은 생성하지 않습니다.

## 플랫폼 및 언어

| 계층 | 제공물 |
|------|--------|
| Python | 설치 가능 패키지 `mystilink-horoscope-calculator` + 라이브러리 API |
| CLI | `horoscope`(natal / daily / monthly / version) |
| C | CLI 를 spawn 하는 헤더 + 소스(`bindings/c`) |
| C++ | C 바인딩 위의 얇은 래퍼(`bindings/cpp`) |
| C# | CLI 를 spawn 하는 .NET 라이브러리(`bindings/csharp`) |
| Java | CLI 를 spawn 하는 Maven 레이아웃 클래스(`bindings/java`) |
| JavaScript | npm 패키지: Node spawn + 주입 러너 브라우저 팩토리(`bindings/js`) |

예제는 `examples/{c,cpp,csharp,java,js,node,python}/` 에 있습니다.

언어 바인딩은 설정된 경우 `MYSTILINK_HOROSCOPE_CLI`, 그렇지 않으면 `PATH` 상의 `horoscope` 를 해석합니다. 별칭 `mystilink-horoscope` 도 설치됩니다.

## 요구 사항

- Python 3.9+
- 의존성: `pyswisseph`(`pyproject.toml` 에 선언)

## 설치

저장소 루트에서:

```bash
pip install -e .
```

라이브러리와 콘솔 스크립트 `horoscope` 가 설치됩니다.

## CLI

모든 하위 명령은 UTF-8 JSON 을 stdout 에 출력합니다. 비제로 종료 코드 시 오류는 stderr 에 기록됩니다.

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

네이탈 JSON 에는 `schema_version`: `mystilink.horoscope.natal/0.1`, 레거시 `points`, 계약 별칭 `planets` 가 포함됩니다.

### Daily

네이탈 출생 데이터에 대상 달력 날짜를 더합니다. 트랜짓 시각은 기본 현지 정오(`12:00`); `--transit-time HH:MM` 로 덮어쓸 수 있습니다.

```bash
horoscope daily \
  --datetime "1990-06-15 14:30" \
  --timezone Asia/Shanghai \
  --lat 31.2304 \
  --lon 121.4737 \
  --date 2026-09-12
```

응답 하이라이트: `transit_points`, `aspects_to_natal`, `summary.aspect_counts`, `summary.themes`, `summary.overall_tone`.

### Monthly

월의 1일, 중순(15일 또는 말일), 말일을 현지 정오에 샘플링하고 태양 별자리 경로와 애스펙트 압력을 집계합니다.

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

또는: `python -m mystilink_horoscope ...`(동일 CLI).

## 바인딩 사용법(요약)

- **C / C++**: `bindings/c/mystilink_horoscope.c` 를 링크하고 `mystilink_horoscope_run` 을 호출합니다.
- **C#**: `bindings/csharp` 를 참조하고 `HoroscopeCli.Natal(...)` 을 호출합니다.
- **Java**: `bindings/java` 를 컴파일하고 `HoroscopeCli.natal(...)` 을 호출합니다.
- **Node**: `import { natal } from './bindings/js/src/node.js'`.
- **Browser**: `createClient({ run })`. `run(args)` 는 호스트가 제공해야 합니다(브라우저 내 프로세스 spawn 없음).
- **Python 바인딩 헬퍼**: `bindings/python/mystilink_horoscope_binding.py`(라이브러리 + `run_cli`).

실행 가능 샘플은 `examples/` 참조(spawn 기반 바인딩은 CLI 설치 필요).

## Schema

요청/응답 형태의 JSON Schema 초안은 `schema/` 에 있습니다.

## 테스트 / 픽스처

샘플 골든 입력은 `tests/fixtures/` 에 있습니다. 설치 후 Python 예제 실행:

```bash
python examples/python/example.py
```


선택적 `--envelope` 는 결과를 `mystilink.envelope/0.1` 로 감쌉니다(기본은 원시 JSON).

## 제한

- `pyswisseph` 가 필요합니다. Swiss Ephemeris 데이터 파일이 없으면 가능한 경우 Moshier 방식으로 폴백합니다.
- 좌표는 지리 위도/경도(도); 타임존은 유효한 IANA 이름이어야 합니다.
- 일/월간 출력의 테마 점수는 애스펙트 유형과 오브의 구조화 휴리스틱이며, 해석 텍스트가 아닙니다.

## 라이선스

MIT. [LICENSE](../../LICENSE) 참조.
