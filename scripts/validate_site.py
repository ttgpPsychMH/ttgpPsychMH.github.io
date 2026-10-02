from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse, unquote
import json
import sys
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
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

PUBLICATION_TYPES = {"original_research", "review", "conference_paper"}
PUBLICATION_STATUSES = {"published", "ongoing"}
SCOPUS_QUARTILES = {"Q1", "Q2", "Q3", "Q4", None, ""}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def load_yaml_list(path: Path, label: str, errors: list[str]) -> list[dict]:
    if not path.exists():
        fail(errors, f"Missing {label} data file: {path.relative_to(ROOT)}")
        return []

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    except Exception as exc:
        fail(errors, f"Invalid {label} YAML: {exc}")
        return []

    if not isinstance(data, list):
        fail(errors, f"{label} data must be a YAML list")
        return []

    if not all(isinstance(item, dict) for item in data):
        fail(errors, f"Every {label} entry must be a mapping/object")
        return []

    return data


def validate_unique_ids(
    records: list[dict],
    label: str,
    errors: list[str],
) -> None:
    ids = [str(item.get("id", "")).strip() for item in records]
    if any(not value for value in ids):
        fail(errors, f"{label} data contains an entry without an id")
        return

    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        fail(errors, f"{label} data contains duplicate ids: {duplicates}")


def selected_records(records: list[dict], label: str, errors: list[str]) -> list[dict]:
    selected = [item for item in records if item.get("selected") is True]

    orders = []
    for item in selected:
        order = item.get("selected_order")
        if not isinstance(order, int):
            fail(
                errors,
                f"{label} selected item {item.get('id')} must have an integer selected_order",
            )
            continue
        orders.append(order)

    duplicates = sorted({value for value in orders if orders.count(value) > 1})
    if duplicates:
        fail(errors, f"{label} selected_order values are duplicated: {duplicates}")

    return sorted(
        selected,
        key=lambda item: item.get("selected_order", 10**9),
    )


def validate_publication_data(
    publications: list[dict],
    errors: list[str],
) -> None:
    validate_unique_ids(publications, "Publication", errors)

    for pub in publications:
        pub_id = pub.get("id", "<unknown>")

        if pub.get("status") not in PUBLICATION_STATUSES:
            fail(errors, f"Publication {pub_id}: invalid status {pub.get('status')!r}")

        if pub.get("type") not in PUBLICATION_TYPES:
            fail(errors, f"Publication {pub_id}: invalid type {pub.get('type')!r}")

        if not str(pub.get("citation", "")).strip():
            fail(errors, f"Publication {pub_id}: citation is required")

        if pub.get("status") == "published" and not pub.get("year"):
            fail(errors, f"Publication {pub_id}: published entries require a year")

        if pub.get("scopus_quartile") not in SCOPUS_QUARTILES:
            fail(
                errors,
                f"Publication {pub_id}: invalid Scopus quartile "
                f"{pub.get('scopus_quartile')!r}",
            )

        doi = pub.get("doi")
        if doi and not str(doi).startswith("https://doi.org/"):
            fail(errors, f"Publication {pub_id}: DOI must use https://doi.org/")

    selected_records(publications, "Publication", errors)


def validate_project_data(projects: list[dict], errors: list[str]) -> None:
    validate_unique_ids(projects, "Project", errors)

    required = {
        "title",
        "period",
        "status",
        "role",
        "institution",
        "project_type",
        "project_code",
        "principal_investigator",
        "funding_vnd",
        "funding_usd",
        "outcome",
    }

    for project in projects:
        project_id = project.get("id", "<unknown>")
        missing = sorted(
            key for key in required if not str(project.get(key, "")).strip()
        )
        if missing:
            fail(errors, f"Project {project_id}: missing required fields {missing}")

    selected_records(projects, "Project", errors)


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


