---
layout: post
lang: zh
title: "CloudStack搭建KVM多网卡环境"
date: "2014-07-15 17:33:30"
slug: "cloudstack-e6-90-ad-e5-bb-bakvm-e5-a4-9a-e7-bd-91-e5-8d-a1-e7-8e-af-e5-a2-83"
categories: ["CloudStack"]
tags: ["CloudStack", "kvm", "多网卡"]
---
软件环境：agent：CentOS 6.3，minimal安装，CPU启用VT

    management server：CentOS 6.3，minimal安装

    存储：CentOS 6.3 搭建在management server上

网络规划：management server：2个网卡，eth0:10.10.25.10（外部访问）eth1:192.168.1.10（管理网段，与kvm通信，提供nfs）

    agent：2个网卡，eth0:10.10.25.11，eth1:192.168.1.11（管理网段）

    public ip：10.10.25.21~10.10.25.30

    private ip：192.168.1.21~192.168.1.30

1 、在agent 上先搭建网桥：

`# brctl addbr cloudbr0
# brctl addif cloudbr0 eth0
# brctl addbr cloudbr1
# brctl addif cloudbr1 eth1`

修改网卡配置，使eth0和eth1分别通过cloudbr0和cloudbr1通信

ifcfg-eth0:

`DEVICE=eth0
BOOTPROTO=none
HWADDR=00:50:56:90:4E:97
NM_CONTROLLED=yes
ONBOOT=yes
TYPE=Ethernet
UUID=f50419b9-b29a-4be2−b5a5-8639d5125d2c
BRIDGE=cloudbr0`

ifcfg-cloudbr0:

`DEVICE=cloudbr0
TYPE=Bridge
BOOTPROTO=none
ONBOOT=yes
IPADDR=10.10.25.71
NETMASK=255.255.255.0
GATEWAY=10.10.25.1
DNS1=8.8.8.8
DNS2=8.8.4.4
STP=yes`

2、修改主机名：

`# hostname kvm.test.cloud`

修改/etc/hosts和/etc/sysconfig/network，将主机名写入文件中，重启agent主机

3、安装agent

yum或下载安装包都可以

4、修改管理服务主机名

`# hostname manage.test.cloud`

修改/etc/hosts和/etc/sysconfig/network，将主机名写入文件中，重启主机

5、准备主存储和二级存储

创建目录/export/primary和/export/secondary

我之前保存了systemvm template和builtin template

所以直接复制到/export/secondary中即可，目录如下：

/export/secondary/template/tmpl/1/3 /export/secondary/template/tmpl/1/4

编辑/etc/exports写入以下内容

`/export/ *(rw,async,no_root_squash)`

启动nfs服务

`# service nfs start`

6、关闭management-server 防火墙和SELinux

7、安装management-server

8、初始化db，按提示步骤添加资源域

![](http://img.blog.csdn.net/20130820173604781?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvdTAxMTY1MDU2NQ==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/Center)

此处我设置guest和public使用eth0，management使用eth1

所以guest和public的Edit 输入cloudbr0

management输入cloudbr1

其余按提示输入相应信息即可完成

9、部署完成，启用资源域
