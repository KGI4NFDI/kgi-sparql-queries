import unittest

from kgi_example_queries.harvest import harvest_source, harvest_wikitext, load_sources

WIKITEXT = """
== Cats ==
All the cats.
{{SPARQL|query=SELECT ?item WHERE { ?item wdt:P31 wd:Q146. } }}
"""

HTML = """
<h2 id="examples">Example queries</h2>
<p>Example 1: all triples.</p>
<pre><code>SELECT * WHERE { ?s ?p ?o }</code></pre>
<p>Example 2: all subjects.</p>
<textarea>SELECT ?s WHERE { ?s ?p &lt;http://example.org/o&gt; }</textarea>
<pre>ex: &lt;http://example.org/&gt;</pre>
<h2>Counting</h2>
<pre>SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }</pre>
"""

SOURCE = {
    "id": "X1",
    "name": "Example",
    "namespace": "example",
    "domain": "example.org",
    "graph": "example",
    "url": "https://example.org/doc",
}


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

    def test_harvest_wikitext(self):
        """
        test that a page becomes a snapquery named query set
        """
        source = load_sources()[0]
        query_set = harvest_wikitext(source, WIKITEXT)
        self.assertEqual(1, len(query_set))
        query = query_set.queries[0]
        self.assertEqual("Cats", query.name)
        self.assertEqual("cats--examples@wikidata.org", query.query_id)
        self.assertIn("wd:Q146", query.sparql)

    def test_harvest_html(self):
        """
        test that an HTML page becomes a snapquery named query set
        """
        query_set = harvest_source(SOURCE, HTML)
        names = [query.name for query in query_set.queries]
        self.assertEqual(["Example queries 1", "Example queries 2", "Counting"], names)
        self.assertEqual("SELECT ?s WHERE { ?s ?p <http://example.org/o> }", query_set.queries[1].sparql)
        self.assertEqual("example-queries-2--example@example.org", query_set.queries[1].query_id)
        self.assertEqual("https://example.org/doc#examples", query_set.queries[0].url)
        self.assertEqual("https://example.org/doc", query_set.queries[2].url)
