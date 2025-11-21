---
layout: post
lang: zh
title: "Django开发demo"
date: "2014-07-15 17:32:02"
slug: "django-e5-bc-80-e5-8f-91demo"
categories: ["Python", "Programme"]
tags: ["python", "diango"]
---
接上篇继续开发Django 第一个Demo，以Html格式显示当前时间和日期。

新建views.py文件，写入以下代码：

`from django.http import HttpResponse
import datetime`def current\_datetime(request):
now = datetime.datetime.now()
html = "It is now %s."
return  HttpResponse(html)

定义了一个叫做 current\_datetime 的函数。这就是所谓的视图函数（view function）。每个视图函数都以一个 HttpRequest 对象为第一个参数，该参数通常命名为 request  
获取当前系统时间，拼成html格式，创建一个HttpResponse对象并返回

修改url.py，将路径映射到视图

`from django.conf.urls import patterns, include, url
from DjangoTest.views import current_datetime
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
urlpatterns = patterns(",
# Examples:
# url(r'^$', 'DjangoTest.views.home', name='home'),
# url(r'^DjangoTest/', include('DjangoTest.foo.urls')),
# Uncomment the admin/doc line below to enable admin documentation:
# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
# Uncomment the next line to enable the admin:
# url(r'^admin/', include(admin.site.urls)),
(r‘^time/$’, current_datetime)
)`

import刚刚生成的视图函数

r'^time/$' 是一个简单的正则表达式，匹配所有指向URL /time/的请求，都由current\_time这个视图函数来处理

r'^time/$' 中的 r 表示 '^time/$' 是一个原始字符串。这样一来就可以避免正则表达式有过多的转义字符

命令 python manage.py runserver 从同一目录载入文件 settings.py 。 该文件包含了这个特定的Django实例所有的各种可选配置，其中一个最重要的配置就是 ROOT\_URLCONF 。 ROOT\_URLCONF 告诉Django哪个Python模块应该用作本网站的 URLconf。
系统自动生成的 settings.py 里 ROOT\_URLCONF 默认设置是 urls.py
当访问 URL /time/ 时，Django 根据 ROOT\_URLCONF 的设置装载 URLconf 。 然后按顺序逐个匹配URLconf里的URLpatterns，直到找到一个匹配的。当找到这个匹配 的URLpatterns就调用相关联的view函数，并把 HttpRequest 对象作为第一个参数。
