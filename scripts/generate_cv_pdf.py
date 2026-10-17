from pathlib import Path
from datetime import date
from html import escape
import re

import markdown
import yaml
from bs4 import BeautifulSoup
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_pages" / "cv.md"
PUBLICATIONS_DATA = ROOT / "_data" / "publications.yml"
PROJECTS_DATA = ROOT / "_data" / "projects.yml"
OUTPUT = ROOT / "files" / "Tran_Thien_Gia_Phuoc_Academic_CV.pdf"
STYLESHEET = ROOT / "assets" / "css" / "cv-pdf.css"


def strip_front_matter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2].lstrip()
    return text


def load_yaml(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a YAML list.")
    return data


def publication_meta(pub: dict, ongoing: bool = False) -> str:
    parts: list[str] = []
    if ongoing:
        parts.append("Status: Ongoing")
    if pub.get("ssci"):
        parts.append("SSCI")
    if pub.get("esci"):
        parts.append("ESCI")
    if pub.get("scopus_quartile"):
        quartile = f"SCOPUS {pub['scopus_quartile']}"
        if pub.get("scopus_quartile_year"):
            quartile += f" ({pub['scopus_quartile_year']})"
        parts.append(quartile)
    return " · ".join(parts)


def render_publication(pub: dict, ongoing: bool = False) -> str:
    """Format one shared citation without changing author order or markers."""
    citation = markdown.markdown(str(pub.get("citation", "")).strip())
    year = escape(str(pub.get("year", "")))
    identifier = escape(str(pub["id"]), quote=True)
    details = []
    if pub.get("doi"):
        doi = escape(str(pub["doi"]).strip(), quote=True)
        details.append(f'<p class="cv-publication-doi"><a href="{doi}">{doi}</a></p>')
    metadata = publication_meta(pub, ongoing=ongoing)
    if metadata:
        details.append(f'<p class="cv-publication-meta">{escape(metadata)}</p>')
    return (
        f'<div class="cv-publication" data-publication-id="{identifier}">'
        f'<div class="cv-date">{year}</div><div class="cv-entry">'
        f'<div class="cv-citation">{citation}</div>{"".join(details)}</div></div>'
    )


def render_publications_markdown(publications: list[dict]) -> str:
    groups = [
        ("Ongoing Work", [p for p in publications if p.get("status") == "ongoing"], True),
        ("Peer-Reviewed Journal Articles", [p for p in publications
          if p.get("status") == "published" and p.get("type") != "conference_paper"], False),
        ("Conference Papers", [p for p in publications
          if p.get("status") == "published" and p.get("type") == "conference_paper"], False),
    ]
    lines = []
    for heading, records, ongoing in groups:
        if records:
            lines.extend([f"### {heading}", ""])
            for record in records:
                lines.extend([render_publication(record, ongoing=ongoing), ""])
    return "\n".join(lines).strip()


def render_projects_markdown(projects: list[dict]) -> str:
    lines: list[str] = []

    for project in projects:
        lines.extend(
            [
                f'<section class="cv-project" data-project-id="{escape(str(project["id"]), quote=True)}" markdown="1">',
                "",
                f"### {project['title']}",
                "",
                f"**Period:** {project['period']} [{project['status']}]  ",
                f"**Role:** {project['role']}  ",
                f"**Project type:** {project['project_type']}  ",
                f"**Project code:** {project['project_code']}  ",
                f"**Institution:** {project['institution']}  ",
                f"**Principal Investigator:** {project['principal_investigator']}  ",
                f"**Funding:** {project['funding_vnd']} ({project['funding_usd']})  ",
                f"**Outcome:** {project['outcome']}",
                "",
            ]
        )
        if project.get("details"):
            lines.extend([str(project["details"]).strip(), ""])
        lines.extend(["</section>", ""])

    return "\n".join(lines).strip()


def replace_data_block(text: str, name: str, replacement: str) -> str:
    pattern = (
        rf"<!-- CV_{name}_START -->"
        rf".*?"
        rf"<!-- CV_{name}_END -->"
    )
    updated, count = re.subn(
        pattern,
        replacement,
        text,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise ValueError(f"Could not find exactly one CV_{name} data block.")
    return updated


def build_markdown() -> str:
    """Expand the existing public-safe include and shared records."""
    text = SOURCE.read_text(encoding="utf-8")
    text = strip_front_matter(text)

    # PDF rendering does not execute Jekyll: expand the shared date token only.
    date_token = '{{ site.data.cv_sync_state.cv_date | date: "%-d %B %Y" }}'
    if date_token in text:
        state = yaml.safe_load((ROOT / "_data" / "cv_sync_state.yml").read_text(encoding="utf-8"))
        stamp = date.fromisoformat(str(state["cv_date"]))
        text = text.replace(date_token, stamp.strftime("%-d %B %Y"))

    publications = load_yaml(PUBLICATIONS_DATA)
    projects = load_yaml(PROJECTS_DATA)

    # Website-only controls and the embedded PDF viewer should not be rendered
    # inside the generated PDF itself.
    text = re.sub(
        r'<div class="cv-actions">.*?</div>\s*',
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'## PDF Preview\s*<div class="cv-pdf-viewer">.*?</div>\s*## Web CV\s*',
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"\[Download public academic CV \(PDF\)\]\([^\n]+\)\s*",
        "",
        text,
        count=1,
    )

    # Shared public-safe DOCX profile: expand the Jekyll include for PDF rendering.
    profile_include = ROOT / "_includes" / "generated_cv_profile.md"
    include_tag = "{% include generated_cv_profile.md %}"
    if include_tag in text:
        if not profile_include.exists():
            raise ValueError("Missing generated CV profile include.")
        text = text.replace(
            include_tag,
            profile_include.read_text(encoding="utf-8").strip(),
            1,
        )

    # Liquid blocks on the web CV are replaced with Markdown generated from
    # the same YAML data sources before the PDF is rendered.
    text = replace_data_block(
        text,
        "PUBLICATIONS",
        render_publications_markdown(publications),
    )
    text = replace_data_block(
        text,
        "PROJECTS",
        render_projects_markdown(projects),
    )

    return text


def render_document(text: str) -> str:
    body = BeautifulSoup(markdown.markdown(text, extensions=["extra", "sane_lists"]), "html.parser")
    # Imported paragraphs retain all their original text and inline markup.
    # Only paragraphs with an explicit leading date are laid out in two columns.
    date_pattern = re.compile(
        r"^(?:\d{4}(?:\s|$)|(?:January|February|March|April|May|June|July|August|September|October|November|December)\b)"
    )
    for paragraph in list(body.find_all("p")):
        first_break = paragraph.find("br", recursive=False)
        if not first_break or paragraph.find_parent(class_="cv-publication"):
            continue
        first_line = "".join(str(node.get_text() if hasattr(node, "get_text") else node)
                             for node in list(paragraph.contents)[:paragraph.contents.index(first_break)]).strip()
        if not date_pattern.match(first_line):
            continue
        wrapper = body.new_tag("div", attrs={"class": "cv-dated"})
        date_cell = body.new_tag("div", attrs={"class": "cv-date"})
        for node in list(paragraph.contents):
            if node is first_break:
                break
            date_cell.append(node.extract())
        first_break.decompose()
        title = body.new_tag("span", attrs={"class": "cv-entry-title"})
        for node in list(paragraph.contents):
            if getattr(node, "name", None) == "br":
                break
            title.append(node.extract())
        paragraph.insert(0, title)
        entry = body.new_tag("div", attrs={"class": "cv-entry"})
        paragraph.replace_with(wrapper)
        entry.append(paragraph)
        wrapper.extend([date_cell, entry])

    config = yaml.safe_load((ROOT / "_config.yml").read_text(encoding="utf-8"))
    name = escape(str(config["name"]))
    email = escape(str(config["author"]["email"]), quote=True)
    website = escape(str(config["url"]), quote=True)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{name}: Academic Curriculum Vitae</title>
<meta name="author" content="{name}">
</head><body>
<header class="cv-header"><h1>{name}</h1>
<div class="cv-header-details"><div class="cv-document-label">Academic Curriculum Vitae</div>
<div class="cv-contact"><a href="mailto:{email}">{email}</a><br>
<a href="{website}">{website.removeprefix('https://')}</a></div></div></header>
<main>{body}</main>
</body></html>"""


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = render_document(build_markdown())
    fonts = FontConfiguration()
    HTML(string=document, base_url=str(ROOT)).write_pdf(
        str(OUTPUT), stylesheets=[CSS(filename=str(STYLESHEET), font_config=fonts)],
        font_config=fonts
    )


if __name__ == "__main__":
    main()