def validate_page(
    rel_path: str,
    expected_path: str,
    errors: list[str],
) -> tuple[str, str]:
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

    canonical = soup.find(
        "link",
        attrs={"rel": lambda value: value and "canonical" in value},
    )
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

    primary_nav = soup.select_one("nav.site-nav")
    if not primary_nav:
        fail(errors, f"{rel_path}: missing dedicated primary navigation")
    else:
        nav_hrefs = set()
        for anchor in primary_nav.find_all("a", href=True):
            href = anchor.get("href", "")
            parsed = urlparse(href)
            if (
                parsed.scheme in {"http", "https"}
                and parsed.netloc == "ttgppsychmh.github.io"
            ):
                nav_hrefs.add(parsed.path or "/")
            elif not parsed.scheme and not parsed.netloc:
                nav_hrefs.add(parsed.path or "/")

        expected_nav = {
            "/",
            "/research/",
            "/publications/",
            "/projects/",
            "/cv/",
            "/contact/",
        }
        missing_nav = expected_nav - nav_hrefs
        if missing_nav:
            fail(errors, f"{rel_path}: primary navigation missing {sorted(missing_nav)}")

        current_links = primary_nav.select('[aria-current="page"]')
        if expected_path in INDEXABLE_PATHS and len(current_links) != 1:
            fail(
                errors,
                f"{rel_path}: expected exactly one current-page navigation link, "
                f"found {len(current_links)}",
            )

        nav_toggle = primary_nav.select_one("#site-nav-toggle")
        if not nav_toggle or nav_toggle.get("aria-controls") != "site-nav-links":
            fail(
                errors,
                f"{rel_path}: responsive navigation toggle is missing or malformed",
            )

    script_sources = [
        script.get("src", "")
        for script in soup.find_all("script", src=True)
    ]
    if any("main.min.js" in source for source in script_sources):
        fail(errors, f"{rel_path}: legacy Academic Pages runtime is loaded")
    if not any("custom-ui.js" in source for source in script_sources):
        fail(errors, f"{rel_path}: custom-ui.js runtime is missing")

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

    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        payload = script.string or script.get_text()
        try:
            json.loads(payload)
        except Exception as exc:
            fail(errors, f"{rel_path}: invalid JSON-LD: {exc}")

    for link in soup.find_all("a", href=True):
        target = target_for_internal_href(link["href"], file_path)
        if target is not None and not target.exists():
            fail(
                errors,
                f"{rel_path}: broken internal link {link['href']} "
                f"-> {target.relative_to(SITE)}",
            )

    return title_text, description_text


def rendered_ids(soup: BeautifulSoup, selector: str, attribute: str) -> list[str]:
    return [
        str(node.get(attribute, "")).strip()
        for node in soup.select(selector)
    ]


