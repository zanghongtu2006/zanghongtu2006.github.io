---
layout: post
lang: zh
translations:
  en: /en/cloudstack-physical-network-architecture/
  de: /de/cloudstack-physical-network-architecture/
title: "CloudStack 物理网络架构"
date: "2014-07-15 17:28:08"
slug: "cloudstack-physical-network-architecture"
categories: ["CloudStack", "网络"]
tags: ["CloudStack", "physical", "network"]
---
**原文地址：<http://www.shapeblue.com/cloudstack/understanding-cloudstacks-physical-networking-architecture/>**

**翻译仅供参考**

理解并配置CloudStack中某个主机物理网络连接，在一开始的时候可能会显得很混乱。软件定义网络（SDN）的设置大大简化了某些方面的配置，但是其整合到CloudStack并未完全成熟，并且它并不能在任何情况下都是正确的解决方案。

在本文中， Paul Angus，ShapeBlue的云计算架构师，云技术专家，将会揭开一些领域，这些领域可能会导致人们对CloudStack物理网络架构方面理解混乱。

### 物理主机: 物理主机vs. 逻辑主机

混乱的根源之一：当人们提到CloudStack中的“host”，他们可能提到的是两个不同的东西——物理主机和与Cloudstack通信的主机（逻辑主机即hyperviser）。物理主机可以理解为包含CPU，内存，网卡等等的物理设备；（通过管理网络）与Cloudstack通信的主机则理解为物理主机内的hyperviser。举例说明：公共网络（public traffic）能够连接到物理主机（这样可以让系统虚拟机连接到外部网络），但不是逻辑上的host（hyperviser）。

您的物理网络拓扑结构首先取决于您所要实施的资源域类型。从物理网络来看，CloudStack有2种网络模式，“基本”和“高级”。

### 基本模式

在基本模式中，只有一种物理网络，因为没有VLAN隔离。但是你仍然可以通过多个物理网卡来区分物理网络。

基本模式中，可以只有一个来宾网络（guest netowrk）而不需要公有网络（public network）。

![](http://img.blog.csdn.net/20130831165411390)

### Advanced Zones

高级模式中，Cloudstack允许一个public network和创建多个guest network，无论物理的还是逻辑上的（通常使用VLAN区分）。

Use cases for additional physical guest networks could be to create physically separate links from the hosts to a non-CloudStack network segment in a datacentre – for instance an MPLS network

其他用例中，可以启用钻用的来宾网络，这些网络只用由特定域或用户使用，或者提供更高速度的来宾网络，例如：10GB vs 1GB

![](http://img.blog.csdn.net/20130831165709093)

### 网络标签（Network Labels)

配置中最重要的部分是网络标签。在ESXi主机中，这指的是主机的vSwitch，KVM则是已经创建好的网桥的名字，Xenserver中是network 的名字（Xenserver对每个网卡或bongding都会创建一个network）。

网络标签告诉CloudStack主机中的物理网络接口和各个虚拟网络（客户虚拟机和系统虚拟机）的对应关系。SSVM有4个网卡，public，private，storage和mangement，并且他们能够正确连接到主机物理网卡的虚拟网络上是非常重要的。网络标签的名字可以随意取，但是最好使用一个具有提示性的名称。

![](http://img.blog.csdn.net/20130831172603171)

### 存储流量（Storage Traffic）

在各种Cloudstack网络流量类型中，存储流量经常引发最多的歧义。“storage traffic”和“storage network”指的是存储网络流量，快照（备份），ISO和模板是通过该网络向二级存储传入或传出的所有流量。

默认状况下，Cloudstack的主存储和二级存储的流量经过management 网络。二级存储流量可以配置为使用一个和管理网络独立的网络（存储网络）。也可以在hyperviser层配置单独的主存储网络——另一个话题。

分隔二级存储网络和管理网络（主存储网络和二级存储网络）的好处可以在以下情况中看出来：（1）创建一个客户虚拟机，需要从二级存储向主存储复制模板，（2）创建磁盘快照的时候，磁盘进行从主存储复制到二级存储。

### 基本网络（Basic Network Traffic）

在基本网络中，所有流量都经过同一个网卡，并且所有类型的网络都有同样的标签。这是不推荐的。

![](http://img.blog.csdn.net/20130831174415046)

management，storage，guest流量可以通过使用主机上不同标签的物理网卡区分。你既可以使用相同的交换机也可以使用不同的交换机或者相同交换机但是不同的vlan。将不同网络连接到同一个交换机会带来额外的进出该主机的流量。

![](http://img.blog.csdn.net/20130831174949453)

将网卡连接到不同vlan（通过交换机配置）提供了额外的吞吐量，和guest网络的安全性，使其与management和storage隔离。其最好的方法应该是在基本资源域中，guest网络通过一个独立的网卡——至少需要一台主机上有2个网卡。

![](http://img.blog.csdn.net/20130831175637375)

### 高级网络 Advanced Network Traffic

在高级网络中，CloudStack可以在逻辑上，通过使用VLAN tag来区分不同的流量。在某些方面，比基本网络更容易实现隔离的配置。你只需要在交换机上的端口上，为你所需要用到的vlan设置trunk即可。

但是，你仍然要区分物理网络来提高吞吐量和潜在的安全性。再次，这是通过为每个网络接口映射网络标签来实现的，你将会使用流量标签来使流量通过你所希望的网卡。

![](http://img.blog.csdn.net/20130831180550765)

### 主机内部 Inside the Host

将这些都结合在一起，一个包含2个网卡的高级资源域的逻辑图和物理图如下：

![](http://img.blog.csdn.net/20130831180818921)

### 总结

本文解释了一些关键概念和术语，配置基本或者高级资源域中物理网络的关键。特别是文章展示了物理网络中，CloudStack各种类型的网络。

### About the author

Paul Angus 是ShapeBlue的高级顾问和云计算架构师，云计算专家。他曾基于Apache CloudStack和Citrix CloudPlatform设计过多个CloudStack客户环境，遍布4大洲。
