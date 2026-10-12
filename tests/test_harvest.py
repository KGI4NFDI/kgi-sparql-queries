import unittest

from kgi_example_queries.harvest import harvest_source, load_sources

WIKITEXT = """
== Cats ==
All the cats.
{{SPARQL|query=SELECT ?item WHERE { ?item wdt:P31 wd:Q146. } }}
"""

HTML = """
<div class="mw-parser-output">
<h2><span class="mw-headline" id="Generic_Examples">Generic Examples</span></h2>
<h3><span class="mw-headline" id="Select_All_Triples">Select All Triples</span></h3>
<p>Every triple of the graph.</p>
<div class="mw-highlight mw-highlight-lang-sparql mw-content-ltr" dir="ltr"><pre><span class="k">SELECT</span> * WHERE { ?a ?b ?c }
</pre></div>
<p><a href="//query.example.org/#SELECT">Try it!</a></p>
<h3><span class="mw-headline" id="Select_Q1">Select Q1</span></h3>
<div class="mw-highlight mw-highlight-lang-sparql mw-content-ltr" dir="ltr"><pre>SELECT * WHERE { wd:Q1 ?b ?c }
</pre></div>
</div>
"""


class TestHarvest(unittest.TestCase):
    """
    Test the harvest, offline
    """

    def get_source(self, source_format: str) -> dict:
        """
        get the first source of the manifest with the given format
        """
        sources = [source for source in load_sources() if source["format"] == source_format]
        return sources[0]

    def test_sources(self):
        """
        test that the shipped manifest loads
        """
        sources = load_sources()
        self.assertTrue(len(sources) > 0)
        for source in sources:
            self.assertTrue(source["url"].startswith("https://"), source["id"])
            self.assertIn(source["format"], ["wikitext", "html"], source["id"])

    def test_harvest_wikitext(self):
        """
        test that a wikitext page becomes a snapquery named query set
        """
        query_set = harvest_source(self.get_source("wikitext"), WIKITEXT)
        self.assertEqual(1, len(query_set))
        query = query_set.queries[0]
        self.assertEqual("Cats", query.name)
        self.assertEqual("cats--examples@wikidata.org", query.query_id)
        self.assertIn("wd:Q146", query.sparql)

    def test_harvest_html(self):
        """
        test that a rendered page becomes a snapquery named query set
        """
        source = self.get_source("html")
        query_set = harvest_source(source, HTML)
        self.assertEqual(2, len(query_set))
        query = query_set.queries[0]
        self.assertEqual("Select All Triples", query.name)
        self.assertEqual("SELECT * WHERE { ?a ?b ?c }", query.sparql)
        self.assertEqual("Every triple of the graph.", query.description)
        self.assertEqual(f"{source['url']}#Select_All_Triples", query.url)
        self.assertEqual("", query_set.queries[1].description)