def main() -> int:
    errors: list[str] = []
    titles: dict[str, str] = {}
    descriptions: dict[str, str] = {}

    if not SITE.exists():
        print("_site does not exist. Run Jekyll build first.", file=sys.stderr)
        return 2

    publications = load_yaml_list(
        ROOT / "_data" / "publications.yml",
        "Publication",
        errors,
    )
    projects = load_yaml_list(
        ROOT / "_data" / "projects.yml",
        "Project",
        errors,
    )
    validate_publication_data(publications, errors)
    validate_project_data(projects, errors)

    for rel_path, expected_path in CORE_PAGES.items():
        title, description = validate_page(rel_path, expected_path, errors)
        if expected_path in INDEXABLE_PATHS:
            if title:
                if title in titles:
                    fail(
                        errors,
                        f"Duplicate core title: {title!r} on {expected_path} "
                        f"and {titles[title]}",
                    )
                titles[title] = expected_path
            if description:
                if description in descriptions:
                    fail(
                        errors,
                        f"Duplicate core description on {expected_path} "
                        f"and {descriptions[description]}",
                    )
                descriptions[description] = expected_path

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

    home_file = SITE / "index.html"
    if home_file.exists():
        home_soup = BeautifulSoup(
            home_file.read_text(encoding="utf-8"),
            "html.parser",
        )

        selected_pub_data = selected_records(publications, "Publication", errors)
        expected_pub_ids = [str(item["id"]) for item in selected_pub_data]
        actual_pub_ids = rendered_ids(
            home_soup,
            ".selected-publications [data-publication-id]",
            "data-publication-id",
        )
        if actual_pub_ids != expected_pub_ids:
            fail(
                errors,
                f"Homepage selected publications mismatch. "
                f"Expected {expected_pub_ids}, got {actual_pub_ids}",
            )

        selected_pub_nodes = home_soup.select(
            ".selected-publications [data-publication-id]"
        )
        for pub, node in zip(selected_pub_data, selected_pub_nodes):
            if "</strong>" in node.get_text(" ", strip=True):
                fail(
                    errors,
                    f"Selected publication {pub['id']} exposes raw strong-tag text",
                )
            if not node.find("strong"):
                fail(
                    errors,
                    f"Selected publication {pub['id']} must emphasize the site author",
                )
            if pub.get("doi"):
                doi = str(pub["doi"])
                doi_link = node.find("a", href=doi)
                if not doi_link or doi_link.get_text(" ", strip=True) != doi:
                    fail(
                        errors,
                        f"Selected publication {pub['id']} must show its full DOI URL",
                    )
            if "SCOPUS Q" in node.get_text(" ", strip=True):
                fail(
                    errors,
                    f"Selected publication {pub['id']} should not display quartile metadata",
                )

        selected_project_data = selected_records(projects, "Project", errors)
        expected_project_ids = [
            str(item["id"]) for item in selected_project_data
        ]
        actual_project_ids = rendered_ids(
            home_soup,
            ".selected-projects [data-project-id]",
            "data-project-id",
        )
        if actual_project_ids != expected_project_ids:
            fail(
                errors,
                f"Homepage selected projects mismatch. "
                f"Expected {expected_project_ids}, got {actual_project_ids}",
            )

    publications_file = SITE / "publications" / "index.html"
    if publications_file.exists():
        pub_soup = BeautifulSoup(
            publications_file.read_text(encoding="utf-8"),
            "html.parser",
        )
        expected_ids = [str(item["id"]) for item in publications]
        actual_ids = rendered_ids(
            pub_soup,
            "article.publication-card[data-publication-id]",
            "data-publication-id",
        )
        if actual_ids != expected_ids:
            fail(
                errors,
                f"Publications page records mismatch. "
                f"Expected {expected_ids}, got {actual_ids}",
            )

        published = [p for p in publications if p.get("status") == "published"]
        expected_stats = {
            "Original Research": sum(
                p.get("type") == "original_research" for p in published
            ),
            "Conference Papers": sum(
                p.get("type") == "conference_paper" for p in published
            ),
            "SCOPUS Q1": sum(
                p.get("scopus_quartile") == "Q1" for p in published
            ),
            "SCOPUS Q2": sum(
                p.get("scopus_quartile") == "Q2" for p in published
            ),
            "SCOPUS Q3": sum(
                p.get("scopus_quartile") == "Q3" for p in published
            ),
            "SCOPUS Q4": sum(
                p.get("scopus_quartile") == "Q4" for p in published
            ),
            "SSCI": sum(bool(p.get("ssci")) for p in published),
            "ESCI": sum(bool(p.get("esci")) for p in published),
        }

        rendered_stats = {}
        for card in pub_soup.select(".publication-stat"):
            label_node = card.select_one(".publication-stat__label")
            value_node = card.select_one(".publication-stat__value")
            if label_node and value_node:
                rendered_stats[label_node.get_text(" ", strip=True)] = int(
                    value_node.get_text(" ", strip=True)
                )

        if rendered_stats != expected_stats:
            fail(
                errors,
                f"Publication statistics mismatch. "
                f"Expected {expected_stats}, got {rendered_stats}",
            )

    projects_file = SITE / "projects" / "index.html"
    if projects_file.exists():
        project_soup = BeautifulSoup(
            projects_file.read_text(encoding="utf-8"),
            "html.parser",
        )
        expected_ids = [str(item["id"]) for item in projects]
        actual_ids = rendered_ids(
            project_soup,
            "section.project-card[data-project-id]",
            "data-project-id",
        )
        if actual_ids != expected_ids:
            fail(
                errors,
                f"Projects page records mismatch. "
                f"Expected {expected_ids}, got {actual_ids}",
            )

    cv_file = SITE / "cv" / "index.html"
    if cv_file.exists():
        cv_soup = BeautifulSoup(
            cv_file.read_text(encoding="utf-8"),
            "html.parser",
        )
        cv_frame = cv_soup.select_one("iframe.cv-pdf-frame")
        expected_pdf = "/files/Tran_Thien_Gia_Phuoc_Academic_CV.pdf"

        if not cv_frame:
            fail(errors, "CV page is missing the embedded PDF preview")
        elif not cv_frame.get("src", "").startswith(expected_pdf):
            fail(errors, "CV embedded PDF preview points to an unexpected file")

        if cv_frame and cv_frame.get("loading") != "lazy":
            fail(errors, "CV embedded PDF preview should be lazy-loaded")

        cv_publication_ids = rendered_ids(
            cv_soup,
            ".cv-reference[data-publication-id]",
            "data-publication-id",
        )
        expected_publication_ids = [str(item["id"]) for item in publications]
        if cv_publication_ids != expected_publication_ids:
            fail(
                errors,
                f"CV publication records mismatch. "
                f"Expected {expected_publication_ids}, got {cv_publication_ids}",
            )

        cv_project_ids = rendered_ids(
            cv_soup,
            ".cv-project[data-project-id]",
            "data-project-id",
        )
        expected_project_ids = [str(item["id"]) for item in projects]
        if cv_project_ids != expected_project_ids:
            fail(
                errors,
                f"CV project records mismatch. "
                f"Expected {expected_project_ids}, got {cv_project_ids}",
            )

    pdf_file = SITE / "files" / "Tran_Thien_Gia_Phuoc_Academic_CV.pdf"
    if not pdf_file.exists():
        fail(errors, "Built site is missing the downloadable academic CV PDF")
    elif pdf_file.stat().st_size < 10_000:
        fail(errors, "Generated academic CV PDF is unexpectedly small")

    if errors:
        print("\nTECHNICAL QA FAILED\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print("TECHNICAL QA PASSED")
    print(f"Validated {len(CORE_PAGES)} core/utility pages.")
    print(
        "Checked shared publication/project data, cross-page rendering, CV/PDF "
        "generation, SEO metadata, structured data, accessibility, links, "
        "robots.txt, sitemap.xml, manifest, and favicon."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
