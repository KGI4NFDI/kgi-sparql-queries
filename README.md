# kgi-sparql-queries

[![Github Actions Build](https://github.com/KGI4NFDI/kgi-sparql-queries/actions/workflows/build.yml/badge.svg)](https://github.com/KGI4NFDI/kgi-sparql-queries/actions/workflows/build.yml)
[![GitHub issues](https://img.shields.io/github/issues/KGI4NFDI/kgi-sparql-queries.svg)](https://github.com/KGI4NFDI/kgi-sparql-queries/issues)
[![GitHub closed issues](https://img.shields.io/github/issues-closed/KGI4NFDI/kgi-sparql-queries.svg)](https://github.com/KGI4NFDI/kgi-sparql-queries/issues/?q=is%3Aissue+is%3Aclosed)
[![API Docs](https://img.shields.io/badge/API-Documentation-blue)](https://KGI4NFDI.github.io/kgi-sparql-queries/)
[![License](https://img.shields.io/github/license/KGI4NFDI/kgi-sparql-queries.svg)](https://opensource.org/licenses/MIT)

The example SPARQL queries of the
[KGI4NFDI](https://base4nfdi.de/projects/kgi4nfdi) registry and of its individual
knowledge graphs.

## Contents

| Path | Content |
|---|---|
| [`data/sources.yaml`](data/sources.yaml) | where each KG publishes its examples |
| `query-sets/<namespace>@<domain>.yaml` | one [snapquery](https://github.com/WolfgangFahl/snapquery) named query set per KG |

A harvester extracts the examples from the pages listed in `data/sources.yaml`.

## Run locally

Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
kgi-queries harvest    # fetch the examples listed in data/sources.yaml
```

## Run with Docker

```bash
scripts/docker
```

Builds the image and runs the harvest in it; `query-sets/` is written into the repository.

## Tests

```bash
scripts/test
```

## License

Code is MIT. The harvested queries keep the license of their source.
