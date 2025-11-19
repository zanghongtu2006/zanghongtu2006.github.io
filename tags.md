---
layout: page
title: 标签
permalink: /tags/
---

{% assign tags = site.tags | sort %}
<ul>
{% for tag in tags %}
  <li>
    <a href="#{{ tag[0] | slugify }}">{{ tag[0] }} ({{ tag[1].size }})</a>
  </li>
{% endfor %}
</ul>

{% for tag in tags %}
### <a id="{{ tag[0] | slugify }}"></a>{{ tag[0] }}
<ul>
  {% for post in tag[1] %}
    <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> <small>{{ post.date | date: "%Y-%m-%d" }}</small></li>
  {% endfor %}
</ul>
{% endfor %}
