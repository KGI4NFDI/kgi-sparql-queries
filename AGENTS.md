# AGENTS.md - kgi-sparql-queries

## Project Overview

kgi-sparql-queries collects the example SPARQL queries of the
[KGI4NFDI](https://base4nfdi.de/projects/kgi4nfdi) registry and of its
individual knowledge graphs as
[snapquery](https://github.com/WolfgangFahl/snapquery) named query sets.

- **GitHub**: https://github.com/KGI4NFDI/kgi-sparql-queries
- **Upstream**: [snapquery](https://github.com/WolfgangFahl/snapquery) - the
  named query and query set model come from there
- **Sibling**: [kgi-interop-monitor](https://github.com/KGI4NFDI/kgi-interop-monitor) -
  the registry snapshot and anything that queries an endpoint live there
- **Agent rules**: `Agent/Guido/BITPlan` on BITPlan's media wiki; the
  conventions this project follows are under [Conventions](#conventions)

## Boot

Agents working in this repository perform the mandatory boot sequence of the
`Agents` page on BITPlan's media wiki: PLAN-AND-ASK, Document-First, DMAIC
histogram, English-only.

**PLAN-AND-ASK is not optional here.** The scope of this project is agreed with
the maintainers before code is written; an agent that produces features which
were not asked for has failed, however good the code is. Put the plan in an
issue, get it agreed, then implement.

## Scope

MVP: a source manifest, a harvester and one query set per knowledge graph.
Add nothing that has not been agreed. Anything else - RDF export, reports,
parameterization, scheduled harvests - belongs in an issue first.

## Access

The harvester only reads the web pages listed in `data/sources.yaml`.

- Respect `robots.txt` and never work around bot challenges or other access
  controls; record the refusal and ask the owner instead.
- Never use credentials found in a harvested page.
- Do not query the knowledge graphs' SPARQL endpoints from this repository.
- Do not change KGI registry data; report problems to the KG owner.

## Provenance

Agent-written content that makes a claim - an issue comment, a measurement, a
design note - carries the BITPlan provenance markers:

| marker | meaning |
|--------|---------|
| `✍️🤖 Agent/<name>` | written by the agent |
| `🗣️ <human> → 🤖 Agent/<name>` | said by the human, transcribed by the agent |
| `👁️🧑 <human> ✓` | read and approved by the human before posting |

Generated code is reviewed before it is merged; the `👁️🧑 ✓` marker is what
says a human stood behind it.

Every query keeps its source: new sources go into `data/sources.yaml`, and a
query copied by hand states where, when and how it was copied.

## Commands

| Command | Purpose |
|---------|---------|
| `scripts/install` | pip install . |
| `scripts/test` | run the unittest suite, offline |
| `scripts/blackisort` | format code with isort + black - always before commit |
| `scripts/doc` | build API documentation |
| `scripts/release` | build and deploy the documentation, then commit and push |
| `scripts/checkos` | check the project against BITPlan's open source conventions |
| `scripts/docker` | build the image and run the harvest in it |
| `kgi-queries harvest` | fetch the examples listed in `data/sources.yaml` |

## Project Structure

| Path | Purpose |
|------|---------|
| `data/sources.yaml` | where each knowledge graph publishes its examples |
| `kgi_example_queries/` | the harvester package |
| `query-sets/<namespace>@<domain>.yaml` | generated: one snapquery named query set per knowledge graph |
| `tests/known_invalid_queries.yaml` | the committed queries snapquery's SPARQL parser rejects, grouped by cause |

`query-sets/` is harvester output: change the manifest or the harvester, not
the generated files.

A query set change that brings in an invalid query fails the tests until the
query is listed in `tests/known_invalid_queries.yaml` under its cause.

## Conventions

- Python 3.10 or newer
- Tests: **unittest**, offline; no pytest fixtures, no conftest.py
- Formatting: black (120 cols) + isort via `scripts/blackisort`
- One concern per commit
- Dependencies: the snapquery / pyLoDStorage ecosystem - justify any new
  dependency. Prefer using what snapquery already provides over reimplementing
  it here.
