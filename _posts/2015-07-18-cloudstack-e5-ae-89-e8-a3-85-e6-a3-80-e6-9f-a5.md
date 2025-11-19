---
title: "CloudStack安装检查"
date: "2015-07-18 08:51:51"
slug: "cloudstack-e5-ae-89-e8-a3-85-e6-a3-80-e6-9f-a5"
layout: "post"
categories: ["CloudStack"]
tags: ["CloudStack", "全局配置", "版本"]
---
# CloudStack 版本

yum安装之后，不知道自己装的那个版本。
有2个查看的地方：
1、UI
[![version](/assets/images/2015/07/version.jpg)](/assets/images/2015/07/version.jpg)
2、DB
[codesyntax lang="mysql" doclinks="0"]

```
mysql> select * from version;
+----+---------+---------------------+----------+
| id | version | updated             | step     |
+----+---------+---------------------+----------+
|  1 | 4.0.0   | 2015-07-18 08:09:34 | Complete |
|  2 | 4.1.0   | 2015-07-18 00:09:55 | Complete |
|  3 | 4.2.0   | 2015-07-18 00:09:55 | Complete |
|  4 | 4.2.1   | 2015-07-18 00:09:55 | Complete |
|  5 | 4.3.0   | 2015-07-18 00:09:55 | Complete |
|  6 | 4.4.0   | 2015-07-18 00:09:55 | Complete |
|  7 | 4.4.1   | 2015-07-18 00:09:55 | Complete |
|  8 | 4.4.2   | 2015-07-18 00:09:55 | Complete |
|  9 | 4.5.0   | 2015-07-18 00:09:55 | Complete |
| 10 | 4.5.1   | 2015-07-18 00:09:55 | Complete |
+----+---------+---------------------+----------+
10 rows in set (0.00 sec)
```

[/codesyntax]
CloudStack的升级机制中，有自低版本向高版本升级过程，该过程目前不可逆。初始数据库版本为4.0.0.
该版本路径一直升级至4.5.1，其中间隔10个版本。以最后一个为当前版本号。

# 全局配置

## host

该项是主机与Hyperviser通信的IP，即private network IP。该项由系统初始化DB的时候默认填充。
多网卡环境中，可能与设定不符，需要查看并手动进行修改。添加主机不成功，或者系统虚拟机状态不对，都可能由此引发。
在升级或者改网的时候，主机IP改变而DB并不能实时检测此项，需要手动修改。
[![configuration1](/assets/images/2015/07/configuration1.jpg)](/assets/images/2015/07/configuration1.jpg)

## management.network.cidr

同上，也是同种用途
[![configuration2](/assets/images/2015/07/configuration2.jpg)](/assets/images/2015/07/configuration2.jpg)
