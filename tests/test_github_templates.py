import glob
import unittest

import yaml


class TestGithubTemplates(unittest.TestCase):
    """
    Test the issue and pull request templates in .github, offline
    """

    def read_issue_templates(self) -> dict:
        """
        read every issue template as its front matter and its body
        """
        templates = {}
        for path in sorted(glob.glob(".github/ISSUE_TEMPLATE/*.md")):
            with open(path, encoding="utf-8") as template_file:
                text = template_file.read()
            _, front_matter, body = text.split("---\n", 2)
            templates[path] = (yaml.safe_load(front_matter), body)
        return templates

    def test_issue_templates_have_front_matter(self):
        """
        test that every issue template has the name and about fields GitHub
        needs to offer it when a new issue is opened
        """
        templates = self.read_issue_templates()
        self.assertEqual(3, len(templates))
        for path, (front_matter, _) in templates.items():
            for key in ("name", "about"):
                self.assertTrue(front_matter.get(key), f"{path}: {key} missing")

    def test_issue_templates_ask_for_acceptance_criteria(self):
        """
        test that the standard and the epic template ask for acceptance criteria
        """
        templates = self.read_issue_templates()
        for path in (".github/ISSUE_TEMPLATE/KGI_standard_issue.md", ".github/ISSUE_TEMPLATE/KGI_epic.md"):
            _, body = templates[path]
            self.assertIn("acceptance criteria", body.lower().replace("-", " "), path)

    def test_pull_request_template_links_an_issue(self):
        """
        test that the pull request template has the line that closes the
        linked issue when the pull request is merged
        """
        with open(".github/pull_request_template.md", encoding="utf-8") as template_file:
            lines = template_file.read().splitlines()
        self.assertIn("Closes #", lines)
