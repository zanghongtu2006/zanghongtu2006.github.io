---
layout: post
title: "CloudStack4.2源码编译错误"
date: "2014-12-15 18:38:50"
slug: "cloudstack4-2-e6-ba-90-e7-a0-81-e7-bc-96-e8-af-91-e9-94-99-e8-af-af"
categories: ["CloudStack"]
tags: []
lang: zh
permalink: /zh/cloudstack4-2-e6-ba-90-e7-a0-81-e7-bc-96-e8-af-91-e9-94-99-e8-af-af/
translations:
  zh: /zh/cloudstack4-2-e6-ba-90-e7-a0-81-e7-bc-96-e8-af-91-e9-94-99-e8-af-af/
---
因编译api-doc失败，导致整个项目编译不能通过
错误如下：

```text
Traceback (most recent call last):
  File "/opt/cloudstack_local/tools/apidoc/gen_toc.py", line 192, in <module>
    category = choose_category(fn)
  File "/opt/cloudstack_local/tools/apidoc/gen_toc.py", line 172, in choose_category
    (fn, __file__))
Exception: Need to add a category for addStratosphereSsp.xml to /opt/cloudstack_local/tools/apidoc/gen_toc.py:known_categories
```

检查/opt/cloudstack_local/tools/apidoc/gen_toc.py 代码  
192行，category = choose_category(fn)  
fn 为传入参数解析获得，应该是xml文件的文件名  
172行，此处需要传入的参数在known_categories中  
此处传入为：addStratosphereSsp.xml，但是known_categories中并没有想关内容，手动添加一行  

```
'addStratosphereSsp' : 'Stratosphere Ssp'
```
重新编译
