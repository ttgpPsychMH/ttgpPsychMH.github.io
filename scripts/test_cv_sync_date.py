"""Exercise a future sync-state date through both public renderers, in /tmp."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from bs4 import BeautifulSoup
import pymupdf
import yaml


ROOT = Path(__file__).resolve().parents[1]


class CVSyncDateTest(unittest.TestCase):
    def test_state_only_update_reaches_web_and_pdf(self):
        # ruby/setup-ruby stores this path in project-local .bundle/config.
        # Reuse only the gem path; leave other local configuration out of /tmp.
        environment = os.environ.copy()
        bundle_path = subprocess.check_output(
            ["bundle", "exec", "ruby", "-rbundler", "-e", "puts Bundler.settings[:path]"],
            cwd=ROOT, text=True,
        ).strip()
        if bundle_path:
            environment["BUNDLE_PATH"] = str((ROOT / bundle_path).resolve())
        with tempfile.TemporaryDirectory(prefix="cv-date-") as temporary:
            fixture = Path(temporary) / "site"
            shutil.copytree(
                ROOT, fixture,
                ignore=shutil.ignore_patterns(
                    ".git", "_site", ".bundle", ".jekyll-cache",
                    ".sass-cache", "__pycache__", "local",
                ),
            )
            template = fixture / "_pages/cv.md"
            original_template = template.read_bytes()
            state_path = fixture / "_data/cv_sync_state.yml"
            state = yaml.safe_load(state_path.read_text(encoding="utf-8"))
            state["cv_date"] = "2027-01-09"
            state_path.write_text(yaml.safe_dump(state), encoding="utf-8")

            for command in (
                [sys.executable, "scripts/generate_cv_pdf.py"],
                [sys.executable, "scripts/validate_cv_pdf.py"],
                ["bundle", "exec", "jekyll", "build", "--trace"],
                [sys.executable, "scripts/validate_site.py"],
            ):
                subprocess.run(command, cwd=fixture, env=environment, check=True)

            soup = BeautifulSoup(
                (fixture / "_site/cv/index.html").read_text(encoding="utf-8"),
                "html.parser",
            )
            self.assertIn("9 January 2027", soup.select_one("#web-cv + p").get_text())
            with pymupdf.open(fixture / "files/Tran_Thien_Gia_Phuoc_Academic_CV.pdf") as pdf:
                text = " ".join(page.get_text() for page in pdf)
            self.assertIn("9 January 2027", text)
            self.assertNotIn("site.data.cv_sync_state", text)
            self.assertEqual(original_template, template.read_bytes())


if __name__ == "__main__":
    unittest.main()
