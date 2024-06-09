---
layout: page
title: Vehicle Setup
permalink: /setup/
nav: true
nav_order: 3

[//]: # (display_categories: [work, fun])
[//]: # (display_categories: [dataset])
horizontal: true
social: true

---

## Sensor Specifications

Each vehicle is mounted with one LiDAR, three narrow angle RGB cameras, three wide angle RGB fisheye cameras, one IMU, and one GPS.
All sensor data sampled to 10Hz for synchronization.

| Sensor                      | Details                                                                                                                               |
|-----------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| 1 $$\times$$ LiDAR          | 10Hz, 128 channel, horizontal FoV $$360^\circ$$, vertical FoV $$40^\circ$$                                                            |
| 3 $$\times$$ RGB Camrea     | 10Hz, original resolution $$1440 \times 928$$, sampled to $$720 \times 464$$, Horizontal FoV $$60^\circ$$, Vertical FoV $$40^\circ$$  |
| 3 $$\times$$ Fisheye Camrea | 10Hz, original resolution $$1240 \times 728$$, sampled to $$620 \times 364$$, horizontal FoV $$140^\circ$$, vertical FoV $$88^\circ$$ |
| 1 $$\times$$ IMU            | 10Hz, velocity, angular velocity, acceleration                                                                                        |
| 1 $$\times$$ GPS            | 10Hz, longitude, latitude, elevation                                                                                                  |


<br/>

---

## Sensor Locations & coordinate frames
<p style="text-align: center;">
    <img src="../assets/img/vehicle_setup.jpg" alt="drawing" style="width:800px;"/>
</p>

<br/>

---

#### The multiagent and multitraversal datasets are now available for download!

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
