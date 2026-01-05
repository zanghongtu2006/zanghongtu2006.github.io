---
title: "CentOS6.4安装Docker"
date: "2014-12-16 11:36:58"
slug: "docker-e5-ae-89-e8-a3-85"
layout: "post"
categories: ["Docker"]
tags: ["docker"]
lang: zh
permalink: /zh/docker-e5-ae-89-e8-a3-85/
translations:
  zh: /zh/docker-e5-ae-89-e8-a3-85/
---
首先，需要安装EPEL仓库
```bash
# wget http://mirrors.yun-idc.com/epel/6/i386/epel-release-6-8.noarch.rpm
# rpm -ivh epel-release-6-8.noarch.rpm
```

安装docker-io
```bash
# yum -y install docker-io
```

启动docker服务
```bash
# /etc/init.d/docker start
Starting cgconfig service:                                 [  OK  ]
```

设置docker服务开机启动
```bash
# chkconfig docker on
```

测试是否正常工作
```bash
# docker run -i -t fedora /bin/bash
Unable to find image 'fedora' locally
fedora:latest: The image you are pulling has been verified
bfe0bb6667e4: Downloading  6.48 MB/259.4 MB 51m9s
511136ea3c5a: Already exists 
00a0c78eeb6d: Already exists 
```

下载中，由于网速原因，等待比较长一段时间后
```bash
# docker run -i -t fedora /bin/bash
Unable to find image 'fedora' locally
fedora:latest: The image you are pulling has been verified
bfe0bb6667e4: Pull complete 
511136ea3c5a: Already exists 
00a0c78eeb6d: Already exists 
Status: Downloaded newer image for fedora:latest
```
可以看出我们已经运行在docker容器中了
可以像Fedora一样操作了
