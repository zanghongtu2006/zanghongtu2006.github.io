---
title: "MySQL建立数据库连接时出错"
date: "2014-12-08 11:13:33"
slug: "mysql-cannot-allocate-memory-e6-97-a0-e6-b3-95-e5-90-af-e5-8a-a8"
layout: "post"
categories: ["Mysql"]
tags: ["mysql", "allocate", "memory", "数据库", "连接"]
---
该博客自上线以来，多次发生无法连接数据库错误

[![dberror](/assets/images/2014/12/dberror-300x63.jpg)](/assets/images/2014/12/dberror.jpg)

MySQL无法启动，log如下

[codesyntax lang="text" lines="no"]

```
141208 10:53:47 [Warning] Using unique option prefix myisam-recover instead of myisam-recover-options is deprecated and will be removed in a future release. Please use the full name instead.
141208 10:53:47 [Note] Plugin 'FEDERATED' is disabled.
141208 10:53:47 InnoDB: The InnoDB memory heap is disabled
141208 10:53:47 InnoDB: Mutexes and rw_locks use GCC atomic builtins
141208 10:53:47 InnoDB: Compressed tables use zlib 1.2.3.4
141208 10:53:47 InnoDB: Initializing buffer pool, size = 128.0M
InnoDB: mmap(137363456 bytes) failed; errno 12
141208 10:53:47 InnoDB: Completed initialization of buffer pool
141208 10:53:47 InnoDB: Fatal error: cannot allocate memory for the buffer pool
141208 10:53:47 [ERROR] Plugin 'InnoDB' init function returned error.
141208 10:53:47 [ERROR] Plugin 'InnoDB' registration as a STORAGE ENGINE failed.
141208 10:53:47 [ERROR] Unknown/unsupported storage engine: InnoDB
141208 10:53:47 [ERROR] Aborting

141208 10:53:47 [Note] /usr/sbin/mysqld: Shutdown complete
```

[/codesyntax]

看log，是由于innodb无法获取内存而导致不能启动。

我是在vm中运行，vm只有512M内存，所以基本上可以判定不够用了。

但是还得解决。。。

方案如下:

在my.cnf文件中，[mysqld]类别下，加入

innodb\_buffer\_pool\_size = 64M

重启MySQL服务即可
