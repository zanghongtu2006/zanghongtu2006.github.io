---
layout: default
title: 分类
permalink: /pages/class.html
---
<div class="home">
<p>但行好事, 莫问前程。</p><br/>
    {% assign categories = site.categories | sort %}
	{% for category in categories %} 
	      		<div class="panel panel-primary">
	        			<div class="panel-heading center" id="{{ category[0] }}" name="{{ category[0] }}">{{ category[0] }}</div>
			              {% for post in category[1] %}
			                 <a  href='{{ post.url }}'  class="list-group-item clearfix pjaxlink">
				            {{post.title}}
				            <span class="badge">{{ post.date | date:"%Y年%m月%d日" }}</span>
				             </a>
			              {% endfor %}
			   </div>
	{% endfor %}
	
</div>
<div>
</div>