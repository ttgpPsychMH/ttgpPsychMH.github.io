# Newsprint website theme

This restyle applies the Hallmark Newsprint visual direction to the existing academic website. It keeps the Jekyll layouts, content order, public routes, academic data, CV/PDF workflow, portrait automation and automatic Light/Dark behavior intact.

## Visual direction

- Warm newsprint paper, warm black ink and a dried-brick accent use OKLCH tokens.
- Zilla Slab Bold sets the masthead and headings; Spectral sets running text; Libre Franklin is reserved for comparable figures.
- Hairlines and double rules carry hierarchy without cards, rounded corners or shadows.
- The existing portrait is monochrome with a factual caption.
- Research metrics form a ruled broadsheet box score.
- Light and Dark modes share the same warm hue family and meet the existing contrast checks.
- The theme action uses a monochrome inline SVG sun or moon, while its accessible label and tooltip continue to describe the available action.

The local design lock is recorded in [`DESIGN.md`](../../DESIGN.md). Web-font provenance and exact SIL Open Font License texts live in [`assets/fonts/newsprint`](../../assets/fonts/newsprint/README.md).

## Reference and licensing

The design was adapted from the Newsprint theme specification in [nutlope/hallmark](https://github.com/nutlope/hallmark/tree/407fa689f4a276f2fd389208d271d0fef08f5058/skills/hallmark/references/themes), commit `407fa689f4a276f2fd389208d271d0fef08f5058`. Hallmark is MIT licensed; its notice is retained in [`HALLMARK-LICENSE.txt`](HALLMARK-LICENSE.txt). The implementation in this repository was written for the existing Academic Pages markup and does not copy Hallmark application code or image assets.

## Verification

Run the local browser preview with the prepared cloud environment:

```bash
source /workspace/.onboarding/activate.sh
bundle _2.6.9_ exec jekyll serve --host 127.0.0.1 --port 4050 \
  --destination /tmp/newsprint-preview
```

Then run:

```bash
CHROMIUM_PATH=/usr/bin/chromium \
SITE_TEST_URL=http://localhost:4050 \
UI_OUTPUT_DIR=/tmp/newsprint-ui \
node scripts/check_ui.cjs
```

The final run covered the homepage, Research, Publications, Projects, CV and Contact at 1440, 1024, 768, 390 and 320 pixels in Light and Dark modes: 60 page/viewport combinations. It also covered no-flash initialization, live OS-theme changes, session-scoped manual choices, blocked storage, no-JavaScript fallback, keyboard navigation, labeled icons, self-hosted font loading, responsive overflow, image loading and contrast.

The machine-readable browser result is retained in [`browser-results.json`](browser-results.json).

`/workspace/.onboarding/validate.sh` also passed all 8 portrait regression tests and three isolated end-to-end scenarios: baseline, private CV import and a synthetic newly dated portrait. Each scenario regenerated the PDF, built Jekyll and passed technical validation across 8 core/utility pages.

Static previews for review:

- [`light-desktop.png`](previews/light-desktop.png)
- [`dark-desktop.png`](previews/dark-desktop.png)
- [`light-mobile.png`](previews/light-mobile.png)
- [`dark-mobile.png`](previews/dark-mobile.png)

The browser serializes OKLCH colors directly. `scripts/color_utils.cjs` converts both computed OKLCH and RGB colors to relative luminance so contrast regression checks remain format independent.

## Deliberate exceptions

Publication and CV metadata retain middle-dot separators where they are part of compact, verified citation/indexing strings. Long academic records remain complete instead of being shortened to a marketing-page word budget. Bundled Font Awesome and Academicons remain in use only for verified profile and interface marks.

Hallmark's static audit preserved all 46 recorded links. It reports 315 floor findings and 79 reflex findings after the change, compared with 309 and 79 before it. Those findings come from inherited, bundled Academic Pages/vendor CSS and preserved academic date/citation punctuation; the audit reported no finding against the new source partial, templates or test scripts. Browser and semantic checks remain authoritative for rendered contrast, focus, overflow and responsive behavior because the static audit does not associate the compiled stylesheet with each generated HTML file.
