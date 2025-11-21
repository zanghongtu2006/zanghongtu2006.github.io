---
title: "CloudStack 代码阅读（一）—— cloud-api"
date: "2015-03-15 17:23:31"
slug: "post-339"
layout: "post"
categories: ["未分类"]
tags: []
draft: true
---
CloudStack 开放出一系列API，对整个云平台进行管理。
CloudStack的所有API，都在cloud-api这个工程中。
So，我们首先从cloud-api这个工程入手，看一下整个CloudStack的代码结构。

# 简介

cloud-api包含所有的CloudStack API和其它模块中和API相关的接口定义。

# 代码结构

 
org.apache.cloudstack.api.command.admin.\*
org.apache.cloudstack.api.command.user.\*
这两部分代码，是所有CS的API，分为admin/user两部分。
org.apache.cloudstack.api.response
API返回值的类声明
