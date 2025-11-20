---
layout: page
title: 分类
permalink: /categories/
redirect_to: /categories/
---

{% assign cats = site.categories | sort %}
{% for cat in cats %}
## <a id="{{ cat[0] | slugify }}"></a>{{ cat[0] }}

<ul>
  {% for post in cat[1] %}
  <li>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    <small>{{ post.date | date: "%Y-%m-%d" }}</small>
  </li>
  {% endfor %}
</ul>
{% endfor %}
