---
title: "Linux中du和df"
date: "2015-06-10 17:32:33"
slug: "linux-e4-b8-addu-e5-92-8cdf"
layout: "post"
categories: ["Linux"]
tags: ["df", "du", "lsof"]
---
Linux运维过程中，经常发现du和df返回值不一样，偶尔会发现差别很大。
特定情况下，可能df看到磁盘已满，但是du判断磁盘剩余空间很大。
文件系统分配其中的一些磁盘块用来记录它自身的一些数据，如i节点，磁盘分布图，间接块，超级块等。这些数据对大多数用户级的程序来说是不可见的，通常称为Meta Data。
df：命令通过查看文件系统磁盘块分配图得出总块数与剩余块数。反应系统磁盘实际用量。
du：用户态程序。不考虑MetaData，只统计文件系统的部分情况。
所以 df >= du
如果df和du的值相差特别大，说明可能有程序将文件输出指定到了已删除的文件。
例如：程序运行过程中，删除log文件，则程序会持续向原log所指向的fileHandler继续输出，而不会终止。即使新建重名文件，仍然会按原fileHandler写入到原文件。在df看来，磁盘增长依然存在，但du看来，文件已经被删除。长期运行之后，则会发生df看到磁盘占用率远高于du。
此时，可以终止该进程，则已删除的文件fileHandler会被回收，文件被删除。
如果不知道进程ID，可以用lsof查询
[codesyntax lang="bash"]

```
# lsof | grep delete
```

[/codesyntax]
