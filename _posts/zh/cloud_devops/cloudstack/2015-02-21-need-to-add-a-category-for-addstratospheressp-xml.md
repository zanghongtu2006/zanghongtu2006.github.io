---
layout: post
title: "Need to add a category for addStratosphereSsp.xml "
date: "2015-02-21 10:37:18"
slug: "need-to-add-a-category-for-addstratospheressp-xml"
categories: ["CloudStack"]
tags: ["CloudStack"]
lang: zh
permalink: /zh/need-to-add-a-category-for-addstratospheressp-xml/
translations:
  zh: /zh/need-to-add-a-category-for-addstratospheressp-xml/
---
CloudStack 4.2 源码编译过程中出现如下错误

```text
Traceback (most recent call last):  
  File "/opt/cloudstack/tools/apidoc/gen_toc.py", line 192, in <module>  
    category = choose_category(fn)  
  File "/opt/cloudstack/tools/apidoc/gen_toc.py", line 172, in choose_category  
    (fn, __file__))  
Exception: Need to add a category for addStratosphereSsp.xml to /opt/cloudstack/tools/apidoc/gen_toc.py:known_categories  
```

```text
[ERROR] Failed to execute goal org.codehaus.mojo:exec-maven-plugin:1.2.1:exec (compile) on project cloud-apidoc: Command execution failed. Process exited with an error: 1 (Exit value: 1) -> [Help 1]  
[ERROR]   
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.  
[ERROR] Re-run Maven using the -X switch to enable full debug logging.  
[ERROR]   
[ERROR] For more information about the errors and possible solutions, please read the following articles:  
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoExecutionException  
[ERROR]   
[ERROR] After correcting the problems, you can resume the build with the command  
[ERROR]   mvn <goals> -rf :cloud-apidoc
```

解决：
在gen_toc.py 加入addStratosphereSsp相关项

```python
known_categories = {  
......  
    'UCS' : 'UCS',  
    'Ucs' : 'UCS',  
    'CacheStores' : 'Cache Stores',  
    'CacheStore' : 'Cache Store',  
    'addStratosphereSsp' : 'Add StratosphereSsp'  
}
```
重新编译，顺利通过
