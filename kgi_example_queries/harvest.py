"""
Harvest the example queries of the sources in data/sources.yaml with snapquery
"""

from typing import List, Optional

import requests
import yaml
from bs4 import BeautifulSoup
from snapquery.snapquery_core import NamedQuerySet
from snapquery.wd_page_query_extractor import WikidataQueryExtractor

from kgi_example_queries import __version__

USER_AGENT = f"kgi-sparql-queries/{__version__} (https://github.com/KGI4NFDI/kgi-sparql-queries)"


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


def fetch_html(url: str) -> str:
    """
    fetch a rendered page

    Args:
        url: the url of the page

    Returns:
        the HTML of the page
    """
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    html = response.text
    return html


def extract_html(extractor: WikidataQueryExtractor, html: str):
    """
    extract the queries of a rendered wiki page: every SPARQL code block
    is a query, named by the heading above it

    Args:
        extractor: the snapquery extractor that builds and collects the named queries
        html: the HTML of the page
    """
    soup = BeautifulSoup(html, "html.parser")
    for block in soup.select(".mw-highlight-lang-sparql"):
        heading = block.find_previous(["h2", "h3", "h4"])
        if heading is None:
            continue
        # the text between the heading and the code block describes the query
        description = []
        for sibling in block.find_previous_siblings():
            if heading in (sibling, *sibling.find_all(heading.name)):
                break
            description.insert(0, sibling.get_text(" ", strip=True))
        title = heading.get_text(" ", strip=True)
        query = extractor.create_named_query(
            title=title, markup="\n".join(description), sparql=block.get_text().strip()
        )
        extractor.named_query_list.add(query)


def harvest_source(source: dict, content: Optional[str] = None) -> NamedQuerySet:
    """
    extract the example queries of a wiki examples page

    Args:
        source: the source record
        content: the page content, fetched from the source url when None

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
    if source["format"] == "html":
        # for wikis whose robots.txt disallows fetching the wikitext
        if content is None:
            content = fetch_html(source["url"])
        extract_html(extractor, content)
    else:
        extractor.extract_queries(content)
    query_set = extractor.named_query_list
    return query_set


def harvest() -> int:
    """
    harvest all sources and write one query set per source

    Returns:
        the process exit code
    """
    exit_code = 0
    for source in load_sources():
        query_set = harvest_source(source)
        if len(query_set) == 0:
            print(f"{source['id']} {source['name']}: no queries found, nothing written")
            exit_code = 1
            continue
        path = f"query-sets/{query_set.namespace}@{query_set.domain}.yaml"
        query_set.save_to_yaml_file(path)
        print(f"{source['id']} {source['name']}: {len(query_set)} queries -> {path}")
    return exit_code
