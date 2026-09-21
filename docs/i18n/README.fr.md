# Mystilink Calculateur d’horoscope

> Languages: [English](../../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Français](README.fr.md) | [Español](README.es.md)

## Aperçu

Calcule des **cartes natales**, des résumés de **transit quotidien** (planètes de transit vs natal) et des aperçus de transit **mensuels**. La sortie est du JSON structuré. Les positions planétaires utilisent Swiss Ephemeris via `pyswisseph` (repli Moshier lorsque les fichiers d’éphémérides sont indisponibles).

Ce dépôt est une **bibliothèque de calcul / CLI**. Il ne produit pas d’essais de fortune en prose.

## Plateformes et langages

| Couche | Livraison |
|--------|----------|
| Python | Paquet installable `mystilink-horoscope-calculator` + API bibliothèque |
| CLI | `horoscope` (natal / daily / monthly / version) |
| C | En-tête + source qui spawn le CLI (`bindings/c`) |
| C++ | Enveloppe légère sur la liaison C (`bindings/cpp`) |
| C# | Bibliothèque .NET qui spawn le CLI (`bindings/csharp`) |
| Java | Classe à disposition Maven qui spawn le CLI (`bindings/java`) |
| JavaScript | Paquet npm : spawn Node + factory navigateur avec runner injecté (`bindings/js`) |

Les exemples se trouvent sous `examples/{c,cpp,csharp,java,js,node,python}/`.

Les liaisons de langage résolvent l’exécutable comme `MYSTILINK_HOROSCOPE_CLI` s’il est défini, sinon `horoscope` sur `PATH`. L’alias `mystilink-horoscope` reste installé.

## Prérequis

- Python 3.9+
- Dépendance : `pyswisseph` (déclarée dans `pyproject.toml`)

## Installation

Depuis la racine du dépôt :

```bash
pip install -e .
```

Cela installe la bibliothèque et le script console `horoscope`.

## CLI

Toutes les sous-commandes impriment du JSON UTF-8 sur stdout. Les codes de sortie non nuls écrivent les erreurs sur stderr.

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

Le JSON natal inclut `schema_version` : `mystilink.horoscope.natal/0.1`, plus le legacy `points` et l’alias de contrat `planets`.

### Daily

Données de naissance natales plus une date calendaire cible. L’heure de transit vaut par défaut midi local (`12:00`) ; remplacer avec `--transit-time HH:MM`.

```bash
horoscope daily \
  --datetime "1990-06-15 14:30" \
  --timezone Asia/Shanghai \
  --lat 31.2304 \
  --lon 121.4737 \
  --date 2026-09-12
```

Points saillants de la réponse : `transit_points`, `aspects_to_natal`, `summary.aspect_counts`, `summary.themes`, `summary.overall_tone`.

### Monthly

Échantillonne le 1er, le milieu (15 ou dernier) et le dernier jour du mois à midi local ; agrège le parcours du signe solaire et la pression d’aspects.

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

## API Python

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

Ou : `python -m mystilink_horoscope ...` (même CLI).

## Usage des liaisons (esquisse)

- **C / C++** : lier `bindings/c/mystilink_horoscope.c` et appeler `mystilink_horoscope_run`.
- **C#** : référencer `bindings/csharp` et appeler `HoroscopeCli.Natal(...)`.
- **Java** : compiler `bindings/java` et appeler `HoroscopeCli.natal(...)`.
- **Node** : `import { natal } from './bindings/js/src/node.js'`.
- **Browser** : `createClient({ run })` où `run(args)` doit être fourni par l’hôte (pas de spawn de processus dans le navigateur).
- **Aide de liaison Python** : `bindings/python/mystilink_horoscope_binding.py` (bibliothèque + `run_cli`).

Voir `examples/` pour des échantillons exécutables (le CLI doit être installé pour les liaisons basées sur spawn).

## Schema

Des brouillons JSON Schema pour les formes requête/réponse sont sous `schema/`.

## Tests / fixtures

Des entrées golden d’exemple se trouvent dans `tests/fixtures/`. Exécuter l’exemple Python après installation :

```bash
python examples/python/example.py
```


L’option `--envelope` enveloppe le résultat en `mystilink.envelope/0.1` (par défaut : JSON nu).

## Limites

- Nécessite `pyswisseph`. Sans fichiers de données Swiss Ephemeris, le calcul bascule sur la méthode Moshier lorsque c’est possible.
- Les coordonnées sont latitude/longitude géographiques en degrés ; le fuseau doit être un nom IANA valide.
- Les scores de thème dans les sorties daily/monthly sont des heuristiques structurées à partir du type d’aspect et de l’orbe, pas du texte interprétatif.

## Licence

MIT. Voir [LICENSE](../../LICENSE).
