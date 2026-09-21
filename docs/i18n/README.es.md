# Mystilink Calculadora de horóscopo

> Languages: [English](../../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Français](README.fr.md) | [Español](README.es.md)

## Resumen

Calcula **cartas natales**, resúmenes de **tránsito diario** (planetas de tránsito vs natal) y panorámicas de tránsito **mensuales**. La salida es JSON estructurado. Las posiciones planetarias usan Swiss Ephemeris vía `pyswisseph` (reserva Moshier cuando no hay archivos de efemérides).

Este repositorio es una **biblioteca de cálculo / CLI**. No produce ensayos de fortuna en prosa.

## Plataformas e idiomas

| Capa | Entrega |
|------|----------|
| Python | Paquete instalable `mystilink-horoscope-calculator` + API de biblioteca |
| CLI | `horoscope` (natal / daily / monthly / version) |
| C | Cabecera + fuente que lanza el CLI (`bindings/c`) |
| C++ | Envoltorio ligero sobre el enlace C (`bindings/cpp`) |
| C# | Biblioteca .NET que lanza el CLI (`bindings/csharp`) |
| Java | Clase con disposición Maven que lanza el CLI (`bindings/java`) |
| JavaScript | Paquete npm: spawn de Node + fábrica de navegador con runner inyectado (`bindings/js`) |

Los ejemplos están en `examples/{c,cpp,csharp,java,js,node,python}/`.

Los enlaces de lenguaje resuelven el ejecutable como `MYSTILINK_HOROSCOPE_CLI` si está definido; de lo contrario `horoscope` en `PATH`. El alias `mystilink-horoscope` permanece instalado.

## Requisitos

- Python 3.9+
- Dependencia: `pyswisseph` (declarada en `pyproject.toml`)

## Instalación

Desde la raíz del repositorio:

```bash
pip install -e .
```

Esto instala la biblioteca y el script de consola `horoscope`.

## CLI

Todos los subcomandos imprimen JSON UTF-8 en stdout. Los códigos de salida distintos de cero escriben errores en stderr.

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

El JSON natal incluye `schema_version`: `mystilink.horoscope.natal/0.1`, más el legado `points` y el alias de contrato `planets`.

### Daily

Datos de nacimiento natales más una fecha de calendario objetivo. La hora de tránsito por defecto es mediodía local (`12:00`); anule con `--transit-time HH:MM`.

```bash
horoscope daily \
  --datetime "1990-06-15 14:30" \
  --timezone Asia/Shanghai \
  --lat 31.2304 \
  --lon 121.4737 \
  --date 2026-09-12
```

Aspectos destacados de la respuesta: `transit_points`, `aspects_to_natal`, `summary.aspect_counts`, `summary.themes`, `summary.overall_tone`.

### Monthly

Muestrea el día 1, el medio (15 o último) y el último día del mes al mediodía local; agrega la ruta del signo solar y la presión de aspectos.

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

## API de Python

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

O: `python -m mystilink_horoscope ...` (mismo CLI).

## Uso de enlaces (esquema)

- **C / C++**: enlace `bindings/c/mystilink_horoscope.c` y llame a `mystilink_horoscope_run`.
- **C#**: referencie `bindings/csharp` y llame a `HoroscopeCli.Natal(...)`.
- **Java**: compile `bindings/java` y llame a `HoroscopeCli.natal(...)`.
- **Node**: `import { natal } from './bindings/js/src/node.js'`.
- **Browser**: `createClient({ run })` donde `run(args)` debe ser suministrado por el anfitrión (sin spawn de proceso en el navegador).
- **Ayuda de enlace Python**: `bindings/python/mystilink_horoscope_binding.py` (biblioteca + `run_cli`).

Véase `examples/` para muestras ejecutables (el CLI debe estar instalado para enlaces basados en spawn).

## Schema

Borradores JSON Schema para formas de solicitud/respuesta están en `schema/`.

## Pruebas / fixtures

Entradas golden de muestra viven en `tests/fixtures/`. Ejecute el ejemplo de Python tras la instalación:

```bash
python examples/python/example.py
```


La opción `--envelope` envuelve el resultado como `mystilink.envelope/0.1` (por defecto sigue siendo JSON desnudo).

## Límites

- Requiere `pyswisseph`. Sin archivos de datos Swiss Ephemeris, el cálculo recurre al método Moshier cuando es posible.
- Las coordenadas son latitud/longitud geográfica en grados; la zona horaria debe ser un nombre IANA válido.
- Las puntuaciones de tema en la salida diaria/mensual son heurísticas estructuradas a partir del tipo de aspecto y el orbe, no texto interpretativo.

## Licencia

MIT. Véase [LICENSE](../../LICENSE).
