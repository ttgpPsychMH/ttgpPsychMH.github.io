---
layout: archive
title: "Curriculum Vitae"
description: "Academic curriculum vitae of Tran Thien Gia Phuoc, including education, research experience, publications, academic service, awards, training, and research projects."
permalink: /cv/
author_profile: false
redirect_from:
  - /resume
---

<div class="cv-actions">
  <a class="btn cv-download" href="/files/Tran_Thien_Gia_Phuoc_Academic_CV.pdf">Download Academic CV (PDF)</a>
  <a class="btn" href="#web-cv">Read Web CV</a>
  <a class="btn cv-open" href="/files/Tran_Thien_Gia_Phuoc_Academic_CV.pdf" target="_blank" rel="noopener noreferrer">Open PDF in New Tab</a>
</div>

## PDF Preview

<div class="cv-pdf-viewer">
  <iframe
    class="cv-pdf-frame"
    src="/files/Tran_Thien_Gia_Phuoc_Academic_CV.pdf#view=FitH&toolbar=1&navpanes=1"
    title="Tran Thien Gia Phuoc Academic CV PDF preview"
    loading="lazy">
  </iframe>
  <p class="cv-pdf-fallback">If the embedded PDF viewer is not supported by your browser, <a href="/files/Tran_Thien_Gia_Phuoc_Academic_CV.pdf">download the Academic CV PDF</a> or <a href="/files/Tran_Thien_Gia_Phuoc_Academic_CV.pdf" target="_blank" rel="noopener noreferrer">open it in a new tab</a>.</p>
</div>

## Web CV

This web CV is based on the academic CV supplied for this website, dated **{{ site.data.cv_sync_state.cv_date | date: "%-d %B %Y" }}**. Residential address, telephone numbers, date of birth, and place of birth are intentionally omitted from the public website.

## Personal Information

**Full name:** Tran Thien Gia Phuoc  
**Citizenship:** Vietnamese  
**Email:** [tranthiengiaphuoc@gmail.com](mailto:tranthiengiaphuoc@gmail.com)

Academic profiles: [ResearchGate](https://www.researchgate.net/profile/Gia-Phuoc-Tran-Thien) · [ORCID](https://orcid.org/0000-0002-7104-8859) · [Google Scholar](https://scholar.google.com/citations?user=w4dB_uUAAAAJ) · [Scopus](https://www.scopus.com/authid/detail.uri?authorId=58247687800) · [Web of Science](https://www.webofscience.com/wos/author/record/2298566)

{% include generated_cv_profile.md %}

## Publications

<!-- CV_PUBLICATIONS_START -->
{% assign cv_ongoing = site.data.publications | where: "status", "ongoing" %}
{% if cv_ongoing.size > 0 %}
### Ongoing Work

{% for pub in cv_ongoing %}
<div class="cv-reference" data-publication-id="{{ pub.id }}">
{{ pub.citation | markdownify }}
{% if pub.doi %}<p class="cv-reference__doi"><a href="{{ pub.doi }}" rel="noopener noreferrer">{{ pub.doi }}</a></p>{% endif %}
<p class="cv-reference__meta">Status: Ongoing{% if pub.ssci %} · SSCI{% endif %}{% if pub.esci %} · ESCI{% endif %}{% if pub.scopus_quartile %} · SCOPUS {{ pub.scopus_quartile }}{% if pub.scopus_quartile_year %} ({{ pub.scopus_quartile_year }}){% endif %}{% endif %}</p>
</div>
{% endfor %}
{% endif %}

{% assign cv_published = site.data.publications | where: "status", "published" %}
{% assign cv_journal_articles = cv_published | where_exp: "item", "item.type != 'conference_paper'" %}
{% if cv_journal_articles.size > 0 %}
### Peer-Reviewed Journal Articles

{% assign cv_last_year = "" %}
{% for pub in cv_journal_articles %}
{% if pub.year != cv_last_year %}
#### {{ pub.year }}
{% assign cv_last_year = pub.year %}
{% endif %}
<div class="cv-reference" data-publication-id="{{ pub.id }}">
{{ pub.citation | markdownify }}
{% if pub.doi %}<p class="cv-reference__doi"><a href="{{ pub.doi }}" rel="noopener noreferrer">{{ pub.doi }}</a></p>{% endif %}
{% if pub.ssci or pub.esci or pub.scopus_quartile %}<p class="cv-reference__meta">{% if pub.ssci %}SSCI{% endif %}{% if pub.esci %}{% if pub.ssci %} · {% endif %}ESCI{% endif %}{% if pub.scopus_quartile %}{% if pub.ssci or pub.esci %} · {% endif %}SCOPUS {{ pub.scopus_quartile }}{% if pub.scopus_quartile_year %} ({{ pub.scopus_quartile_year }}){% endif %}{% endif %}</p>{% endif %}
</div>
{% endfor %}
{% endif %}

{% assign cv_conference_papers = cv_published | where: "type", "conference_paper" %}
{% if cv_conference_papers.size > 0 %}
### Conference Papers

{% for pub in cv_conference_papers %}
<div class="cv-reference" data-publication-id="{{ pub.id }}">
{{ pub.citation | markdownify }}
</div>
{% endfor %}
{% endif %}
<!-- CV_PUBLICATIONS_END -->

## Research Projects

<!-- CV_PROJECTS_START -->
{% for project in site.data.projects %}
<section class="cv-project" data-project-id="{{ project.id }}" markdown="1">

### {{ project.title }}

**Period:** {{ project.period }} [{{ project.status }}]  
**Role:** {{ project.role }}  
**Project type:** {{ project.project_type }}  
**Project code:** {{ project.project_code }}  
**Institution:** {{ project.institution }}  
**Principal Investigator:** {{ project.principal_investigator }}  
**Funding:** {{ project.funding_vnd }} ({{ project.funding_usd }})  
**Outcome:** {{ project.outcome }}

{% if project.details %}{{ project.details }}{% endif %}

</section>
{% endfor %}
<!-- CV_PROJECTS_END -->
