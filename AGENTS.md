# Academic website engineering rules

- Develop in the existing checkout on a feature branch. Do not merge visual redesigns into `master` without the owner's visual approval. Phase 1 covers the shared foundation and homepage; subsequent page and PDF redesigns require review.
- Preserve all routes, redirects, SEO and accessibility. Theme behavior follows the OS automatically, with a two-state Light/Dark button and a temporary tab-session override cleared by OS changes. Keep readable focus indicators and usable navigation/theme fallbacks without JavaScript.
- `_data/publications.yml`, `_data/projects.yml`, and `_data/research_metrics.yml` remain authoritative. Never invent or alter academic facts while changing presentation. Preserve record IDs, selected ordering, author order, indexing years and database separation.
- On the homepage, research metrics follow the introduction and precede research interests. Keep exact snapshot dates, values, source links and source scopes.
- Read portrait configuration from `site.author.avatar`; never hard-code the current dated filename into templates. The private portrait importer must remain independent of DOCX updates.
- Never place private DOCX, original photos, tokens or sensitive sync reports in this repository. Run importer integration checks against temporary copies. Do not change private workflows or existing secrets for a visual redesign.
- Keep the generated PDF at `files/Tran_Thien_Gia_Phuoc_Academic_CV.pdf`, and preserve the DOCX → public-safe include → shared YAML → web/PDF pipeline. Retain A4 unless approved otherwise. PDF styling work belongs to its own reviewed phase.
- Use original frontend implementation. Do not copy reference-site code or assets without verifying licensing. Retain notices for any adapted licensed code.
- Validate with Jekyll, `node --check assets/js/custom-ui.js`, PDF generation and `python scripts/validate_site.py`. Do not weaken semantic QA. Generate PDFs and run sync scenarios in temporary copies unless intentionally updating the tracked PDF.
- Verify browser layouts at 1440, 1024, 768, 390 and 320 pixels, including mobile menu, keyboard access, themes, overflow and profile image loading. Record evidence and limitations honestly.
- Do not claim a PR, Actions run, or deployment succeeded without its actual result. Do not deploy before approval.
