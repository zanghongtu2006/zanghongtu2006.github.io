---
title: "centos VLAN配置(vconfig)"
date: "2014-08-05 17:40:08"
slug: "centos-vlan-e9-85-8d-e7-bd-aevconfig"
layout: "post"
categories: ["CentOS"]
tags: ["vlan", "centos"]
---
1、安装vconfig并加载8021q模块

# modprobe 8021q

2、配置vlan并启动网卡

# vconfig add eth0 107

# ifconfig eth0.107 10.1.1.254 netmask 255.255.255.0
