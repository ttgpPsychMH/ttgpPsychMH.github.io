---
permalink: /projects/
title: "Projects"
description: "Research projects involving occupational, behavioral, and psychological research, including project roles, funding, methods, and outcomes."
author_profile: true
---

This page presents the research projects listed in my academic CV dated **2 March 2026**. Project details are generated from a single structured data source used across the website and CV.

{% for project in site.data.projects %}
<section class="project-card project-card--{{ forloop.index }}" data-project-id="{{ project.id }}" markdown="1">

## {{ project.title }}

**Period:** {{ project.period }} [{{ project.status }}]  
**Role:** {{ project.role }}  
**Institution:** {{ project.institution }}  
**Project type:** {{ project.project_type }}  
**Project code:** {{ project.project_code }}  
**Principal Investigator:** {{ project.principal_investigator }}  
**Funding:** {{ project.funding_vnd }} ({{ project.funding_usd }})  
**Outcome:** {{ project.outcome }}

{% if project.details %}{{ project.details }}{% endif %}

</section>
{% endfor %}
