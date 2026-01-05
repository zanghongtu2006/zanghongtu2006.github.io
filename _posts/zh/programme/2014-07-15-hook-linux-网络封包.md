---
layout: post
title: "Hook linux 网络封包"
date: "2014-07-15 17:25:03"
slug: "hook-linux-e7-bd-91-e7-bb-9c-e5-b0-81-e5-8c-85"
categories: ["C&C++", "Linux"]
tags: ["linux", "hook", "netfilter", "网络", "封包", "kernel"]
lang: zh
permalink: /zh/hook-linux-e7-bd-91-e7-bb-9c-e5-b0-81-e5-8c-85/
translations:
  zh: /zh/hook-linux-e7-bd-91-e7-bb-9c-e5-b0-81-e5-8c-85/
---
要注册一个hook函数需要用到nf\_register\_hook()或者nf\_register\_hooks()系统API和一个struct nf\_hook\_ops{}类型的结构体对象

一个简单的demo，基于CentOS 6.3，内核版本：linux-2.6.32-279.el6  

myHook.c:
```cpp
#include <linux/kernel.h>
#include <linux/ip.h>
#include <linux/version.h>
#include <linux/netfilter.h>
#include <linux/netfilter\_ipv4.h>
#include <linux/skbuff.h>
#include <linux/netfilter\_ipv4/ip\_tables.h>
#include <linux/moduleparam.h>
#include <linux/in.h>
#include <linux/socket.h>
#include <linux/icmp.h>
MODULE\_LICENSE("GPL");
MODULE\_AUTHOR("ZHT");
MODULE\_DESCRIPTION("My Hook Test");
static int pktcnt = 0;
static unsigned int myhook\_func(unsigned int hooknum, struct sk\_buff \*\*skb,
const struct net\_device \*in,
const struct net\_device \*out,
int (\*okfn)(struct sk\_buff \*)) {
    struct iphdr \*ip\_hdr = (struct iphdr \*)skb\_network\_header(skb);
    printk ("%u.%u.%u.%u\n",NIPQUAD(ip\_hdr->daddr));
    return NF\_ACCEPT;
}
static struct nf\_hook\_ops nfho = {
    .hook = myhook\_func,
    .owner = THIS\_MODULE,
    .pf = PF\_INET,
    .hooknum = 3,
    .priority = NF\_IP\_PRI\_FIRST,
};
static int \_\_init myhook\_init(void) {
    nf\_register\_hook(&nfho);
}
static void \_\_exit myhook\_finit(void) {
    nf\_unregister\_hook(&nfho);
}
module\_init(myhook\_init);
module\_exit(myhook\_finit);
```

Makefile:
```text
obj-m:=myHook.o
myHookmodules-objs:=module
KDIR:=/lib/modules/2.6.32-279.el6.x86\_64/source/
MAKE:=make
default:
$(MAKE) -C $(KDIR) SUBDIRS=$(shell pwd) modules
clean:
$(MAKE) -C $(KDIR) SUBDIRS=$(shell pwd) clean
```
  
放在同一目录下，make编译生成myHook.ko

用命令

```shell
# insmod myHook.ko
# rmmod myHook.ko
```

可以注册和删除该module

注册后，在/var/log/messages中，可看到如下log：

```text
1. Sep  4 22:56:23 rdesktop kernel: 172.16.18.37
2. Sep  4 22:56:23 rdesktop kernel: 172.16.18.37
```