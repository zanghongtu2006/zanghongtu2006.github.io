---
title: "CloudStack自动代码审查（1）-cloud-style.xml"
date: "2015-06-11 11:52:39"
slug: "cloudstack-e8-87-aa-e5-8a-a8-e4-bb-a3-e7-a0-81-e5-ae-a1-e6-9f-a5-ef-bc-881-ef-bc-89-cloud-style-xml"
layout: "post"
categories: ["Java", "CloudStack"]
tags: ["代码", "CloudStack", "code-style", "maven"]
---
CloudStack在4.4版本中，加入了自动代码审查功能。对于不满足code-style的代码，在使用maven编译的过程中，会报错导致无法继续编译。
详细研究了一下代码审查功能的实现机制，总结至此。
./tools/checkstyle/src/main/resources/cloud-style.xml
[codesyntax lang="xml"]

```
<?xml version="1.0"?>
<!-- Licensed to the Apache Software Foundation (ASF) ...... License. -->
<!DOCTYPE module PUBLIC
    "-//Puppy Crawl//DTD Check Configuration 1.2//EN"
    "http://www.puppycrawl.com/dtds/configuration_1_2.dtd">

<module name="Checker">
  <module name="FileTabCharacter">
    <property name="eachLine" value="true" />
  </module>

  <module name="TreeWalker">
    <module name="LineLength">
      <property name="max" value="1024" />
    </module>

    <module name="RedundantImport" />
    <module name="UnusedImports" />
    <module name="MemberName">
      <property name="format" value="^_?[a-zA-Z0-9]*$" />
    </module>
	<module name="LocalFinalVariableName">
	  <property name="format" value="^[a-zA-Z][a-zA-Z0-9_]*$" />
	</module>
	<module name="StaticVariableName">
	  <property name="format" value="^(s_)?[a-z][a-zA-Z0-9]*$"/>
	</module>
	<module name="ConstantName">
	  <property name="format" value="^[a-zA-Z][a-zA-Z0-9_]*$"/>
	</module>

    <module name="PackageName" />
    <module name="ParameterName" />
    <module name="TypeName" />
    <module name="AvoidStarImport" />
  </module>
  <module name="RegexpSingleline">
    <!-- \s matches whitespace character, $ matches end of line. -->
    <property name="format" value="\s+$" />
    <property name="message" value="Line has trailing spaces." />
  </module>

  <!-- some modules that we should soon add <module name="MagicNumber"/> -->

  <!-- some modules that we should soon add -->

</module>
```

[/codesyntax]
该文件定义了code-style检查模块。内容是一个嵌套的module集合。每个module中，可以嵌套其它module或propertiy，property是module属性，用于标记检查的格式和错误提示。

# 顶层module

<module name="Checker">
定义代码检查module。

# 第二层module

嵌套了3个module
1、<module name="FileTabCharacter">
2、<module name="TreeWalker">
3、<module name="RegexpSingleline">
后续会添加<module name="MagicNumber"/>和其他的module

# 第三层module

## FileTabCharacter

[codesyntax lang="xml"]

```
<module name="FileTabCharacter">
    <property name="eachLine" value="true" />
</module>
```

[/codesyntax]

## TreeWalker

1、<module name="LineLength">
[codesyntax lang="xml"]

```
<module name="LineLength">
    <property name="max" value="1024" />
</module>
```

[/codesyntax]
单行最大不超过1024个字符
2、<module name="RedundantImport" />
检查是否有重复的import
3、<module name="UnusedImports" />
检查是否有未使用的import
4、<module name="MemberName">
[codesyntax lang="xml"]

```
<module name="MemberName">
    <property name="format" value="^_?[a-zA-Z0-9]*$" />
</module>
```

[/codesyntax]
检查成员变量命名是否遵循命名规则：以下划线开始，名字只包含英文大小写和阿拉伯数字
5、<module name="LocalFinalVariableName">
[codesyntax lang="xml"]

```
<module name="LocalFinalVariableName">
    <property name="format" value="^[a-zA-Z][a-zA-Z0-9_]*$" />
</module>
```

[/codesyntax]
检查final变量命名是否遵循命名规则：以英文大小写字符开始，名字只包含英文大小写和阿拉伯数字
6、<module name="StaticVariableName">
[codesyntax lang="xml"]

```
<module name="StaticVariableName">
    <property name="format" value="^(s_)?[a-z][a-zA-Z0-9]*$"/>
</module>
```

[/codesyntax]
检查static变量命名是否遵循命名规则：以s\_开始，名字只包含英文大小写和阿拉伯数字
7、<module name="ConstantName">
[codesyntax lang="xml"]

```
<module name="ConstantName">
    <property name="format" value="^[a-zA-Z][a-zA-Z0-9_]*$"/>
</module>
```

[/codesyntax]
检查常量命名是否遵循命名规则：名字只包含英文大小写和阿拉伯数字
8、<module name="PackageName" />
9、<module name="ParameterName" />
10、<module name="TypeName" />
11、<module name="AvoidStarImport" />

## RegexpSingleline

[codesyntax lang="xml"]

```
<module name="RegexpSingleline">
    <!-- \s matches whitespace character, $ matches end of line. -->
    <property name="format" value="\s+$" />
    <property name="message" value="Line has trailing spaces." />
</module>
```

[/codesyntax]
format：空行是否有空格，或者每行末尾是否有空格
message：如果检查空行有空格或者每行末尾有空格，则返回错误值：Line has trailing spaces.
