# Academic editorial redesign — audit and Phase 1 specification

## Scope and evidence

Baseline: `master` at `bfd31751f0858f46c64969e9864247f50a336c59`; fetched origin/master and confirmed no divergence before branching. Phase 1 branch: `design/academic-editorial-homepage`. The owner must approve the prototype before a production merge or the full page/PDF redesign.

The live reference initially returned a network-proxy CONNECT 403. Access subsequently succeeded after the required reference hosts were saved to the environment draft. Direct Chromium observation (trusted environment CA imported into a dedicated NSS profile; TLS verification retained) and downloaded public CSS confirmed the current website at desktop, tablet and mobile widths. Reference screenshots were inspected locally rather than copying its portrait or personal content into this repository.

Verified live website observations: Jekyll 4.4.1 / Minima, near-white `#fdfdfd` canvas, system sans-serif at 17.6px / 26.4px line height, 800px text width inside a wrapper with 30px horizontal padding (860px total at desktop), a 5px dark top border, one-line name/navigation header with a light lower rule, and a 150px-wide portrait floated left with 40px right spacing. The footer has a thin full-width rule and centered muted profile links. At 600px the reference changes to a compact menu; content gutters narrow to 18px. The reference /cv/ page displays a titled 800px-high PDF iframe. The reference homepage has no visible title before its introduction.

The reference website repository https://github.com/gboeing/gboeing.github.io at `fcacc58b4a9c6c975de472db97f97b4d7d6a429b` separately declares MIT licensing, copyright 2014–2026 Geoff Boeing. Our markup, JavaScript and SCSS are independently implemented around the existing Academic Pages pipeline; no reference text, photographs or source snippets are incorporated.

Verified reference CV source: https://github.com/gboeing/cv at `98a2d05452dcc2833af1f2012b0be061fe688692`. `LICENSE.txt` is MIT, copyright 2017–2025 Geoff Boeing. Source observations: 11-point report, Letter paper, EB Garamond body, TeX Gyre Heros headings, uppercase small section headings, 1-inch left/top margins, compact lists, 1.7-cm date column, black links and a two-part contact header. The live reference PDF was subsequently downloaded and inspected with pdfinfo and Poppler renders of pages 1, 2 and 22. It is a 22-page Letter document. Visual observations agree with the source: bold serif name, split contact header, compact date/citation columns, uppercase sans-serif section headings without decorative panels, black links, and centered page numbers. Only representative reference pages were inspected; this is not a full reference-PDF quality audit. No reference code, photograph, text, or font asset is copied into this implementation.

## Comparison

| Area | Reference evidence / requested direction | Current website | Phase 1 proposal |
| --- | --- | --- | --- |
| Canvas | Near-white background, 800px text column verified | Pastel background, gradient panels, broad layout | Match near-white canvas and 800px main column |
| Header | Single row with lightweight name, plain navigation, dark top rule | Floating rounded navigation, active gradient pills | Same basic alignment and rules; retain all routes via name/home and five page links |
| Type | System sans-serif 17.6px/26.4px verified; CV serif/sans verified | Colored headings and injected decorative icons | Match system font rhythm, remove icon badges; PDF typography deferred |
| Portrait | Left floated, 150px wide with 40px right spacing | Sticky pastel sidebar with an existing broken image URL | Match reference placement using the existing dated portrait, preserving original framing; stack on narrow mobile |
| Metrics | Preserve data and separation | Three dashboard-style gradient cards with tiles | Three plain source columns separated by fine rules; exact scope, values, date and links retained |
| Bibliography | Readable scholarly citations requested | Citations among rounded panels | Original citation text, author emphasis, DOI links and hanging indents retained |
| Footer | Understated requested | Large colored footer | Small neutral footer aligned to the content shell |
| Dark mode | Preserve existing preference | Green/purple surfaces | Neutral dark canvas, restrained blue links, unchanged three-mode preference |

