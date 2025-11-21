---
title: "/proc/sysrq-trigger文件的功能"
date: "2016-07-14 11:19:00"
slug: "procsysrq-trigger-e6-96-87-e4-bb-b6-e7-9a-84-e5-8a-9f-e8-83-bd"
layout: "post"
categories: ["Linux"]
tags: []
---
立即重启计算机      echo "b" > /proc/sysrq-trigger
立即关闭计算机      echo "o" > /proc/sysrq-trigger
导出内存分配的信息    echo "m"  > proc/sysrq-trigger        (可以用/var/log/message查看)Outputs memory statistics to the console
导出当前CPU寄存器信息和标志位的信息     echo "p"  > proc/sysrq-trigger       (outputs all flags and registers to the console)
导出线程状态信息        echo "t"  > proc/sysrq-trigger          (outputs a list of processes to the console)
故意让系统崩溃            echo "c"  > proc/sysrq-trigger         (crashes the system without first unmounting file systems or syncing disks attached to the system)
立即重新挂载所有的文件系统               echo "s"  > proc/sysrq-trigger     (attempts to sync disks attached to the system)
立即重新挂载所有的文件系统为只读     echo "u"  > proc/sysrq-trigger     (attempts to unmount and remount all file systems as read-only)
此外，还有两个类似于强制注销的功能
e ---- kills all processes except init using SIGTERM
i ---- kills all processes except init using SIGKILL
转载自：<http://blog.csdn.net/choice_jj/article/details/7965676>
