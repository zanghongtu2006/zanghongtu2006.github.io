---
title: "CloudStack修复bug"
date: "2014-07-15 17:26:25"
slug: "cloudstack-e4-bf-ae-e5-a4-8dbug"
layout: "post"
categories: ["Java", "CloudStack"]
tags: ["CloudStack", "bug", "patch"]
---
CloudStack应用越来越广，但是随着测试也遇到了越来越多的bug。

不想等待新版本发布而且又急于修复某些bug的童鞋，可以参考下本文内容。

CloudStack是java语言写成，发布时会发布为jar

一、先介绍下CloudStack版本控制

DB

cloud.version

该表中，存有version字段，存放该版本的版本号

例如：4.1.xxxxxxx （xxxxxx为时间戳）

META-INF

解压任一jar 包，会有META-INF目录

目录中有MANIFEST.MF存放版本信息

例如：

Specification-Version: 4.1.xxxxxxxxxx

Implementation-Version: 4.1.xxxxxxxxxx

CloudStack在启动时，会检查jar包中的版本信息是否和db中匹配

如果jar包中版本信息高于DB，则会启动自动升级

相等则正常启动

低于DB中版本信息，则会启动失败

二、了解了版本控制，就知道如果需要修复bug后，更新jar包的同时，必须修改Jar中的MANIFEST.MF

修改代码后，使用mvn命令编译

编译方式可以参考社区官网：<https://cwiki.apache.org/confluence/display/CLOUDSTACK/Setting+up+CloudStack+Development+Environment+on+Linux>

编译完成在每个工程目录下会产生target目录，目录下会生成对应jar包

例：server工程会生成 server/target/cloud-server-xx.jar

三、替换jar包

1>在windows下用winrar打开jar包，替换MANIFEST.MF中的版本信息为DB中的信息，重新打包

或者

用beyond compare打开安装环境中，与其同名的jar，直接比较两个jar包

此方法可以直接替换jar中的\*.class和MENIFEST.MF而不需要解压jar包

2>将新的jar包覆盖原有jar

3>重启mangement server
