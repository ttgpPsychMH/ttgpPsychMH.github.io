# Post-merge production audit — 17 October 2026

## Production result

No deployment blocker found. Website PR [#21](https://github.com/ttgpPsychMH/ttgpPsychMH.github.io/pull/21) merged at 15:39:06 Bangkok time; Garamond PDF PR [#23](https://github.com/ttgpPsychMH/ttgpPsychMH.github.io/pull/23) merged at 15:45:29. The production head is `250dc54483eebd27a5d1f19d76500727fdd0c487`, including the subsequent generated PDF commit.

GitHub Pages reports `built`, publishing `master` from `/`. [Pages run 39018583736](https://github.com/ttgpPsychMH/ttgpPsychMH.github.io/actions/runs/39018583736) succeeded at that exact head; its deployment finished at 15:46:50 Bangkok time (08:46:50 UTC). Earlier cancelled runs were superseded by this successful deployment.

[Production results](production-results.json) preserve the HTTP, browser and PDF observations:

- HTTP 200 for Home, Research, Publications, Projects, CV and Contact, plus all 20 discovered local asset URLs: the configured portrait, CSS/JavaScript, favicon/manifest assets, downloadable PDF and CSS-referenced font formats. Correct content types; no failed asset responses observed.
- Public Chromium checks passed all 30 combinations of those six pages and 1440/1024/768/390/320px widths. Styles, images, current navigation, H1 semantics, body size and overflow passed. Keyboard skip/menu navigation, Escape, outside clicks, mobile navigation, System/Light/Dark modes, theme persistence/system changes, blocked storage and navigation without JavaScript passed. This used the browser checker from the deployed base, before the requested footer change.
- Clicking every desktop navigation destination and the home brand reached the intended route. Clicking the CV download link returned HTTP 200 with `application/pdf`.
- The downloaded public PDF passes artifact validation: 6 A4 pages, 25 publications, 2 projects, all 87 public source paragraphs, embedded Garamond fonts, 24 distinct clickable links, page numbers and text bounds. Its SHA-256 equals the tracked production PDF: `0cc005f7a3309b5c8b0d4450d717640563383ec099fb888a93113f53b7c061ec`.

The environment initially denied the production domain at its network proxy. That was an environment restriction, not evidence of downtime. After adding the production hostname to the environment's allowed-domain draft, actual HTTP and browser requests succeeded. Chromium used the trusted environment CA; TLS verification remained enabled.

## Maintenance changes

- The web CV date now reads `_data/cv_sync_state.yml`, the state written by the existing private DOCX importer. The PDF renderer expands that same date expression because it does not execute Liquid. PDF typography and content sources remain intact. Date-only state changes now trigger PDF generation too.
- Validation retains PR/manual/staging triggers and adds every `master` push without a path filter, including PDF-only commits. Since pushes made with `GITHUB_TOKEN` do not ordinarily start another push workflow, a successful `Generate public CV PDF` completion on `master` also starts validation. That follow-up checks the final `master` tree, including the generated PDF; its event's original `head_sha` predates the bot commit. Push/PR checks still use the triggering SHA.
- Validation has read-only contents permission, never commits or dispatches a workflow, and cancels superseded runs for the same ref/PR. PDF output is excluded from the generator's source path triggers. The generator completion can therefore cause validation, but validation cannot cause another generation/validation loop. Failed generator runs remain failures and do not start the successful-completion check.
- At the owner's subsequent request, the homepage's four text profile links move to a shared footer row of Email, ORCID, ResearchGate and GitHub icons. All destinations still come from the existing author configuration. Buttons have accessible names, decorative glyphs, titles, visible keyboard focus and 56×52px targets; they wrap on narrow screens and follow the existing themes. Font Awesome assets and their existing license notices are retained locally.
- Both reference repositories were consulted: [website](https://github.com/gboeing/gboeing.github.io) at `fcacc58b4a9c6c975de472db97f97b4d7d6a429b`, and [CV](https://github.com/gboeing/cv) at `98a2d05452dcc2833af1f2012b0be061fe688692`. Both declare MIT licensing. The footer implementation is original, using the website's existing icon bundle; no reference personal content, code snippets or assets were copied. Existing Garamond PDF styling is retained.
- Old open-PR/deployment statements are updated while historical redesign screenshots, JSON reports and test counts are preserved. The [metrics proposal](research-metrics.md) describes periodic review, authoritative evidence and draft PRs; no metric values, scopes or snapshot dates change.

Footer previews: [desktop](previews/footer-desktop.png), [mobile](previews/footer-mobile.png), [dark mobile](previews/footer-dark.png).

## Maintenance verification

- `python scripts/test_cv_sync_date.py`: passed. Changing only the fixture state date to 9 January 2027 updates both built HTML and generated PDF, without editing the CV template. Full PDF/site validators pass within the fixture.
- The date fixture reuses the original checkout's installed gem path while building entirely inside the temporary checkout. This also passes with the project-local bundle path used by `ruby/setup-ruby`; it avoids requiring a second gem installation or copying other local Bundler settings into the fixture.
- The actual private DOCX importer was also exercised in temporary source/website copies with a newly dated DOCX filename. It wrote the new authoritative state, retained the Liquid CV template, and produced the correct web/PDF date. The build contained no DOCX files. Source files and sensitive importer reports stayed outside this repository.
- All 8 private portrait regression tests passed. Baseline, current DOCX import and independent synthetic dated-portrait import each generated a PDF, built Jekyll and passed site QA for all 8 core/utility pages. No private workflow changes were needed.
- The updated browser checker passed all 30 local page/width combinations plus the existing theme/menu/storage checks and new footer glyph, label and keyboard-focus checks; see [maintenance browser results](browser-results.json). Desktop, mobile and dark footer screenshots were inspected. New artifacts use `UI_OUTPUT_DIR` so historical redesign evidence stays unchanged.
- Both JavaScript syntax checks and actionlint 1.7.12 checks for the two modified workflows passed. The three academic YAML files, sync state, generated public profile, portrait, citations/projects, PDF styles/fonts, tracked PDF and existing public routes remain unchanged; the private checkout remains clean.

Repeat the public PDF artifact check after downloading it from its fixed public URL:

```bash
python scripts/validate_cv_pdf.py --pdf /tmp/public-cv.pdf
```

For the maintenance code, install `scripts/requirements-cv.txt`, run `bundle install`, then run the date test, PDF generator/checker, Jekyll build and site validator in a temporary checkout. Browser preview commands are in [redesign verification](../redesign/verification.md); write fresh artifacts to a separate `UI_OUTPUT_DIR`.

## Limits and rollout

These public-site observations describe the deployed base, not the pending maintenance branch. The new date/CI/footer changes require PR review and merge before they appear in production. PR CI is checked on the actual PR revision; the new `master` push and generator-completion hooks can only be observed after the workflow is merged onto the default branch. Workflow syntax/local checks do not establish that those future events have already run.

The audit is a point-in-time check, not uptime monitoring. External academic-provider values and link availability were not reverified; they remain the previously approved snapshot. The metrics document is a proposal, with no scheduled scraper or automatic numeric edits. No private DOCX, original portrait, credentials or sensitive sync report is published.
