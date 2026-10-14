import unittest

import yaml
from snapquery.sparql_analyzer import SparqlAnalyzer

from kgi_example_queries.harvest import harvest_source, load_sources

WIKITEXT = """
== Cats ==
All the cats.
{{SPARQL|query=SELECT ?item WHERE { ?item wdt:P31 wd:Q146. } }}
"""


class TestHarvest(unittest.TestCase):
    """
    Test the harvest, offline
    """

    def test_sources(self):
        """
        test that the shipped manifest loads
        """
        sources = load_sources()
        self.assertTrue(len(sources) > 0)
        for source in sources:
            self.assertTrue(source["url"].startswith("https://"), source["id"])

    def test_harvest_source(self):
        """
        test that a page becomes a snapquery named query set
        """
        source = load_sources()[0]
        query_set = harvest_source(source, WIKITEXT)
        self.assertEqual(1, len(query_set))
        query = query_set.queries[0]
        self.assertEqual("Cats", query.name)
        self.assertEqual("cats--examples@wikidata.org", query.query_id)
        self.assertIn("wd:Q146", query.sparql)

    def test_pinned_sources(self):
        """
        test that the committed query sets of the pinned D3.1 sources are complete
        """
        expected = {"d3.1": 20, "d3.1-stories": 9}
        for source in load_sources():
            if source.get("format") != "pinned":
                continue
            path = f"query-sets/{source['namespace']}@{source['domain']}.yaml"
            with open(path, encoding="utf-8") as yaml_file:
                query_set = yaml.safe_load(yaml_file)
            self.assertEqual(expected[source["namespace"]], len(query_set["queries"]), path)

    def test_pinned_queries_are_valid(self):
        """
        test that every query of the pinned D3.1 sources is valid SPARQL,
        after adding the prefixes it uses without declaring them
        """
        # valid, but a SERVICE inside a SERVICE breaks rdflib's parser:
        # RDFLib/rdflib#2136, fixed by RDFLib/rdflib#3408, not released yet
        known_failures = {"listing-1-9--d3.1-stories@kgi.services.base4nfdi.de"}
        for source in load_sources():
            if source.get("format") != "pinned":
                continue
            path = f"query-sets/{source['namespace']}@{source['domain']}.yaml"
            with open(path, encoding="utf-8") as yaml_file:
                query_set = yaml.safe_load(yaml_file)
            for query in query_set["queries"]:
                if query["query_id"] in known_failures:
                    continue
                sparql = SparqlAnalyzer.add_missing_prefixes(query["sparql"])
                self.assertTrue(SparqlAnalyzer.is_valid(sparql), query["query_id"])
