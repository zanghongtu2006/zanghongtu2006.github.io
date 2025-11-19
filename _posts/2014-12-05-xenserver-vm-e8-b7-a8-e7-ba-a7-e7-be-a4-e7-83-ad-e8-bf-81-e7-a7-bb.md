---
title: "XenServer VM 跨集群热迁移"
date: "2014-12-05 17:12:56"
slug: "xenserver-vm-e8-b7-a8-e7-ba-a7-e7-be-a4-e7-83-ad-e8-bf-81-e7-a7-bb"
layout: "post"
categories: ["IaaS"]
tags: ["xenserver", "migrate", "跨集群"]
---
刚发现的新功能，对于大部分运维来说，可能是雕虫小技了。
Mark一下，新大陆。。。
[![m1](/assets/images/2014/12/m1-300x187.jpg)](/assets/images/2014/12/m1.jpg)
[![m2](/assets/images/2014/12/m2-300x148.jpg)](/assets/images/2014/12/m2.jpg)
[![m3](/assets/images/2014/12/m3-300x163.jpg)](/assets/images/2014/12/m3.jpg)
如此操作，VM就会迁移到另一个集群中了。CPU，MEM，DISK，Network全复制。
