---
permalink: /publications/
title: "Publications"
description: "Peer-reviewed publications, ongoing work, conference papers, DOI links, and indexing information from the academic CV of Tran Thien Gia Phuoc."
author_profile: true
---

This page follows the publication list in my academic CV dated **2 March 2026**. Publication counts and indexing summaries below are generated automatically from the metadata attached to each entry.

{% assign published = site.data.publications | where: "status", "published" %}
{% assign original_research = published | where: "type", "original_research" %}
{% assign conference_papers = published | where: "type", "conference_paper" %}
{% assign q1 = published | where: "quartile", "Q1" %}
{% assign q2 = published | where: "quartile", "Q2" %}
{% assign q3 = published | where: "quartile", "Q3" %}
{% assign q4 = published | where: "quartile", "Q4" %}
{% assign ssci = published | where: "ssci", true %}
{% assign esci = published | where: "esci", true %}

<div class="publication-stats" aria-label="Publication statistics">
  <div class="publication-stat publication-stat--green">
    <span class="publication-stat__value">{{ original_research | size }}</span>
    <span class="publication-stat__label">Original Research</span>
  </div>
  <div class="publication-stat publication-stat--purple">
    <span class="publication-stat__value">{{ conference_papers | size }}</span>
    <span class="publication-stat__label">Conference Papers</span>
  </div>
  <div class="publication-stat">
    <span class="publication-stat__value">{{ q1 | size }}</span>
    <span class="publication-stat__label">Q1</span>
  </div>
  <div class="publication-stat">
    <span class="publication-stat__value">{{ q2 | size }}</span>
    <span class="publication-stat__label">Q2</span>
  </div>
  <div class="publication-stat">
    <span class="publication-stat__value">{{ q3 | size }}</span>
    <span class="publication-stat__label">Q3</span>
  </div>
  <div class="publication-stat">
    <span class="publication-stat__value">{{ q4 | size }}</span>
    <span class="publication-stat__label">Q4</span>
  </div>
  <div class="publication-stat publication-stat--index">
    <span class="publication-stat__value">{{ ssci | size }}</span>
    <span class="publication-stat__label">SSCI</span>
  </div>
  <div class="publication-stat publication-stat--index">
    <span class="publication-stat__value">{{ esci | size }}</span>
    <span class="publication-stat__label">ESCI</span>
  </div>
</div>

<p class="publication-stats-note"><i class="fa-solid fa-circle-info" aria-hidden="true"></i> Counts include published outputs only. Ongoing work is displayed below but excluded from the statistics. “Original Research” excludes entries classified as reviews or conference papers.</p>

{% assign ongoing = site.data.publications | where: "status", "ongoing" %}
{% if ongoing.size > 0 %}
## Ongoing work

{% for pub in ongoing %}
<article class="publication-card">
  <div class="publication-citation">{{ pub.citation | markdownify }}</div>
  <div class="publication-meta">
    <span class="publication-badge publication-badge--ongoing">Ongoing</span>
    {% if pub.quartile %}<span class="publication-badge">{{ pub.quartile }}{% if pub.quartile_year %} · {{ pub.quartile_year }}{% endif %}</span>{% endif %}
  </div>
</article>
{% endfor %}
{% endif %}

{% assign journal_articles = published | where_exp: "item", "item.type != 'conference_paper'" %}
{% assign last_year = "" %}
{% for pub in journal_articles %}
  {% if pub.year != last_year %}
## {{ pub.year }}
    {% assign last_year = pub.year %}
  {% endif %}

<article class="publication-card">
  <div class="publication-citation">{{ pub.citation | markdownify }}</div>
  <div class="publication-links">
    {% if pub.doi %}<a href="{{ pub.doi }}" rel="noopener noreferrer"><i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i> DOI</a>{% endif %}
  </div>
  {% if pub.quartile or pub.ssci or pub.esci %}
  <div class="publication-meta" aria-label="Indexing information">
    {% if pub.ssci %}<span class="publication-badge publication-badge--index">SSCI</span>{% endif %}
    {% if pub.esci %}<span class="publication-badge publication-badge--index">ESCI</span>{% endif %}
    {% if pub.quartile %}<span class="publication-badge">{{ pub.quartile }}{% if pub.quartile_year %} · {{ pub.quartile_year }}{% endif %}</span>{% endif %}
  </div>
  {% endif %}
</article>
{% endfor %}

{% if conference_papers.size > 0 %}
## Conference papers

{% for pub in conference_papers %}
<article class="publication-card">
  <div class="publication-citation">{{ pub.citation | markdownify }}</div>
  <div class="publication-meta">
    <span class="publication-badge publication-badge--conference">Conference Paper</span>
  </div>
</article>
{% endfor %}
{% endif %}
