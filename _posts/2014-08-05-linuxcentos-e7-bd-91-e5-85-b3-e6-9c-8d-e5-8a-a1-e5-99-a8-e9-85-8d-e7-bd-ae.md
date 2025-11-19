---
title: "[Linux]CentOS网关服务器配置"
date: "2014-08-05 17:41:04"
slug: "linuxcentos-e7-bd-91-e5-85-b3-e6-9c-8d-e5-8a-a1-e5-99-a8-e9-85-8d-e7-bd-ae"
layout: "post"
categories: ["CentOS"]
tags: ["Gateway"]
---
**1. 网关服务器上两张网卡：**
eth0 ：内网172.18.1.240
eth1：外网211.139.169.X

**2. 客户端机：**
172.18.1.x

**3. 网关服务器配置：**打开IP转发功能：

echo 1 > /proc/sys/net/ipv4/ip\_forward

建立nat 伪装：

iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE

iptables -t nat -A POSTROUTING -s 172.18.1.0/22 -o eth1 -j MASQUERADE

建立转发(特定子网的转发)：

iptables -A FORWARD -i eth0 -j ACCEPT

iptables -A FORWARD -s 172.18.1.0/22 -m state --state ESTABLISHED,RELATED -j ACCEPT

转自：<http://blog.csdn.net/cjy37/article/details/7104898>
