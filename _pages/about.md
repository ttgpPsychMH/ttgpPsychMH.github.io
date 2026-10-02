---
permalink: /
description: "Academic profile of Tran Thien Gia Phuoc, a psychology researcher focused on occupational mental health, psychological assessment, and quantitative research."
author_profile: true
redirect_from:
  - /about/
  - /about.html
---

<h1 class="sr-only">Tran Thien Gia Phuoc</h1>

<p class="home-intro">I am a researcher in psychology with interests in occupational mental health, psychological assessment, and quantitative research. My work has examined work engagement, burnout, psychological distress, employee well-being, and broader mental health questions across working and student populations.</p>

My research experience includes study design, data collection, manuscript preparation, and quantitative analysis. I am particularly interested in using psychological and organizational research to better understand mental health and well-being in educational and workplace settings.

## Research interests

- Occupational mental health and employee well-being
- Work engagement, burnout, and psychological distress
- Psychological assessment and quantitative methods
- Mental health among students, young adults, and working populations
- Developing interests in cognitive psychology and behavioral research

[Research overview →](/research/)

## Academic profile highlights

- Member, Psychological Research Laboratory (2019–Present)
- Ad hoc reviewer for Springer Nature journals listed in my CV, including *BMC Psychology*, *Discover Psychology*, *Scientific Reports*, and *Discover Public Health*
- Member, Vietnam Psychotherapy Association (2024–Present)
- Idea Prize, Student Scientific Research Conference, Ho Chi Minh City University of Education (2020)
- Research experience in eye-tracking and emotional Stroop task data collection
- Training in social and behavioral research ethics, statistics, mental healthcare, and human resource management

## Selected publications

{% assign selected_publications = site.data.publications | where: "selected", true | sort: "selected_order" %}
<div class="selected-publications" role="list" aria-label="Selected publications">
{% for pub in selected_publications %}
  {% assign selected_citation = pub.citation | replace: "&#42;", "" | markdownify | remove: "<p>" | remove: "</p>" %}
  <p role="listitem" data-publication-id="{{ pub.id }}">{{ selected_citation }}{% if pub.doi %} <a href="{{ pub.doi }}" rel="noopener noreferrer">{{ pub.doi }}</a>{% endif %}</p>
{% endfor %}
</div>

[View all publications →](/publications/)

## Selected research projects

{% assign selected_projects = site.data.projects | where: "selected", true | sort: "selected_order" %}
<div class="selected-projects" role="list" aria-label="Selected research projects">
{% for project in selected_projects %}
<div class="selected-project" role="listitem" data-project-id="{{ project.id }}">
<strong>{{ project.title }}</strong><br>
{{ project.role }}, {{ project.institution }}, {{ project.period }}.
</div>
{% endfor %}
</div>

[View research projects →](/projects/)

## Academic profiles

[ORCID](https://orcid.org/0000-0002-7104-8859) · [Google Scholar](https://scholar.google.com/citations?user=w4dB_uUAAAAJ) · [ResearchGate](https://www.researchgate.net/profile/Gia-Phuoc-Tran-Thien) · [Scopus](https://www.scopus.com/authid/detail.uri?authorId=58247687800) · [Web of Science](https://www.webofscience.com/wos/author/record/2298566)
