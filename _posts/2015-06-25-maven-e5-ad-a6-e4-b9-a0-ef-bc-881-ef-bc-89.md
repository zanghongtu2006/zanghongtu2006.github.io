---
title: "Maven学习（1）"
date: "2015-06-25 19:48:07"
slug: "maven-e5-ad-a6-e4-b9-a0-ef-bc-881-ef-bc-89"
layout: "post"
categories: ["编程开发"]
tags: ["maven"]
---
**最简单的maven pom文件：**
[codesyntax lang="xml"]

```
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.mycompany.app</groupId>
    <artifactId>my-app</artifactId>
    <version>1</version>
</project>
```

[/codesyntax]
 
文件包含以上几个POM元素：
<project>:根
<modelVersion>：Model版本，一般设置为4.0.0
<groupId>：Project Group
<artifactId>：Project ID
<version>：Project Version
如上设置后，完整的项目名称为com.mycompany.app:my-app:1。
Maven需要很多POM配置项，如果没有写明的，会读取Maven的默认配置。
**继承：**
[codesyntax lang="text"]

```
.
|-- my-module
|   `-- pom.xml
`-- pom.xml
```

[/codesyntax]
 
建立一个子项目my-module，包含在刚刚建立的父项目my-app中
[codesyntax lang="xml"]

```
<project>
    <parent>
        <groupId>com.mycompany.app</groupId>
        <artifactId>my-app</artifactId>
        <version>1</version>
    </parent>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.mycompany.app</groupId>
    <artifactId>my-module</artifactId>
    <version>1</version>
</project>
```

[/codesyntax]
 
加入了<parent>标签，里面写了父工程的信息。
由此可见，parent和当前工程groupId，version都相同，如果不需要特别指定这些信息，也可以省略使其直接继承parent。
[codesyntax lang="xml"]

```
<project>
    <parent>
        <groupId>com.mycompany.app</groupId>
        <artifactId>my-app</artifactId>
        <version>1</version>
    </parent>
    <modelVersion>4.0.0</modelVersion>
    <artifactId>my-module</artifactId>
</project>
```

[/codesyntax]
**另一种parent结构：**
[codesyntax lang="text"]

```
.
 |-- my-module
 |   `-- pom.xml
 `-- parent
     `-- pom.xml
```

[/codesyntax]
子工程并非在parent工程中，或者parent工程在其他目录
[codesyntax lang="xml"]

```
<project>
    <parent>
        <groupId>com.mycompany.app</groupId>
        <artifactId>my-app</artifactId>
        <version>1</version>
        <relativePath>../parent/pom.xml</relativePath>
    </parent>
    <modelVersion>4.0.0</modelVersion>
    <artifactId>my-module</artifactId>
</project>
```

[/codesyntax]

```
<relativePath> 指定parent路径
```
