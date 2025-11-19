---
title: "Ubuntu下格式化xml文件"
date: "2016-03-20 11:54:03"
slug: "ubuntu-e4-b8-8b-e6-a0-bc-e5-bc-8f-e5-8c-96xml-e6-96-87-e4-bb-b6"
layout: "post"
categories: ["未分类"]
tags: []
---
安装tidy：
[codesyntax lang="bash"]

```
sudo apt-get install tidy
```

[/codesyntax]
使用tidy格式化xml文件：
[codesyntax lang="bash"]

```
cat ugly.xml | tidy -utf8 -xml -w 255 -i -c -q -asxml > pretty.xml
```

[/codesyntax]
