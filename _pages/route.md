---
layout: page
title: Route
permalink: /route/
nav: true
nav_order: 2

[//]: # (display_categories: [work, fun])
[//]: # (display_categories: [dataset])
horizontal: true
social: true

---

## Route Map with Multitraversal locations

May Mobility is currently focusing on microservice transportation, running shuttle vehicles within a fixed region through various routes and directions.

We selected 67 locations within the vehicles' operation area for multitraversal data collection. 
As demonstrated, the vehicles' routes are randomly distributed across the area.
Note: the 67 locations are indexed from 0-66, but #2 has been removed due to scarcity of data.

<p style="text-align: center;">
    <img src="../assets/img/route/map.png" alt="drawing" style="width:800px;"/>
</p>

<br/>

---
The full route is over 20 kilometers long, encompassing urban, residential, highway, and university campus areas with diverse surroundings in terms of traffic, vegetation, buildings, and road marks.

The fleet operates nonstop every workday across the year, therefore covering various lighting and weather conditions with its data.

<p style="text-align: center;">
    <img src="../assets/img/route/urban_rain.jpg" alt="drawing" style="width:300px; margin: 0 20px 20px 0;"/>
    <img src="../assets/img/route/residential_sunny.jpg" alt="drawing" style="width:300px; margin: 0 20px 20px 0;"/>
    <img src="../assets/img/route/bridge_sunny.jpg" alt="drawing" style="width:300px; margin: 0 20px 20px 0;"/>
    <img src="../assets/img/route/narrow_snow.jpg" alt="drawing" style="width:300px; margin: 0 20px 20px 0;"/>
    <img src="../assets/img/route/highway_sunny.jpg" alt="drawing" style="width:300px; margin: 0 20px 20px 0;"/>
    <img src="../assets/img/route/openfield_snow.jpg" alt="drawing" style="width:300px; margin: 0 20px 20px 0;"/>
</p>

<br/>

---

#### The multiagent and multitraversal datasets are now available for download!

<br/>

<!-- pages/datasets.md -->
<div class="projects">
{% if site.enable_project_categories and page.display_categories %}
  <!-- Display categorized projects -->
  {% for category in page.display_categories %}
  <a id="{{ category }}" href=".#{{ category }}">
    <h2 class="category">{{ category }}</h2>
  </a>
  {% assign categorized_projects = site.projects | where: "category", category %}
  {% assign sorted_projects = categorized_projects | sort: "importance" %}
  <!-- Generate cards for each project -->
  {% if page.horizontal %}
  <div class="container">
    <div class="row row-cols-1 row-cols-md-2">
    {% for project in sorted_projects %}
      {% include projects_horizontal.liquid %}
    {% endfor %}
    </div>
  </div>
  {% else %}
  <div class="row row-cols-1 row-cols-md-3">
    {% for project in sorted_projects %}
      {% include projects.liquid %}
    {% endfor %}
  </div>
  {% endif %}
  {% endfor %}

{% else %}

<!-- Display projects without categories -->

{% assign sorted_projects = site.projects | sort: "importance" %}

  <!-- Generate cards for each project -->

{% if page.horizontal %}

  <div class="container">
    <div class="row row-cols-1 row-cols-md-2">
    {% for project in sorted_projects %}
      {% include projects_horizontal.liquid %}
    {% endfor %}
    </div>
  </div>
  {% else %}
  <div class="row row-cols-1 row-cols-md-3">
    {% for project in sorted_projects %}
      {% include projects.liquid %}
    {% endfor %}
  </div>
  {% endif %}
{% endif %}
</div>

<br/>

---
