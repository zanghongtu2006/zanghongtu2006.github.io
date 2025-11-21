---
layout: post
lang: zh
title: "Hook linux 网络封包"
date: "2014-07-15 17:25:03"
slug: "hook-linux-e7-bd-91-e7-bb-9c-e5-b0-81-e5-8c-85"
categories: ["C&C++", "Linux"]
tags: ["linux", "hook", "netfilter", "网络", "封包", "kernel"]
---
要注册一个hook函数需要用到nf\_register\_hook()或者nf\_register\_hooks()系统API和一个struct nf\_hook\_ops{}类型的结构体对象

一个简单的demo，基于CentOS 6.3，内核版本：linux-2.6.32-279.el6

**[cpp]** [view plain](http://blog.csdn.net/u011650565/article/details/11100167# "view plain")[copy](http://blog.csdn.net/u011650565/article/details/11100167# "copy")

1. myHook.c:
2. #include <linux/kernel.h>
3. #include <linux/ip.h>
4. #include <linux/version.h>
5. #include <linux/netfilter.h>
6. #include <linux/netfilter\_ipv4.h>
7. #include <linux/skbuff.h>
8. #include <linux/netfilter\_ipv4/ip\_tables.h>
9. #include <linux/moduleparam.h>
10. #include <linux/in.h>
11. #include <linux/socket.h>
12. #include <linux/icmp.h>
14. MODULE\_LICENSE("GPL");
15. MODULE\_AUTHOR("ZHT");
16. MODULE\_DESCRIPTION("My Hook Test");
18. static int pktcnt = 0;
19. static unsigned int myhook\_func(unsigned int hooknum, struct sk\_buff \*\*skb,
20. const struct net\_device \*in,
21. const struct net\_device \*out,
22. int (\*okfn)(struct sk\_buff \*)) {
23. struct iphdr \*ip\_hdr = (struct iphdr \*)skb\_network\_header(skb);
24. printk ("%u.%u.%u.%u\n",NIPQUAD(ip\_hdr->daddr));
25. return NF\_ACCEPT;
26. }
28. static struct nf\_hook\_ops nfho = {
29. .hook = myhook\_func,
30. .owner = THIS\_MODULE,
31. .pf = PF\_INET,
32. .hooknum = 3,
33. .priority = NF\_IP\_PRI\_FIRST,
34. };
36. static int \_\_init myhook\_init(void) {
37. nf\_register\_hook(&nfho);
38. }
40. static void \_\_exit myhook\_finit(void) {
41. nf\_unregister\_hook(&nfho);
42. }
44. module\_init(myhook\_init);
45. module\_exit(myhook\_finit);

**[plain]** [view plain](http://blog.csdn.net/u011650565/article/details/11100167# "view plain")[copy](http://blog.csdn.net/u011650565/article/details/11100167# "copy")

1. Makefile:
2. obj-m:=myHook.o
3. myHookmodules-objs:=module
4. KDIR:=/lib/modules/2.6.32-279.el6.x86\_64/source/
5. MAKE:=make
6. default:
7. $(MAKE) -C $(KDIR) SUBDIRS=$(shell pwd) modules
8. clean:
9. $(MAKE) -C $(KDIR) SUBDIRS=$(shell pwd) clean

  
放在同一目录下，make编译生成myHook.ko

用命令

**[plain]** [view plain](http://blog.csdn.net/u011650565/article/details/11100167# "view plain")[copy](http://blog.csdn.net/u011650565/article/details/11100167# "copy")

1. # insmod myHook.ko
2. # rmmod myHook.ko

可以注册和删除该module

注册后，在/var/log/messages中，可看到如下log：

**[plain]** [view plain](http://blog.csdn.net/u011650565/article/details/11100167# "view plain")[copy](http://blog.csdn.net/u011650565/article/details/11100167# "copy")

1. Sep  4 22:56:23 rdesktop kernel: 172.16.18.37
2. Sep  4 22:56:23 rdesktop kernel: 172.16.18.37
