# Phase 1 review and verification

## Visual review

- [Desktop first screen](previews/homepage-1440-viewport.png)
- [Mobile first screen](previews/homepage-390-viewport.png)
- [Full desktop homepage](previews/homepage-1440.png)
- [Full mobile homepage](previews/homepage-390.png)
- [1024px](previews/homepage-1024.png), [768px](previews/homepage-768.png), [320px](previews/homepage-320.png)
- [Mobile navigation](previews/mobile-menu.png)
- [Dark theme](previews/homepage-dark-390.png)
- [Previous desktop design](previews/before-1440.png), [previous mobile design](previews/before-390.png)

The prototype follows the verified reference's 800px text column, near-white canvas, system-font typography, dark upper rule, inline header/navigation, and small left portrait. It retains the owner's original biography and academic sections, metrics in the required position, all routes, and three theme modes. The portrait stacks on narrow phones and the menu switches earlier to accommodate the longer name. Existing secondary page content remains intact under the shared foundation; page-specific redesign and PDF redesign await approval.

Screenshots are captured with Chromium through Playwright. They are static review artifacts, not claims of deployment. Reference screenshots were inspected locally; its personal image/content is not committed here.

## Repeat the checks

Activate the environment's Ruby/Python tools, then run Jekyll, JavaScript syntax and site QA from the website checkout. The environment helper safely checks PDF/import behavior in temporary copies:

```bash
source /workspace/.onboarding/activate.sh
bash /workspace/.onboarding/validate.sh
```

The helper runs all 8 portrait regression tests, JavaScript syntax checking and three complete integration scenarios: baseline data, latest private DOCX import, and synthetic new portrait. Each scenario generates the PDF, builds Jekyll and runs `scripts/validate_site.py`. Each site validation covers 8 core/utility pages. Reports from DOCX tests stay in /tmp and must not be committed.

For browser testing, start a dedicated preview build so ordinary production-URL builds cannot overwrite its local asset URLs:

```bash
bundle exec jekyll serve --host 127.0.0.1 --port 4010 \
  --destination /tmp/academic-design-preview --no-watch
```

Use another shell to run:

```bash
CHROMIUM_PATH=/usr/bin/chromium node scripts/check_ui.cjs
```

Playwright is available in the prepared environment. Elsewhere, install it into an ignored local tooling directory and provide its module path, for example:

```bash
npm install --prefix local/browser-tools --no-save playwright
NODE_PATH="$PWD/local/browser-tools/node_modules" \
  CHROMIUM_PATH=/path/to/chromium node scripts/check_ui.cjs
```

The test accepts `SITE_TEST_URL` for a different local preview origin. It visits six routes at 1440, 1024, 768, 390 and 320 pixels; checks stylesheet application, image loading, H1/current-link semantics, readable body size and horizontal overflow; and tests keyboard skip navigation, menu focus/Escape/outside clicks, themes, storage persistence, system preference changes and blocked localStorage. Navigation without JavaScript is also checked. Theme foreground/link contrast is measured against the canvas. Results are written to `browser-results.json`; these are functional browser checks, not pixel-diff baselines.

Data preservation check:

```bash
git diff origin/master --exit-code -- \
  _data/publications.yml _data/projects.yml _data/research_metrics.yml \
  _data/cv_sync_state.yml _data/portrait_sync_state.yml \
  _includes/generated_cv_profile.md scripts/generate_cv_pdf.py files .github/workflows
```

## Phase boundary and external checks

This review does not approve a production merge. The PDF architecture comparison is in the design audit; the existing generator and tracked PDF are intentionally unchanged in Phase 1. No new PDF page previews are claimed.

GitHub Actions and Pages deployment require separate remote evidence. Local checks do not establish either outcome. GitHub API initially returned Forbidden; access subsequently succeeded. Draft PR [#21](https://github.com/ttgpPsychMH/ttgpPsychMH.github.io/pull/21) is open, and the existing Validate Jekyll site workflow was triggered. Its result must be checked independently; publication and deployment remain subject to owner approval.

The live reference website, TeX source and reference PDF were accessible after the network update. Reference PDF inspection is recorded in the audit. Keep the CV source and website source licenses separate; both were verified as MIT.

## Current local results

- PASS: 8 portrait regression tests; JavaScript syntax; all three PDF/build/import scenarios, with technical QA passing for 8 pages per scenario.
- PASS: browser checks for all six routes at all five widths; three theme modes and persistence; keyboard skip link, navigation focus and Escape, outside click, navigation without JavaScript, and storage denial. The final run also checks CV action-link contrast.
- PASS: unchanged academic YAML, sync-state records, generated profile, PDF generator, tracked public files and existing workflows compared with origin/master. The private checkout remains clean.
- Visual inspection performed on desktop/mobile homepage, mobile menu and dark homepage screenshots, plus desktop Research and mobile CV pages. Portraits and existing PDF preview load.
- Remote status: draft PR [#21](https://github.com/ttgpPsychMH/ttgpPsychMH.github.io/pull/21) is open. Consult its checks for current GitHub Actions results. Production has not been merged or deployed.


## Phase 2 — approved direction extended to all pages

After the owner approved Phase 1, Research, Publications, Projects, CV and Contact were changed to the same readable single-column layout. Bibliography entries have hanging indents and understated indexing/DOI metadata. Publication statistics remain data-driven, displayed without cards. Projects retain every metadata field in responsive definition lists; their displayed sync date now comes from the actual sync state. Research has keyboard-accessible section links, and the CV has a link directly to its web version. No academic records, generated profile, private workflow or PDF generator was changed in this website phase.

[Research desktop](previews/research-1440.png) · [Publications desktop](previews/publications-1440.png) · [Projects mobile](previews/projects-390.png) · [CV desktop](previews/cv-1440.png) · [Contact mobile](previews/contact-390.png).

Local checks repeated after these changes: all 30 page/viewport browser checks, theme/keyboard/storage checks, 8 portrait regressions, and all 3 PDF/Jekyll/import scenarios passed. Website approval does not itself approve the separately redesigned PDF.
