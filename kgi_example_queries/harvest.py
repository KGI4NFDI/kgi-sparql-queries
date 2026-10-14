"""
Harvest the example queries of the sources in data/sources.yaml with snapquery
"""

from typing import List, Optional

import yaml
from snapquery.snapquery_core import NamedQuerySet
from snapquery.wd_page_query_extractor import WikidataQueryExtractor


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


def harvest_source(source: dict, wikitext: Optional[str] = None) -> NamedQuerySet:
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
