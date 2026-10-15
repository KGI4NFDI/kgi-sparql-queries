"""
Harvest the example queries of the sources in data/sources.yaml with snapquery
"""

import re
from collections import Counter
from typing import List, Optional

import requests
import yaml
from bs4 import BeautifulSoup
from snapquery.snapquery_core import NamedQuery, NamedQuerySet
from snapquery.wd_page_query_extractor import WikidataQueryExtractor

from kgi_example_queries import __version__

USER_AGENT = f"kgi-sparql-queries/{__version__} (https://github.com/KGI4NFDI/kgi-sparql-queries)"
HEADINGS = ["h1", "h2", "h3", "h4", "h5", "h6"]
SPARQL = re.compile(r"\b(SELECT|CONSTRUCT|ASK|DESCRIBE)\b.*\{", re.IGNORECASE | re.DOTALL)


def load_sources(path: str = "data/sources.yaml") -> List[dict]:
    """
    load the sources of the manifest

    Args:
        path: the path of the YAML file

    Returns:
        the source records
    """
    with open(path, encoding="utf-8") as yaml_file:
        sources = yaml.safe_load(yaml_file)["sources"]
    return sources


def harvest_html(source: dict, html: Optional[str] = None) -> NamedQuerySet:
    """
    extract the example queries of an HTML page: every pre or textarea
    element holding a SPARQL query, named by the heading above it and
    numbered where several queries share a heading

    Args:
        source: the source record
        html: the page content, fetched from the source url when None

    Returns:
        the snapquery named query set
    """
    if html is None:
        response = requests.get(source["url"], headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()
        html = response.text
    soup = BeautifulSoup(html, "html.parser")
    blocks = [block for block in soup.find_all(["pre", "textarea"]) if SPARQL.search(block.get_text())]
    headings = [block.find_previous(HEADINGS) for block in blocks]
    titles = [" ".join(heading.get_text().split()) if heading else source["name"] for heading in headings]
    total = Counter(titles)
    seen = Counter()
    query_set = NamedQuerySet(domain=source["domain"], namespace=source["namespace"], target_graph_name=source["graph"])
    for block, heading, title in zip(blocks, headings, titles):
        seen[title] += 1
        name = f"{title} {seen[title]}" if total[title] > 1 else title
        url = source["url"]
        if heading is not None and heading.get("id"):
            url = f"{url}#{heading['id']}"
        query = NamedQuery(
            domain=source["domain"],
            namespace=source["namespace"],
            name=name,
            title=name,
            description="",
            url=url,
            sparql=block.get_text().strip(),
        )
        query_set.add(query)
    return query_set


def harvest_wikitext(source: dict, wikitext: Optional[str] = None) -> NamedQuerySet:
    """
    extract the example queries of a Wikibase examples page

    Args:
        source: the source record
        wikitext: the page content, fetched from the source url when None

    Returns:
        the snapquery named query set
    """
    # nqm is only needed to store the queries in snapquery's database
    extractor = WikidataQueryExtractor(
        nqm=None,
        base_url=source["url"],
        domain=source["domain"],
        namespace=source["namespace"],
        target_graph_name=source["graph"],
    )
    extractor.extract_queries(wikitext)
    query_set = extractor.named_query_list
    return query_set


def harvest_source(source: dict, content: Optional[str] = None) -> NamedQuerySet:
    """
    extract the example queries of a source with the extractor for its format

    Args:
        source: the source record
        content: the page content, fetched from the source url when None

    Returns:
        the snapquery named query set
    """
    if source.get("format") == "wikitext":
        query_set = harvest_wikitext(source, content)
    else:
        query_set = harvest_html(source, content)
    return query_set


def harvest() -> int:
    """
    harvest all sources and write one query set per source

    Returns:
        the process exit code
    """
    exit_code = 0
    for source in load_sources():
        if source.get("format") == "pinned":
            print(f"{source['id']} {source['name']}: pinned, query set kept")
            continue
        query_set = harvest_source(source)
        if len(query_set) == 0:
            print(f"{source['id']} {source['name']}: no queries found, nothing written")
            exit_code = 1
            continue
        path = f"query-sets/{query_set.namespace}@{query_set.domain}.yaml"
        query_set.save_to_yaml_file(path)
        print(f"{source['id']} {source['name']}: {len(query_set)} queries -> {path}")
    return exit_code
