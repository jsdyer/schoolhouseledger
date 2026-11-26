import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from html import unescape
from urllib.parse import urlencode
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build import ROOT, build, metadata


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / "web", self.root / "web")
        shutil.copyfile(ROOT / "tool.json", self.root / "tool.json")
        shutil.copyfile(ROOT / "README.md", self.root / "README.md")

    def edit(self, **changes):
        tool = json.loads((self.root / "tool.json").read_text())
        tool.update(changes)
        (self.root / "tool.json").write_text(json.dumps(tool))

    def test_build_is_scoped_to_web_and_escapes_metadata(self):
        (self.root / "private.txt").write_text("must not publish")
        self.edit(title='<img src=x onerror="bad()">')
        build(self.root)
        page = (self.root / "dist/index.html").read_text()
        self.assertIn('&lt;img', page)
        self.assertNotIn('<img', page)
        self.assertNotIn('{{', page)
        self.assertIn('href="./style.css"', page)
        self.assertFalse((self.root / "dist/private.txt").exists())
        self.assertTrue((self.root / "dist/.nojekyll").exists())

    def test_school_sitemap_contains_only_documented_linked_histories(self):
        build(self.root)
        site = self.root / "dist"
        entry = (site / "index.html").read_text()
        data = json.loads((site / "data/edition.json").read_text())
        sitemap = ET.parse(site / "sitemap.xml")
        urls = {node.text for node in sitemap.findall(".//{*}loc")}
        self.assertEqual(len(urls), 1 + len(data["schools"]))
        self.assertIn("https://coolcode.ca/schoolhouseledger/schools/", urls)
        directory = (site / "schools/index.html").read_text()
        self.assertIn('href="./schools/"', entry)
        self.assertIn('rel="canonical" href="https://coolcode.ca/schoolhouseledger/schools/"', directory)
        self.assertEqual(directory.count('<th scope="row">'), len(data["schools"]))
        for name, school in data["schools"].items():
            slug = name.replace(", ", "-").replace(" ", "-").lower()
            path = f"schools/{slug}/"
            url = "https://coolcode.ca/schoolhouseledger/" + path
            page = (site / path / "index.html").read_text()
            self.assertIn(url, urls)
            self.assertIn(f'href="../{path}"', directory)
            self.assertIn('href="../">Browse all school histories', page)
            self.assertIn(f'href="./{path}"', entry)
            self.assertIn(f'rel="canonical" href="{url}"', page)
            self.assertIn(f'{data["source"]}#page={school["page"]}', page)
            self.assertEqual(page.count('<th scope="row">'), len(school["years"]))
            for year, figures in school["years"].items():
                self.assertIn("../../#" + urlencode({"school": name, "year": year}), unescape(page))
                self.assertIn(f'<td>{figures["enrolled"]:,}</td><td>{figures["daily"]:.2f}</td>', page)
        port = (site / "schools/port-kells/index.html").read_text()
        self.assertNotIn("1889–90", port)
        self.assertIn("annual school expenditure of $640", port)

    def test_url_matches_tool_id(self):
        self.edit(url="/different/")
        with self.assertRaises(ValueError): metadata(self.root)

    def test_requires_a_source_sentence_and_a_guide_note(self):
        (self.root / "README.md").write_text("# A tool")
        with self.assertRaisesRegex(ValueError, "README note"):
            metadata(self.root)
        self.edit(data_info={"mode": "local", "detail": ""})
        with self.assertRaisesRegex(ValueError, "homepage card"):
            metadata(self.root)

    def test_browser_access_is_explicit(self):
        self.edit(access="install")
        with self.assertRaisesRegex(ValueError, "immediately usable"):
            metadata(self.root)

    def test_failed_build_keeps_existing_output(self):
        build(self.root)
        existing = (self.root / "dist/index.html").read_bytes()
        self.edit(source="javascript:bad()")
        with self.assertRaises(ValueError): build(self.root)
        self.assertEqual((self.root / "dist/index.html").read_bytes(), existing)


if __name__ == "__main__": unittest.main()
