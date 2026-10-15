"""
Extract the example SPARQL queries of KGI4NFDI deliverable D3.1 into a snapquery query set

D3.1 "Best practices and guidelines for metadata mapping, linking, and integration",
version 1.0, https://doi.org/10.5281/zenodo.15780729, CC BY 4.0, is a PDF.
This script is the record of how its queries were copied.

Usage, from the repository root:
    pip install .[pinned]
    python scripts/extract_d31.py

The text is read with pypdf in plain mode; its layout mode inserts spaces inside IRIs.

Rule 1: a query starts at a line beginning with #, PREFIX or SELECT and ends at
the next empty line. This finds all 29 queries, but cuts 14 of them wrong.

Rule 2: page numbers and the empty lines at the top of a page are dropped, so a
query crossing a page break stays whole. 12 are still cut wrong.

Rule 3: a caption "Listing 1.n." also ends a query and names the query above it.
7 are still cut wrong.

Rule 4: a line of plain words after a line with a comment continues that comment,
which the PDF wrapped. 2 are still wrong: Q15, whose PREFIX IRIs lack angle
brackets in D3.1 itself, and Listing 1.9, which is complete.

Correction: a PREFIX IRI without angle brackets gets them. This changes Q15 as
published in D3.1.
"""

import re
import sys
from io import BytesIO
from typing import Dict, List
from urllib.robotparser import RobotFileParser

import pypdf
import requests
from snapquery.snapquery_core import NamedQuery, NamedQuerySet

PDF_URL = (
    "https://zenodo.org/records/15780729/files/"
    "D3.1%20Best%20practices%20and%20guidelines%20for%20metadata%20mapping,%20linking,%20and%20integration.pdf"
)
USER_AGENT = "kgi-sparql-queries (https://github.com/KGI4NFDI/kgi-sparql-queries)"
DOMAIN = "kgi.services.base4nfdi.de"

START = re.compile(r"^\s*(#|PREFIX\b|SELECT\b)")
WRAPPED = re.compile(r"^\s*[a-z][a-z ,]*[.,]?\s*$")
CAPTION = re.compile(r"^\s*(Listing \d+\.\d+)\.")
HEADING = re.compile(r"^(Q\d+[a-d]?|Story \d)\.? ")
BARE_PREFIX = re.compile(r"^(\s*PREFIX\s+[\w-]*:\s*)(https?://\S+)$", re.MULTILINE)
QUERY_FORM = re.compile(r"\b(SELECT|ASK|CONSTRUCT|DESCRIBE)\b")


def fetch_pdf() -> bytes:
    """
    download the PDF, if robots.txt allows it

    Returns:
        the PDF content
    """
    robots = RobotFileParser("https://zenodo.org/robots.txt")
    robots.read()
    if not robots.can_fetch(USER_AGENT, PDF_URL):
        sys.exit(f"robots.txt disallows {PDF_URL}")
    response = requests.get(PDF_URL, headers={"User-Agent": USER_AGENT}, timeout=60)
    response.raise_for_status()
    content = response.content
    return content


def read_lines(pdf: bytes) -> List[tuple]:
    """
    read the text of the PDF

    Args:
        pdf: the PDF content

    Returns:
        (page number, line) for every line of the PDF
    """
    lines = []
    for number, page in enumerate(pypdf.PdfReader(BytesIO(pdf)).pages, start=1):
        page_lines = page.extract_text(extraction_mode="plain").split("\n")
        page_lines = [line for line in page_lines if line.strip() != str(number)]
        while page_lines and not page_lines[0].strip():
            page_lines.pop(0)
        lines.extend((number, line) for line in page_lines)
    return lines


def find_queries(lines: List[tuple]) -> List[Dict]:
    """
    find the query blocks and the heading each one is under

    Args:
        lines: (page number, line) for every line of the PDF

    Returns:
        one dict per query with heading, page and lines
    """
    blocks = []
    block = None
    heading = None
    for page, line in lines:
        if block is None:
            caption = CAPTION.match(line)
            if caption and blocks and "name" not in blocks[-1]:
                blocks[-1]["name"] = caption.group(1)
            match = HEADING.match(line)
            # the table of contents repeats the headings, followed by dots
            if match and "...." not in line:
                heading = match.group(1)
            if START.match(line):
                block = {"heading": heading, "page": page, "lines": [line]}
            continue
        caption = CAPTION.match(line)
        if caption:
            block["name"] = caption.group(1)
        elif line.strip():
            if "#" in block["lines"][-1] and WRAPPED.match(line):
                block["lines"][-1] = block["lines"][-1].rstrip() + " " + line.strip()
            else:
                block["lines"].append(line)
            continue
        blocks.append(block)
        block = None
    if block:
        blocks.append(block)
    queries = [block for block in blocks if any(QUERY_FORM.search(line.split("#")[0]) for line in block["lines"])]
    return queries


def to_query_set(queries: List[Dict]) -> NamedQuerySet:
    """
    turn the query blocks into one snapquery query set: Q1 to Q16d, written for
    any knowledge graph, and the stories, written for Wikidata, FactGrid and MaRDI

    Args:
        queries: the query blocks

    Returns:
        the query set
    """
    query_set = NamedQuerySet(domain=DOMAIN, namespace="d3.1", target_graph_name="various")
    names = [query.get("name", query["heading"]) for query in queries]
    seen = {}
    for query, name in zip(queries, names):
        # number the queries that share a name, such as the two versions of Q7
        if names.count(name) > 1:
            seen[name] = seen.get(name, 0) + 1
            name = f"{name} {seen[name]}"
        sparql = "\n".join(line.rstrip() for line in query["lines"]).strip()
        sparql = BARE_PREFIX.sub(r"\1<\2>", sparql)
        named_query = NamedQuery(
            domain=DOMAIN,
            namespace=query_set.namespace,
            name=name,
            title=name,
            description="",
            url=f"{PDF_URL}#page={query['page']}",
            sparql=sparql,
        )
        query_set.add(named_query)
    return query_set


def main():
    """
    extract the queries and write the query set
    """
    query_set = to_query_set(find_queries(read_lines(fetch_pdf())))
    path = f"query-sets/{query_set.namespace}@{query_set.domain}.yaml"
    query_set.save_to_yaml_file(path)
    print(f"{len(query_set)} queries -> {path}")


if __name__ == "__main__":
    main()
