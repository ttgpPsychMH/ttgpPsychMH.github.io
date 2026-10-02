from __future__ import annotations

from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse, unquote
import json
import sys
import xml.etree.ElementTree as ET
import yaml


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
BASE_URL = "https://ttgppsychmh.github.io"

CORE_PAGES = {
    "index.html": "/",
    "research/index.html": "/research/",
    "publications/index.html": "/publications/",
    "projects/index.html": "/projects/",
    "cv/index.html": "/cv/",
    "contact/index.html": "/contact/",
    "sitemap/index.html": "/sitemap/",
    "404.html": "/404.html",
}

INDEXABLE_PATHS = {
    "/",
    "/research/",
    "/publications/",
    "/projects/",
    "/cv/",
    "/contact/",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def target_for_internal_href(href: str, current_file: Path) -> Path | None:
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None

    parsed = urlparse(href)
    if parsed.scheme in {"http", "https"}:
        if parsed.netloc != "ttgppsychmh.github.io":
            return None
        path = parsed.path
    elif parsed.netloc:
        return None
    else:
        path = parsed.path

    if not path:
        return None

    path = unquote(path)
    if path.startswith("/"):
        relative = path.lstrip("/")
    else:
        relative = str((current_file.parent.relative_to(SITE) / path))

    relative = relative.split("?", 1)[0]
    candidate = SITE / relative

    if path.endswith("/") or candidate.is_dir():
        candidate = candidate / "index.html"
    elif not candidate.suffix:
        candidate = candidate / "index.html"

    return candidate


def validate_page(rel_path: str, expected_path: str, errors: list[str]) -> tuple[str, str]:
    file_path = SITE / rel_path
    if not file_path.exists():
        fail(errors, f"Missing built page: {rel_path}")
        return "", ""

    soup = BeautifulSoup(file_path.read_text(encoding="utf-8"), "html.parser")

    html = soup.find("html")
    if not html or not html.get("lang"):
        fail(errors, f"{rel_path}: missing html lang attribute")

    title = soup.find("title")
    title_text = title.get_text(" ", strip=True) if title else ""
    if not title_text:
        fail(errors, f"{rel_path}: missing page title")

    description = soup.find("meta", attrs={"name": "description"})
    description_text = description.get("content", "").strip() if description else ""
    if len(description_text) < 40:
        fail(errors, f"{rel_path}: missing or weak meta description")

    canonical = soup.find("link", attrs={"rel": lambda v: v and "canonical" in v})
    expected_canonical = BASE_URL + expected_path
    if not canonical or canonical.get("href") != expected_canonical:
        fail(
            errors,
            f"{rel_path}: canonical mismatch; expected {expected_canonical}, "
            f"got {canonical.get('href') if canonical else None}",
        )

    h1s = soup.find_all("h1")
    if len(h1s) != 1:
        fail(errors, f"{rel_path}: expected exactly one H1, found {len(h1s)}")

    skip = soup.find("a", class_="skip-link")
    if not skip or skip.get("href") != "#main":
        fail(errors, f"{rel_path}: missing skip-to-main link")
    if not soup.find(id="main"):
        fail(errors, f"{rel_path}: missing #main target")

    ids = [tag.get("id") for tag in soup.find_all(attrs={"id": True})]
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        fail(errors, f"{rel_path}: duplicate HTML ids: {duplicates}")

    for img in soup.find_all("img"):
        if img.get("alt") is None:
            fail(errors, f"{rel_path}: image missing alt attribute: {img.get('src')}")

    for button in soup.find_all("button"):
        accessible_name = (
            button.get("aria-label")
            or button.get("title")
            or button.get_text(" ", strip=True)
        )
        if not accessible_name:
            fail(errors, f"{rel_path}: button lacks an accessible name")

    required_meta = [
        ("property", "og:title"),
        ("property", "og:description"),
        ("property", "og:type"),
        ("property", "og:url"),
        ("property", "og:image"),
        ("name", "twitter:card"),
        ("name", "twitter:title"),
        ("name", "twitter:description"),
        ("name", "twitter:url"),
        ("name", "twitter:image"),
    ]
    for attr, value in required_meta:
        node = soup.find("meta", attrs={attr: value})
        if not node or not node.get("content", "").strip():
            fail(errors, f"{rel_path}: missing {value} metadata")

    robots = soup.find("meta", attrs={"name": "robots"})
    robots_content = robots.get("content", "").lower() if robots else ""
    if expected_path in INDEXABLE_PATHS and "noindex" in robots_content:
        fail(errors, f"{rel_path}: indexable page is marked noindex")
    if expected_path in {"/404.html", "/sitemap/"} and "noindex" not in robots_content:
        fail(errors, f"{rel_path}: utility page should be noindex")

    # JSON-LD must be parseable wherever present.
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        payload = script.string or script.get_text()
        try:
            json.loads(payload)
        except Exception as exc:
            fail(errors, f"{rel_path}: invalid JSON-LD: {exc}")

    # Check local links reachable in the built site.
    for link in soup.find_all("a", href=True):
        target = target_for_internal_href(link["href"], file_path)
        if target is not None and not target.exists():
            fail(errors, f"{rel_path}: broken internal link {link['href']} -> {target.relative_to(SITE)}")

    return title_text, description_text


def main() -> int:
    errors: list[str] = []
    titles: dict[str, str] = {}
    descriptions: dict[str, str] = {}

    if not SITE.exists():
        print("_site does not exist. Run Jekyll build first.", file=sys.stderr)
        return 2

    for rel_path, expected_path in CORE_PAGES.items():
        title, description = validate_page(rel_path, expected_path, errors)
        if expected_path in INDEXABLE_PATHS:
            if title:
                if title in titles:
                    fail(errors, f"Duplicate core title: {title!r} on {expected_path} and {titles[title]}")
                titles[title] = expected_path
            if description:
                if description in descriptions:
                    fail(
                        errors,
                        f"Duplicate core description on {expected_path} and {descriptions[description]}",
                    )
                descriptions[description] = expected_path

    # Required technical discovery files.
    robots = SITE / "robots.txt"
    if not robots.exists():
        fail(errors, "Missing robots.txt")
    else:
        robots_text = robots.read_text(encoding="utf-8")
        if f"Sitemap: {BASE_URL}/sitemap.xml" not in robots_text:
            fail(errors, "robots.txt does not advertise the canonical XML sitemap")

    sitemap = SITE / "sitemap.xml"
    if not sitemap.exists():
        fail(errors, "Missing sitemap.xml")
    else:
        try:
            root = ET.parse(sitemap).getroot()
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = {node.text for node in root.findall(".//sm:loc", ns)}
            for path in INDEXABLE_PATHS:
                expected = BASE_URL + path
                if expected not in urls:
                    fail(errors, f"XML sitemap missing core URL: {expected}")
        except Exception as exc:
            fail(errors, f"Invalid sitemap.xml: {exc}")

    manifest = SITE / "images" / "manifest.json"
    if not manifest.exists():
        fail(errors, "Missing web manifest")
    else:
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            if data.get("theme_color") != "#9be5dc":
                fail(errors, "Manifest theme_color does not match the site palette")
            if not data.get("name"):
                fail(errors, "Manifest missing site name")
        except Exception as exc:
            fail(errors, f"Invalid manifest JSON: {exc}")

    if not (SITE / "images" / "favicon.svg").exists():
        fail(errors, "Missing SVG favicon")

    # Embedded CV preview must remain available alongside the downloadable PDF.
    cv_file = SITE / "cv" / "index.html"
    if cv_file.exists():
        cv_soup = BeautifulSoup(cv_file.read_text(encoding="utf-8"), "html.parser")
        cv_frame = cv_soup.select_one("iframe.cv-pdf-frame")
        expected_pdf = "/files/Tran_Thien_Gia_Phuoc_Academic_CV.pdf"
        if not cv_frame:
            fail(errors, "CV page is missing the embedded PDF preview")
        elif not cv_frame.get("src", "").startswith(expected_pdf):
            fail(errors, "CV embedded PDF preview points to an unexpected file")
        if not (SITE / "files" / "Tran_Thien_Gia_Phuoc_Academic_CV.pdf").exists():
            fail(errors, "Built site is missing the downloadable academic CV PDF")

    # Publication metric cards must match the structured metadata source.
    publication_data_file = ROOT / "_data" / "publications.yml"
    if not publication_data_file.exists():
        fail(errors, "Missing structured publication metadata")
    else:
        try:
            publication_data = yaml.safe_load(publication_data_file.read_text(encoding="utf-8")) or []
            published = [p for p in publication_data if p.get("status") == "published"]
            expected_stats = {
                "Original Research": sum(p.get("type") == "original_research" for p in published),
                "Conference Papers": sum(p.get("type") == "conference_paper" for p in published),
                "Q1": sum(p.get("quartile") == "Q1" for p in published),
                "Q2": sum(p.get("quartile") == "Q2" for p in published),
                "Q3": sum(p.get("quartile") == "Q3" for p in published),
                "Q4": sum(p.get("quartile") == "Q4" for p in published),
                "SSCI": sum(bool(p.get("ssci")) for p in published),
                "ESCI": sum(bool(p.get("esci")) for p in published),
            }

            publications_file = SITE / "publications" / "index.html"
            if publications_file.exists():
                pub_soup = BeautifulSoup(publications_file.read_text(encoding="utf-8"), "html.parser")
                cards = pub_soup.select(".publication-stat")
                rendered_stats = {}
                for card in cards:
                    label_node = card.select_one(".publication-stat__label")
                    value_node = card.select_one(".publication-stat__value")
                    if label_node and value_node:
                        rendered_stats[label_node.get_text(" ", strip=True)] = int(
                            value_node.get_text(" ", strip=True)
                        )
                if rendered_stats != expected_stats:
                    fail(
                        errors,
                        f"Publication statistics mismatch. Expected {expected_stats}, got {rendered_stats}",
                    )
            else:
                fail(errors, "Missing built Publications page")
        except Exception as exc:
            fail(errors, f"Could not validate publication metadata/statistics: {exc}")

    if errors:
        print("\nTECHNICAL QA FAILED\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print("TECHNICAL QA PASSED")
    print(f"Validated {len(CORE_PAGES)} core/utility pages.")
    print("Checked SEO metadata, canonical URLs, structured data, accessibility structure,")
    print("internal links, robots.txt, sitemap.xml, manifest, and favicon.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
