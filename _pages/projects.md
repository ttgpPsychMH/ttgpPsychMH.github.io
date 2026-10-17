---
permalink: /projects/
title: "Projects"
description: "Research projects involving occupational, behavioral, and psychological research, including project roles, funding, methods, and outcomes."
author_profile: false
---

This page presents the research projects listed in my academic CV last synchronized on **{{ site.data.cv_sync_state.cv_date | date: "%-d %B %Y" }}**. Project details are generated from a single structured data source used across the website and CV.

{% for project in site.data.projects %}
<section class="project-card" data-project-id="{{ project.id }}" markdown="1">

## {{ project.title }}

<dl class="project-details">
  <dt>Period</dt><dd>{{ project.period }} [{{ project.status }}]</dd>
  <dt>Role</dt><dd>{{ project.role }}</dd>
  <dt>Institution</dt><dd>{{ project.institution }}</dd>
  <dt>Project type</dt><dd>{{ project.project_type }}</dd>
  <dt>Project code</dt><dd>{{ project.project_code }}</dd>
  <dt>Principal Investigator</dt><dd>{{ project.principal_investigator }}</dd>
  <dt>Funding</dt><dd>{{ project.funding_vnd }} ({{ project.funding_usd }})</dd>
  <dt>Outcome</dt><dd>{{ project.outcome }}</dd>
</dl>

{% if project.details %}{{ project.details }}{% endif %}

</section>
{% endfor %}
