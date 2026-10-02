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

## Research metrics

{% assign research_metrics = site.data.research_metrics %}
<div class="research-metrics" aria-label="Research metrics snapshot">
  <div class="research-metrics__meta">
    <span><i class="fa-regular fa-clock" aria-hidden="true"></i> Snapshot: {{ research_metrics.updated | date: "%-d %B %Y" }}</span>
    <span>Source coverage differs across databases; metrics are presented separately.</span>
  </div>

  <div class="research-metrics__sources">
  {% for source in research_metrics.sources %}
    <section class="research-metric-source research-metric-source--{{ source.id }}" data-metric-source="{{ source.id }}">
      <div class="research-metric-source__header">
        <div class="research-metric-source__title">
          <span class="research-metric-source__icon" aria-hidden="true"><i class="{{ source.icon_class }}"></i></span>
          <div class="research-metric-source__identity">
            <h3>{{ source.name }}</h3>
            <span class="research-metric-source__scope">{{ source.scope }}</span>
          </div>
        </div>
        <a class="research-metric-source__link" href="{{ source.profile_url }}" rel="noopener noreferrer">View profile <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
      </div>

      {% if source.metrics and source.metrics.size > 0 %}
      <div class="research-metric-values" aria-label="{{ source.name }} metrics">
        {% for metric in source.metrics %}
        <div class="research-metric-value" data-metric-key="{{ metric.key }}">
          <span class="research-metric-value__number">{{ metric.value }}</span>
          <span class="research-metric-value__label">{{ metric.label }}</span>
        </div>
        {% endfor %}
      </div>
      {% endif %}

      {% if source.author_positions and source.author_positions.size > 0 %}
      <div class="research-author-positions" aria-label="{{ source.name }} author positions">
        <div class="research-author-positions__heading">Author position</div>
        {% for position in source.author_positions %}
        <div class="research-author-position" data-position-key="{{ position.key }}">
          <div class="research-author-position__label">
            <span>{{ position.label }}</span>
            <strong>{{ position.value }}%</strong>
          </div>
          <div class="research-author-position__track" role="progressbar" aria-label="{{ position.label }}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{{ position.value }}">
            <span class="research-author-position__fill" style="width: {{ position.value }}%;"></span>
          </div>
        </div>
        {% endfor %}
      </div>
      {% endif %}
    </section>
  {% endfor %}
  </div>

  <p class="research-metrics__note"><i class="fa-solid fa-circle-info" aria-hidden="true"></i> Citation and publication counts vary by database coverage and indexing practices and should not be summed across sources.</p>
</div>

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

