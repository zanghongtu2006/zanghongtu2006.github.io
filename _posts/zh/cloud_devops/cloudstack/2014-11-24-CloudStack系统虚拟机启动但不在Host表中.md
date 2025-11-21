---
title: "CloudStack系统虚拟机启动但不在Host表中"
date: "2014-11-24 16:39:27"
slug: "cloudstack-e7-b3-bb-e7-bb-9f-e8-99-9a-e6-8b-9f-e6-9c-ba-e5-90-af-e5-8a-a8-e4-bd-86-e4-b8-8d-e5-9c-a8host-e8-a1-a8-e4-b8-ad"
layout: "post"
categories: ["CloudStack"]
tags: ["CloudStack"]
---
今天有网友问到这个问题，CloudStack中，系统虚拟机正常启动，Running状态。
但是在host表中没有相应项，上传下载模板等功能也不正常。
原因：系统虚拟机启动之后，会通过管理网段主动连接management-server。
链接成功后，则会在host表中写入相关记录，连接失败的话，会一直处于异常但Running的状态。
查找问题步骤：
1、vm已经启动，说明系统基本环境可用，可以排除主存储，二级存储和hyperviser的连接问题。
2、系统虚拟机无法连接management-server，但网络又是可用的，基本可以定位到设置有误。
3、查看全局配置:host, management.network.cidr,这两个参数
host：management-server ip，初始化db的时候，自动写入，该项是最容易出问题的。
应该为management-server的private IP，自动写入则可能写成其他网段IP。
如果更换过management-server的IP，则需要在启动后，修改此项并重启management-server。
management.network.cidr：管理网段cidr
这两项需要和系统虚拟机的管理网段相同
系统虚拟机启动后，会根据这两项参数设置路由表，使系统虚拟机跟mangement-server连接。
修改这两项之后，重启management-server。
如果无效，破坏掉系统虚拟机使其重新生成即可。
