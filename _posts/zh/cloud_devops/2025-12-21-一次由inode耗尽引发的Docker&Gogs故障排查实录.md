---
layout: post
lang: zh
slug: inode-caused-break-down-trouble-shooting
permalink: /zh/inode-caused-break-down-trouble-shooting/
translations:
  en: /en/inode-caused-break-down-trouble-shooting/
  zh: /zh/inode-caused-break-down-trouble-shooting/
title: "一次由inode耗尽引发的Docker&Gogs故障排查实录"
date: 2025-11-27 22:51:00 +0100
categories: ["Diary"]
---

# 一次由inode耗尽引发的Docker&Gogs故障排查实录

## 背景

我的一台 Linux 云主机上，Docker 开始频繁报错：  
no space left on device

但用 **df -h** 查看磁盘空间，发现磁盘容量还有大量剩余。
乍一看非常反直觉，但这恰恰是 Linux 系统中一个经典且隐蔽的问题。

## 一、初步现象：磁盘有空间，Docker 却“满了”

最初的检查：
```shell
df -h
```

结果显示磁盘容量充足，但 Docker：  
容器启动失败  
写文件失败  
构建失败  
这说明问题并不在 block space（磁盘容量）。

## 二、关键一步：检查 inode

随后检查 inode 使用情况：
```shell
df -i
```

结果非常关键：  
```shell
Filesystem      Inodes   IUsed   IFree IUse% Mounted on
/dev/vda2      3932160 3929865    2295  100% /
```

根分区 inode 100% 用尽。  
结论：  
系统已经无法创建任何新文件，即使磁盘还有空间。

Docker、Git、日志、临时文件，本质上都依赖 inode。

## 三、避免 find，全用 du --inodes 定位

在 inode 即将耗尽的系统上：  
不要 find /  
不要全盘扫描

正确方式是逐层缩小范围：
```shell
du --inodes -d 1 / | sort -nr | head
```

结果非常震撼：
```shell
3648582 /opt
149766  /var
```

/opt 一个目录，占用了 92% 以上的 inode

## 四、锁定元凶：/opt 下的 Gogs

继续下钻：
```shell
du --inodes -d 1 /opt | sort -nr | head
```

发现其中有一个：

**/opt/docker/gogs**

服务器上运行着一个 Docker 部署的 Gogs（Git 服务）。

## 五、Gogs 为什么会吃掉几百万 inode？

深入查看后发现：  
Gogs 的 Git 仓库位于宿主机 /opt/docker/gogs/data/git  
每个仓库除了主仓库，还会自动创建一个：  
**<repo>.wiki.git**

关键认知：
Gogs 的 Wiki 本质上是一个“独立的 Git 仓库”  
而 Git 的存储特点是：  
每个 object = 一个小文件  
每个小文件 = 一个 inode  
Wiki 编辑频繁，但几乎从不 GC  
loose objects 会无限增长

## 六、为什么 GC 会失败？

尝试执行：  
```shell
git gc --aggressive --prune=now
```

却直接失败：  
```shell
unable to create packed-refs.new: No space left on device
```

原因很简单：  
Git GC 本身也需要创建新文件, 而 inode 已经 100% 用尽  
这是一个典型的“死锁场景”：

想 GC → 需要 inode  
inode 已满 → GC 无法执行

## 七、关键突破：删除 *.wiki.git

在确认 Wiki 内容完全不重要后，果断执行：
```wiki
rm -rf /opt/docker/gogs/data/git/gogs-repositories/*/*.wiki.git
```

效果立竿见影：  
inode 使用率立刻下降  
系统恢复可写  
Docker / Git 恢复正常  
Wiki 仓库正是 inode 爆炸的主因之一

## 八、问题解决后的收尾工作

再次执行 Git GC（此时已能成功）  
在 Gogs 中禁用 Wiki 功能：  
**DISABLE_WIKI = true** 

规划长期方案：  
**Git 仓库迁移到独立磁盘**  
**定期 git gc**  
**inode 监控与告警**

## 九、总结

这次问题的本质并不是：  
Docker 的问题  
Linux 的问题  
磁盘容量的问题  
而是：  
inode 被 Git（尤其是 Wiki 仓库）长期、无感知地耗尽  

经验教训  
**df -h 看不到一切，df -i 同样重要**
**Git ≠ 数据库，更不适合存放大量小变更**
**Wiki 是隐藏的 inode 杀手**
**Docker 只是“第一个报警的人”**

# 结语

这是一次非常典型且极具价值的排障案例。
如果你的服务器上同时存在：  
Docker  
Git 服务（Gogs / Gitea / GitLab）  
根分区运行多年  
**强烈建议你现在就检查一次 inode**
