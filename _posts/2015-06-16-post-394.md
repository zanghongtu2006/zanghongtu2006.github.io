---
title: "Hadoop在CloudStack NAT环境中无法使用"
date: "2015-06-16 11:39:36"
slug: "post-394"
layout: "post"
categories: ["未分类"]
tags: []
draft: true
---
网友问题：在cloudstack 开启了hadoop三个节点。
分别是：h1 [外部ip:192.168.1.100 内网ip:10.0.0.1] h2 h3. 对h1做了静态NAT. 并配制了防火墙， 此时可以通过hadoop client访问h1,并可以创建目录，但不能上传文件，报错：
Exception in thread "main" org.apache.hadoop.ipc.RemoteException(java.io.IOException): File /text1/lg1.txt could only be replicated to 0 nodes instead of minReplication (=1). There are 0 datanode(s) running and no node(s) are excluded in this operation.
但是，将h1移出cloudstack管理， 直接使用192网络，此时上传文件正常。 求解
