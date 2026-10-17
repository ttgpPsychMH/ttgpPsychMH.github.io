# Academic CV PDF redesign

This separate PDF change follows the owner-approved website direction. It keeps A4, WeasyPrint, the existing public-safe DOCX include and the publication/project YAML sources. The public output remains `files/Tran_Thien_Gia_Phuoc_Academic_CV.pdf`.

[Open the generated PDF](../../files/Tran_Thien_Gia_Phuoc_Academic_CV.pdf).

Page previews: [1](pages/page-1.png) · [2](pages/page-2.png) · [3](pages/page-3.png) · [4](pages/page-4.png) · [5](pages/page-5.png) · [6](pages/page-6.png).

## Presentation

- Bundled EB Garamond for body and name; compact sans-serif uppercase section headings.
- Black text and clickable links, with no colored panels or rules under every heading.
- Dates aligned in a left column for education, appointments, awards, training and publications.
- Original citation wording, author order/emphasis, corresponding-author markers, DOI links, quartiles and reference years retained.
- Projects grouped with their complete metadata and explanatory text to avoid an isolated final paragraph.
- Page numbers centered in the footer; source paragraph text remains selectable.

The original paged CSS is informed by the inspected Geoff Boeing CV source and representative reference PDF pages. No reference personal content or implementation code is copied. EB Garamond is bundled unmodified under SIL OFL 1.1; see `assets/fonts/cv/OFL.txt` and its source-provenance README. The PDF does not depend on external font downloads at generation time.

## Content and layout validation

The previous PDF had 8 pages; the new public PDF has 6 A4 pages. Page-count reduction comes from typography and spacing, not omitted public content. All six output pages were rendered and visually inspected. No clipped text, overlaps, missing glyphs or empty pages were observed.

The PDF checker verifies the actual artifact, including:

- Every public source paragraph, publication/project IDs and order, all 25 citations and 2 projects.
- Every expected clickable DOI/profile/contact link (24 distinct links in the current document).
- Embedded Garamond fonts, A4 dimensions, page numbering, nonempty pages and text bounding boxes.
- Optional previous-generator paragraph comparison and previous-PDF vocabulary comparison.

Local parity run checked 174 source paragraphs (current source plus previous generator output), including the public-safe generated profile. No previous-PDF terms were lost. No academic YAML or generated profile was changed. The checker is also added to both public PDF generation and site-validation workflows. Regeneration triggers now include the generated profile, config, CSS, fonts, requirements and checker.

```bash
python -m pip install -r scripts/requirements-cv.txt
python scripts/generate_cv_pdf.py
python scripts/validate_cv_pdf.py --render-dir /tmp/cv-pages --report /tmp/cv-report.json
```

For comparison with a retained prior public artifact and generator:

```bash
python scripts/validate_cv_pdf.py \
  --previous-pdf /tmp/cv-before.pdf \
  --previous-generator /tmp/previous-site/scripts/generate_cv_pdf.py
```

The older generator is run with its PDF writer replaced by an HTML capture; its files are not overwritten. Keep the old generator in a temporary website copy so it reads the matching original public include and data.

## Review and automation

The website changes are reviewed separately in PR #21. This PDF branch is independently based on master so either PR can be inspected without mixing unrelated edits. Combined website/PDF behavior is also tested in a temporary fixture. Private DOCX and portrait files are never copied into the public repository, and private workflows/secrets are unchanged.

The new website and PDF are not a production deployment until their PRs are approved and merged. GitHub Actions results must be checked on the actual PR head; local validation does not establish remote CI or Pages deployment.

Additional local checks: the latest DOCX import and synthetic dated-portrait import both regenerated the redesigned PDF and passed PDF validation plus existing website QA. A temporary pagination fixture repeats the existing citations to exercise a 100-record list; no synthetic record is saved to the real YAML or public output. All six actual public PDF pages were visually checked after pagination adjustments.

The 100-record pagination fixture passed on 14 A4 pages, including all source paragraphs, links, font and bounds checks. A negative check with the final page deliberately removed was correctly rejected for missing public content. The combined website/PDF fixture also passed all 30 browser page/viewport checks, theme/menu/storage checks, full website QA and source/previous-PDF parity checks.
