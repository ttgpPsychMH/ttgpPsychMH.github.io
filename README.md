# Personal Academic Website

This repository contains the personal academic website and research portfolio of **Tran Thien Gia Phuoc**.

View the website at **https://ttgppsychmh.github.io**.

The site presents my research interests, publications, research projects, academic experience, curriculum vitae, and scholarly profiles. It is built with Jekyll and GitHub Pages, using Academic Pages as the underlying framework with a custom visual and content system.

## Structure

- `_data/publications.yml` — single source of truth for publications, selected publications, publication statistics, and CV publication records
- `_data/projects.yml` — single source of truth for research projects, selected projects, and CV project records
- `_pages/` — website page structure and non-tabular academic content
- `_config.yml` — site-wide identity, metadata, and profile configuration
- `_sass/custom.scss` — custom pastel green–purple visual system
- `assets/js/custom-ui.js` — theme switching and interface enhancements
- `files/` — public downloadable files, including the generated academic CV
- `scripts/generate_cv_pdf.py` — generates the public CV PDF from the web-CV framework plus the shared publication/project data
- `scripts/validate_site.py` — validates shared data, cross-page rendering, SEO, accessibility, metadata, and internal links

## Maintenance

### Publications

Add or update a publication in `_data/publications.yml`. The same record is used to:

- render the Publications page
- calculate Original Research / Conference Paper / Scopus Q1–Q4 / SSCI / ESCI counts
- populate the Publications section of the web CV
- populate the Publications section of the generated CV PDF
- populate the homepage when `selected: true`

Use `selected_order` to control the order of selected publications on the homepage.

### Projects

Add or update a research project in `_data/projects.yml`. The same record is used to:

- render the Projects page
- populate the Research Projects section of the web CV
- populate the Research Projects section of the generated CV PDF
- populate the homepage when `selected: true`

Use `selected_order` to control the order of selected projects on the homepage.

### CV

General CV content such as education, appointments, training, awards, and memberships remains in `_pages/cv.md`. Publications and projects are generated from their shared YAML sources.

When `_pages/cv.md`, `_data/publications.yml`, or `_data/projects.yml` changes, GitHub Actions regenerates the public PDF automatically.

## Validation

Before publication, GitHub Actions:

- checks custom JavaScript syntax
- generates the CV PDF from the current shared data
- builds the Jekyll site
- verifies that homepage selections, Publications, Projects, web CV, and publication statistics all match the YAML sources
- checks SEO, accessibility, structured data, sitemap, manifest, and internal links

The site uses a system-aware light/dark theme. Visitors can also select System, Light, or Dark manually.

## Credits

The site is built on [Academic Pages](https://github.com/academicpages/academicpages.github.io), which is based on the [Minimal Mistakes](https://github.com/mmistakes/minimal-mistakes) Jekyll theme. The repository retains the upstream MIT license for the software and theme components.

Academic writing, CV content, publications, and other scholarly materials remain subject to their respective authors' and publishers' rights unless otherwise stated.
