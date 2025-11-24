---
layout: post
lang: zh
translations:
  en: /en/cloudstack-e6-97-a0-e6-b3-95-e6-b7-bb-e5-8a-a0-e6-a8-a1-e6-9d-bf-e5-92-8ciso/
  de: /de/cloudstack-e6-97-a0-e6-b3-95-e6-b7-bb-e5-8a-a0-e6-a8-a1-e6-9d-bf-e5-92-8ciso/
title: "CloudStack无法添加模板和iso"
date: "2014-08-05 16:52:08"
slug: "cloudstack-e6-97-a0-e6-b3-95-e6-b7-bb-e5-8a-a0-e6-a8-a1-e6-9d-bf-e5-92-8ciso"
categories: ["CloudStack"]
tags: ["CloudStack", "添加模板"]
---
做了N久的CloudStack二次开发，最近越来越多的人开始使用CloudStack。
通常会遇到添加模板和iso不成功的问题。
表现为注册了template/iso之后，"已就绪" "状态" "大小" 等选项都为空，或者提示no route to host等现象
 
CloudStack是通过SSVM进行template/iso上传和下载，所以基本可以判定为SSVM网络有问题
这样就可以做以下检查：
1、内建模板不存在（"已就绪" "状态" "大小" 等选项都为空多发生在这种情况）：
CS默认有2种模板，系统虚拟机模板[SystemVM Template (XenServer)]和内建模板[CentOS 5.6(64-bit) no GUI (XenServer)]
在ssvm正常启动之后，会连接management-server 的8250端口，成功连接后，UI上就可以看到以上两个模板。
如果此时没有内建模板的信息，则说明ssvm没能正常连接management-server。
这种情况多会发生在全局配置错误。相关项为：management.network.cidr，host，secstorage.allowed.internal.cidr
<1> 如果management-server存在多个网卡，默认cloudstack会选择route中为default的那个网卡设置management.network.cidr和host，如果该项并非用来连接host和ssvm private ip的网络，则需要修改为正确网络，ssvm启动后，会根据这两个值来配置路由表，如果错误则无法连接到management-server。
解决方案：这种情况需要修改全局配置后，重启management-server，然后破坏掉ssvm，等待系统重建
<2>secstorage.allowed.internal.cidr 设置为0.0.0.0/0
经常会发生在网络情况比较单一的环境，比如基本模式或者高级模式但是public ip和private ip在同一网段中，会导致SSVM路由表错误，正常SSVM路由default 网卡为eth2，即public，此时会变为eth1，即private，由于其防火墙限制，导致无法上传或下载模板
解决方案：这种情况需要修改全局配置，将secstorage.allowed.internal.cidr设为正确值，如果有多个cidr可以用逗号分隔，重启management-server，然后重启ssvm
 
2、内建模板已存在
内建模板已经显示在UI上，说明SSVM已经成功连接到management-server。
至于内建模板，我这里下载基本上不会成功，原因大体就是因为网速太慢，半天下一点，断了重新下。可以尝试在db中修改url从本地下载。
<1> no route to host
这种情况多发生在SSVM的public和private在同一网段的情况下，很多人的测试环境受实际因素影响，并不能隔离public和private，而是都使用同一网段。并且上传template/iso所用的http server也在同一网段。
CS默认会通过public ip进行下载，如果http server和 private ip处于同一网段的时候，则会尝试使用private ip进行下载。由于很多新人刚刚使用CS的时候，并不知道还有secstorage.allowed.internal.cidr 这样的全局配置，所以并未进行相关设置，这样就会导致private ip被防火墙阻拦而无法进行下载
解决方案：将private ip所在网段的cidr写入secstorage.allowed.internal.cidr ，并重启ms，重启SSVM
<2> 有人发现有此选项，但为求省事，设置secstorage.allowed.internal.cidr 为0.0.0.0/0
此项设置并不符合CS的设计，不过大部分环境中可以正常使用，所以也少有人会注意到全局设置中的不能设置为0.0.0.0的提示。
如1.2中所描述的环境，则很有可能会出现路由表错误而无法正常使用的问题。
<3> 下载一半后中断，无法继续下载。
此种情况见过多次，但是自己的环境中并未重现。
跟踪代码发现下载流的size不能满足默认大小，可以试着尝试修改SSVM的service\_offering，增加SSVM的内存。**这个仅为猜测，有待将来重现后再进行跟踪调试**
