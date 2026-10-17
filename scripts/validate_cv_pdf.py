"""Validate the actual generated public PDF against its public source data."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import unicodedata

from bs4 import BeautifulSoup
import markdown
import pymupdf

from generate_cv_pdf import (
    OUTPUT, build_markdown, load_yaml, PUBLICATIONS_DATA,
    render_document,
)


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text))


def document_text(document: pymupdf.Document) -> str:
    return " ".join(
        block[4]
        for page in document
        for block in page.get_text("blocks")
        if block[1] < page.rect.height - 40
    )


def previous_paragraphs(generator: Path) -> list[str]:
    """Capture an older generator's HTML without changing its output file."""
    spec = importlib.util.spec_from_file_location("previous_cv_generator", generator)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    captured = []

    class CaptureHTML:
        def __init__(self, string: str, **kwargs):
            captured.append(string)

        def write_pdf(self, *args, **kwargs):
            return None

    module.HTML = CaptureHTML
    module.main()
    soup = BeautifulSoup(captured[0], "html.parser")
    return [node.get_text(" ", strip=True) for node in soup.select("p, li")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, default=OUTPUT)
    parser.add_argument("--previous-generator", type=Path)
    parser.add_argument("--previous-pdf", type=Path)
    parser.add_argument("--render-dir", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    errors = []
    records = load_yaml(PUBLICATIONS_DATA)
    projects = load_yaml(PUBLICATIONS_DATA.with_name("projects.yml"))
    source = BeautifulSoup(markdown.markdown(build_markdown(), extensions=["extra", "sane_lists"]), "html.parser")
    expected = [node.get_text(" ", strip=True) for node in source.select("p, li")]
    if args.previous_generator:
        expected.extend(previous_paragraphs(args.previous_generator))
    html = BeautifulSoup(render_document(build_markdown()), "html.parser")
    actual_ids = [node["data-publication-id"] for node in html.select("[data-publication-id]")]
    if actual_ids != [str(record["id"]) for record in records]:
        errors.append("PDF HTML publication IDs/order differ from the shared YAML")
    project_ids = [node["data-project-id"] for node in html.select("[data-project-id]")]
    if project_ids != [str(project["id"]) for project in projects]:
        errors.append("PDF HTML project IDs/order differ from the shared YAML")
    with pymupdf.open(args.pdf) as document:
        if not len(document):
            errors.append("PDF has no pages")
        text = document_text(document)
        if args.previous_pdf:
            with pymupdf.open(args.previous_pdf) as previous:
                tokenize = lambda value: set(re.findall(r"\w+", unicodedata.normalize("NFKC", value).lower()))
                missing = tokenize(document_text(previous)) - tokenize(text)
                if missing:
                    errors.append(f"Terms from the previous PDF are missing: {sorted(missing)}")
        normalized = normalize(text)
        for index, paragraph in enumerate(expected):
            if paragraph and normalize(paragraph) not in normalized:
                errors.append(f"Missing public source paragraph #{index + 1}: {paragraph[:100]}")
        links = {link.get("uri") for page in document for link in page.get_links() if link.get("uri")}
        for anchor in html.select("a[href]"):
            if anchor["href"].startswith(("https://", "mailto:")) and anchor["href"] not in links:
                errors.append(f"Missing clickable link: {anchor['href']}")
        fonts = {font[3] for page in document for font in page.get_fonts()}
        if not any("Garamond" in font for font in fonts):
            errors.append("Bundled Garamond font is not embedded")
        if "\ufffd" in text or "\x00" in text:
            errors.append("PDF contains replacement or null glyphs")
        for index, page in enumerate(document):
            if abs(page.rect.width - 595.276) > 1 or abs(page.rect.height - 841.89) > 1:
                errors.append(f"Page {index + 1} is not A4")
            if len(page.get_text().strip()) < 80:
                errors.append(f"Page {index + 1} is blank or unexpectedly sparse")
            page_number = page.get_text(clip=pymupdf.Rect(0, page.rect.height - 40, page.rect.width, page.rect.height))
            if str(index + 1) not in page_number.split():
                errors.append(f"Page {index + 1} lacks its correct footer number")
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        box = pymupdf.Rect(span["bbox"])
                        if not (pymupdf.Rect(-0.5, -0.5, page.rect.width + 0.5, page.rect.height + 0.5).contains(box)):
                            errors.append(f"Page {index + 1} has text outside its bounds")
            if args.render_dir:
                args.render_dir.mkdir(parents=True, exist_ok=True)
                page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).save(args.render_dir / f"page-{index + 1}.png")
        report = {"pages": len(document), "publications": len(records), "projects": len(projects), "source_paragraphs_checked": len(expected),
                  "clickable_links": len(links), "fonts": sorted(fonts), "errors": errors}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    for error in errors:
        print("FAIL:", error)
    if not errors:
        print(f"PDF QA PASSED: {report['pages']} A4 pages, {len(records)} publications, {len(expected)} public source paragraphs, {len(links)} clickable links.")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
