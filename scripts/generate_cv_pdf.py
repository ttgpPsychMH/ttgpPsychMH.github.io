from pathlib import Path
import re

import markdown
from weasyprint import HTML


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_pages" / "cv.md"
OUTPUT = ROOT / "files" / "Tran_Thien_Gia_Phuoc_Academic_CV.pdf"


def strip_front_matter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2].lstrip()
    return text


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    text = strip_front_matter(text)

    # The PDF should not contain the website's "download this PDF" action.
    text = re.sub(
        r"<a class=\"btn cv-download\"[^>]*>.*?</a>\s*",
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
