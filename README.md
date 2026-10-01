# Personal Academic Website

This repository contains the personal academic website and research portfolio of **Tran Thien Gia Phuoc**.

View the website at **https://ttgppsychmh.github.io**.

The site presents my research interests, publications, research projects, academic experience, curriculum vitae, and scholarly profiles. It is built with Jekyll and GitHub Pages, using Academic Pages as the underlying framework with a custom visual and content system.

## Structure

- `_pages/` — website content
- `_config.yml` — site-wide identity, metadata, and configuration
- `_sass/custom.scss` — custom pastel green–purple visual system
- `assets/js/custom-ui.js` — theme switching and interface enhancements
- `files/` — public downloadable files, including the academic CV
- `scripts/generate_cv_pdf.py` — generates the public CV PDF from the web CV
- `scripts/validate_site.py` — pre-launch SEO, accessibility, metadata, and internal-link checks

## Maintenance

The academic CV is maintained in `_pages/cv.md`. When it changes, GitHub Actions automatically regenerates the public PDF.

Site changes are validated automatically before publication. The validation workflow checks JavaScript syntax, builds the Jekyll site, and runs SEO, accessibility, structured-data, sitemap, manifest, and internal-link checks.

The site uses a system-aware light/dark theme. Visitors can also select System, Light, or Dark manually.

## Credits

The site is built on [Academic Pages](https://github.com/academicpages/academicpages.github.io), which is based on the [Minimal Mistakes](https://github.com/mmistakes/minimal-mistakes) Jekyll theme. The repository retains the upstream MIT license for the software and theme components.

Academic writing, CV content, publications, and other scholarly materials remain subject to their respective authors' and publishers' rights unless otherwise stated.
