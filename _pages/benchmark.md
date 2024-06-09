---
layout: page
title: Benchmark Tasks
permalink: /benchmark/
nav: true
nav_order: 4

[//]: # (display_categories: [work, fun])
[//]: # (display_categories: [dataset])
horizontal: true
social: true

---

## Neural Reconstruction

In our single-traversal dynamic scene reconstruction experiments, we selected 10 different locations, each with one traversal, aiming to capture and represent complex urban environments. 
For our multitraversal environment reconstruction experiments, we selected a total of 50 traversals. This comprised 10 unique locations, with 5 traversals for each location, enabling us to capture variations in illuminating conditions and weather.


**Single-traversal experiments**: 
PVG achieves higher SSIM scores and better LPIPS scores, indicating enhanced structural details. 
EmerNeRF excels in PSNR, likely due to its novel approach of dynamic-static decomposition. 
EmerNeRF and PVG both demonstrate the ability to perfectly render dynamic objects like moving cars, whereas iNGP and 3DGS exhibit relatively poor performance in this regard.

**Multitraversal experiments**:
The main challenge is to handle appearance variations and dynamic objects across repeated traversals over time.
In our experiment, iNGP achieves the best similarity metrics since it preserves the most information about dynamic objects. 
RobustNeRF performs best in eliminating dynamic objects, albeit at the cost of rendering static objects with less detail. 
SegFormer achieves superior visual results compared to the other two methods. 
Yet the shadows of cars are not comletely removed, likely due to the inadequate recognition of shadows by semantic segmentation models.

<br/>

<p style="text-align: center;">
    <img src="/MARS/assets/img/nerf_quantitative_result.png" alt="drawing" style="width:600px;"/>
</p>

<p style="text-align: center;">
    <span style="font-weight: bold;">Quantitative results</span>
</p>

<br/>

<p style="text-align: center;">
    <img src="/MARS/assets/img/nerf_qualitative_1.jpg" alt="drawing" style="width:500px; margin: 0 20px 20px 0;"/>
    <img src="/MARS/assets/img/nerf_qualitative_2.jpg" alt="drawing" style="width:500px; margin: 0 20px 20px 0;"/>
</p>

<p style="text-align: center;">
    <span style="font-weight: bold; text-align: center;">Qualitative results</span>
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
