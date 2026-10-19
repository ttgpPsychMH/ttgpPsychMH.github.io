# Automatic system theme and two-state control

The website initially follows the visitor's operating system. The button shows a moon with “Switch to dark theme” in Light, and a sun with “Switch to light theme” in Dark. Its tooltip matches its accessible name. There is no selectable System mode.

## State and initialization

`_includes/theme-init.js` runs inline in the head before the first stylesheet. It owns both initial selection and later changes, replacing the duplicated head/runtime three-mode logic. It sets an explicit `data-theme="light"` or `"dark"` before styled content can paint. The button stays hidden until its handler and descriptive labels are ready.

Manual choices use the `theme-session` sessionStorage key with two fields: `theme` and `system` (the OS preference at selection). Navigation and reload in the same tab retain a valid choice. A different current system snapshot invalidates the stored choice on the next load. A live `matchMedia` change clears the choice immediately. `pageshow` reconciles restored history pages, including re-reading session state on a back/forward-cache restoration; visibility changes also check the current OS preference.

The old localStorage `theme` key is never read as a preference and is removed where allowed, including legacy `system`, `light`, `dark` or invalid values. Malformed session data, an invalid mode or a mismatched system snapshot is discarded. Storage reads/writes/removals are guarded independently; no credentials, cookies, external services or frontend libraries are involved.

Dark variables are shared through Sass mixins with a CSS `prefers-color-scheme` fallback when there is no explicit data-theme. This preserves the existing light/dark palette, including inherited Academic Pages variables. With JavaScript disabled the control stays hidden, system changes still update CSS, and navigation remains available.

## Modified files

| Files | Change |
| --- | --- |
| `_includes/theme-init.js`, `_includes/head.html` | One early initializer and session/system state machine |
| `assets/js/custom-ui.js` | Remove legacy three-mode theme code; retain navigation |
| `_includes/masthead.html`, `_layouts/default.html` | Action-labelled semantic button; remove forced initial theme |
| `_sass/custom.scss`, `_sass/theme/_default_dark.scss` | Reuse unchanged dark palettes for the no-JavaScript fallback |
| `scripts/check_theme.cjs`, `scripts/check_ui.cjs` | Theme-policy regressions and both-theme responsive coverage |
| `scripts/validate_site.py`, `.github/workflows/validate-site.yml` | Check early inline initialization/accessibility and all changed JavaScript syntax |
| `README.md`, `AGENTS.md`, `docs/redesign/verification.md`, this directory | Current behavior, review images and test evidence |

## Verification — 19 October 2026

Browser regression results: [JSON report](browser-results.json).

- Six routes × five widths (1440/1024/768/390/320) × two themes: 60 checks. Existing image, stylesheet, H1/current-link, overflow, CV action contrast and footer glyph/accessibility checks remain active. Existing keyboard menu, skip link, Escape, outside click and footer focus checks remain active.
- Fresh Light/Dark sessions; live transitions in both directions; manual toggle; Space/Enter and visible focus; manual choice across internal navigation/reload; OS change clearing that choice; history navigation; a changed system while the website is absent; a fresh session returning to the OS preference.
- Initial system Light/Dark and saved manual Dark/Light under the opposite OS setting were observed before DOMContentLoaded, with the deferred UI script deliberately held. Every styled animation frame sampled had the expected theme/background. The initializer also precedes the first stylesheet in generated HTML. This checks early initialization instead of relying on a late runtime correction.
- All legacy values; malformed/invalid/stale session state; blocked storage getters; throwing writes/removals; no-JavaScript initial/live CSS behavior in both directions; older `addListener` fallback; missing `matchMedia` graceful fallback.
- Body, normal link, navigation, theme-control and footer foreground contrast is at least 4.5:1 in both themes. This is a targeted check, not a complete accessibility audit.
- JavaScript syntax checks, actionlint, Jekyll build and site QA for all 8 core/utility pages; CV-date integration test; generated PDF artifact validation. All 8 portrait regressions and baseline/DOCX/independent-portrait import build scenarios also passed in temporary copies.

Desktop: [Light](previews/theme-light-1440.png) · [Dark](previews/theme-dark-1440.png). Mobile: [Light](previews/theme-light-390.png) · [Dark](previews/theme-dark-390.png).

Build a dedicated preview using the installed Ruby/Python environment:

```bash
node --check _includes/theme-init.js
node --check assets/js/custom-ui.js
node --check scripts/check_theme.cjs
node --check scripts/check_ui.cjs
python scripts/test_cv_sync_date.py
bundle exec jekyll serve --host 127.0.0.1 --port 4040 \
  --destination /tmp/theme-toggle-live --no-watch
```

In another shell, with Playwright and Chromium available:

```bash
SITE_TEST_URL=http://localhost:4040 UI_OUTPUT_DIR=/tmp/theme-toggle-browser \
  CHROMIUM_PATH=/usr/bin/chromium node scripts/check_ui.cjs
```

For PDF/build/site checks use a temporary checkout to avoid overwriting the tracked PDF: install `scripts/requirements-cv.txt`, then run the generator, `scripts/validate_cv_pdf.py`, `bundle exec jekyll build --trace` and `scripts/validate_site.py`. Private importer scenarios and their sensitive reports must also remain in temporary directories. Historical screenshot/report directories are unchanged.

## Limits and compatibility

Session means the browser's tab/page session. A fresh tab/context starts from the OS; manual choices are not shared across separate tabs. Browsers may copy sessionStorage when duplicating a tab, or restore an existing page session after restarting. They define those as continuation of the saved session. The current OS snapshot is still checked on every load.

When storage is blocked, manual switching and live system sync work in the current document, but preserving a manual choice across documents is unavailable; the next page starts from the OS. Without `matchMedia`, JavaScript defaults to Light and the manual button works; live OS detection requires that API. Older MediaQueryList implementations use `addListener`. Modern CSS media-query support is needed for the no-JavaScript fallback.

No browser API exposes an OS theme-change history while no website document is running. A changed current preference is detected on return; a change away and back to the same preference while absent cannot be distinguished from no change. Closing the tab and starting a fresh session discards the override regardless.

Automated coverage uses Chromium on Linux with emulated system preferences. Native Firefox/Safari, physical OS settings panels and compositor-level first-pixel rendering have not been tested. Sampled styled frames and delayed-runtime checks passed; they are not a claim about every possible browser/extension combination. This PR changes no academic YAML, publication/project content, metrics, PDF generator/styles/output, private import workflow or portrait automation. It is not automatically merged or deployed.
