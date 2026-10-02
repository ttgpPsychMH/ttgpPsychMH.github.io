from pathlib import Path
import re

import markdown
import yaml
from weasyprint import HTML


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_pages" / "cv.md"
PUBLICATIONS_DATA = ROOT / "_data" / "publications.yml"
PROJECTS_DATA = ROOT / "_data" / "projects.yml"
OUTPUT = ROOT / "files" / "Tran_Thien_Gia_Phuoc_Academic_CV.pdf"


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


def render_publications_markdown(publications: list[dict]) -> str:
    lines: list[str] = []

    ongoing = [p for p in publications if p.get("status") == "ongoing"]
    if ongoing:
        lines.extend(["### Ongoing Work", ""])
        for pub in ongoing:
            lines.extend([str(pub.get("citation", "")).strip(), ""])
            if pub.get("doi"):
                doi = str(pub["doi"]).strip()
                lines.extend([f"[{doi}]({doi})", ""])
            meta = publication_meta(pub, ongoing=True)
            if meta:
                lines.extend([f"*{meta}*", ""])

    published = [p for p in publications if p.get("status") == "published"]
    journal_articles = [
        p for p in published if p.get("type") != "conference_paper"
    ]

    if journal_articles:
        lines.extend(["### Peer-Reviewed Journal Articles", ""])
        last_year = None
        for pub in journal_articles:
            year = pub.get("year")
            if year != last_year:
                lines.extend([f"#### {year}", ""])
                last_year = year

            lines.extend([str(pub.get("citation", "")).strip(), ""])
            if pub.get("doi"):
                doi = str(pub["doi"]).strip()
                lines.extend([f"[{doi}]({doi})", ""])
            meta = publication_meta(pub)
            if meta:
                lines.extend([f"*{meta}*", ""])

    conference_papers = [
        p for p in published if p.get("type") == "conference_paper"
    ]
    if conference_papers:
        lines.extend(["### Conference Papers", ""])
        for pub in conference_papers:
            lines.extend([str(pub.get("citation", "")).strip(), ""])

    return "\n".join(lines).strip()


def render_projects_markdown(projects: list[dict]) -> str:
    lines: list[str] = []

    for project in projects:
        lines.extend(
            [
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


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    text = strip_front_matter(text)

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

    body = markdown.markdown(text, extensions=["extra", "sane_lists"])

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4;
    margin: 18mm 18mm 20mm 18mm;
    @bottom-center {{
      content: "Tran Thien Gia Phuoc · Academic CV · " counter(page);
      font-size: 8pt;
      color: #777;
    }}
  }}
  body {{
    font-family: "DejaVu Sans", Arial, sans-serif;
    color: #222;
    font-size: 10.5pt;
    line-height: 1.46;
  }}
  h1 {{
    font-size: 22pt;
    margin: 0 0 12pt;
    color: #347f76;
  }}
  h2 {{
    font-size: 14pt;
    margin: 18pt 0 7pt;
    padding-bottom: 3pt;
    border-bottom: 0.7pt solid #777;
    color: #725c86;
  }}
  h3 {{
    font-size: 11.5pt;
    margin: 12pt 0 4pt;
  }}
  h4 {{
    font-size: 10.5pt;
    margin: 9pt 0 3pt;
    color: #555;
  }}
  p {{
    margin: 0 0 7pt;
  }}
  ul {{
    margin-top: 3pt;
    margin-bottom: 8pt;
    padding-left: 18pt;
  }}
  li {{
    margin-bottom: 3pt;
  }}
  a {{
    color: #347f76;
    text-decoration: none;
  }}
  strong {{
    font-weight: 700;
  }}
</style>
</head>
<body>
<h1>Tran Thien Gia Phuoc</h1>
{body}
</body>
</html>"""

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html, base_url=str(ROOT)).write_pdf(str(OUTPUT))


if __name__ == "__main__":
    main()