Reference-derived dimensions and typography are used where they fit the existing content. Deliberate adaptations: retain the owner's much longer biography and academic sections; display research metrics directly after the introduction; retain System/Light/Dark controls; switch the menu at 900px to accommodate the longer name and five links; stack the portrait on narrow mobile. The text footer retains existing attribution and sitemap access instead of duplicating profile links already present in the homepage.

## Architecture and data inventory

- Jekyll 3.10 / GitHub Pages 232, Ruby 3.2; no Node frontend bundle. SCSS compiles through Jekyll. `assets/js/custom-ui.js` owns theme and mobile-navigation behavior.
- Public routes: `/`, `/research/`, `/publications/`, `/projects/`, `/cv/`, `/contact/`, `/sitemap/`, `/404.html`. Existing redirect declarations stay in place (including `/about/`, `/about.html`, `/resume`).
- Shared layouts: `_layouts/default.html`, `single.html`, `archive.html`; head/SEO, sidebar/author, masthead and footer includes. `_sass/custom.scss` is the final visual layer.
- 25 publication records and 2 project records. Homepage: 4 selected publications and 2 selected projects, sorted by existing `selected_order`. No YAML academic data is changed.
- Research metrics remain a dated, manual snapshot from three distinct databases; no fabricated annual series or aggregated citation count.
- `scripts/generate_cv_pdf.py`: Python 3.12, Markdown, PyYAML, WeasyPrint. `scripts/validate_site.py`: BeautifulSoup and PyYAML. Public PDF path remains fixed.
- Private source tools use python-docx, ruamel.yaml, Pillow and PyYAML. DOCX parser reconciles public-safe records; standalone dated portraits are re-encoded without EXIF. No private content is committed to the public repository.
- Public CI: `validate-site.yml` builds and checks PRs targeting master; `generate-cv-pdf.yml` regenerates PDF on its declared source paths. Private CI: DOCX dry run, portrait regression/integration, and separate CV/portrait PR automation. Phase 1 leaves these workflows unchanged.
- Future PDF work must extend workflow path triggers if templates, fonts, styles, or generated-profile dependencies are added. Do not rely on a new styling file without a corresponding trigger.

## PDF architecture decision for later review

| Consideration | Retain WeasyPrint (recommended) | Add LaTeX |
| --- | --- | --- |
| Fidelity | Serif body, uppercase sans headings, date columns and hanging indents can be recreated with HTML/CSS | Closest match to reference typesetting |
| Maintenance and CI | Existing pipeline and dependencies; small change surface | Additional TeX distribution, escaping and build steps |
| Unicode | Existing Unicode text pipeline and font fallback | Requires careful engine/font selection and escaping |
| Shared records | Existing generator already consumes public include and YAML | Needs another serializer and parity checks |
| Long documents | Paged CSS, page counters and break controls; inspect output | Strong pagination but larger migration risk |
| Content safety | Existing filtering remains in place | Greater risk of omitted/duplicated content during conversion |

Keep WeasyPrint and A4 for Phase 3 unless visual review establishes a concrete limitation. Do not change the current tracked PDF or generator during Phase 1.

## Baseline verification

Before implementation: 8 portrait regression tests passed; custom JavaScript syntax passed; baseline, latest DOCX import and synthetic portrait each generated a PDF, built with Jekyll, and passed technical QA covering 8 pages. Latest DOCX reconciliation reported zero unmatched publication/project records. Baseline screenshots are under `previews/before-1440.png` and `before-390.png`.

## Phases and review

1. Phase 1: implement the shared visual foundation, navigation, footer and homepage. Supply browser screenshots at desktop/mobile widths and functional regression results in a PR if API access permits.
2. Await visual approval before merging into production. Review visual similarity alongside deliberate content and accessibility adaptations.
3. Phase 2: refine all remaining page-specific presentation after approval, preserving data, routes and automation.
4. Phase 3: redesign PDF separately; compare extracted public text and records, render every page, inspect clipping/Unicode/links, update CI triggers, and request review.
5. Final regression: rebuild all site/import scenarios, verify Actions and eventual Pages deployment results. Local success does not establish deployment success.
