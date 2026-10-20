import glob
import unittest

import yaml
from snapquery.sparql_analyzer import SparqlAnalyzer


class TestQuerySets(unittest.TestCase):
    """
    Test the committed query sets, offline
    """

    # list every query id on failure, not a truncated diff
    maxDiff = None

    def test_queries_are_valid(self):
        """
        test that every committed query is valid SPARQL, after adding the
        prefixes it uses without declaring them, unless it is listed in
        tests/known_invalid_queries.yaml
        """
        with open("tests/known_invalid_queries.yaml", encoding="utf-8") as yaml_file:
            causes = yaml.safe_load(yaml_file)
        known_invalid = {query_id for cause in causes.values() for query_id in cause["queries"]}
        invalid = set()
        for path in sorted(glob.glob("query-sets/*.yaml")):
            with open(path, encoding="utf-8") as yaml_file:
                query_set = yaml.safe_load(yaml_file)
            for query in query_set["queries"]:
                sparql = SparqlAnalyzer.add_missing_prefixes(query["sparql"])
                if not SparqlAnalyzer.is_valid(sparql):
                    invalid.add(query["query_id"])
        self.assertEqual([], sorted(invalid - known_invalid), "invalid, add to tests/known_invalid_queries.yaml")
        self.assertEqual(
            [], sorted(known_invalid - invalid), "valid or gone, remove from tests/known_invalid_queries.yaml"
        )
