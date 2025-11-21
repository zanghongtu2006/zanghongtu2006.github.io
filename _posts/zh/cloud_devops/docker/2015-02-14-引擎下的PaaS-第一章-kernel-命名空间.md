---
title: "【翻译】引擎下的PaaS, 第一章: kernel 命名空间"
date: "2015-02-14 12:59:28"
slug: "e3-80-90-e7-bf-bb-e8-af-91-e3-80-91-e5-bc-95-e6-93-8e-e4-b8-8b-e7-9a-84paas-e7-ac-ac-e4-b8-80-e7-ab-a0-kernel-e5-91-bd-e5-90-8d-e7-a9-ba-e9-97-b4"
layout: "post"
categories: ["PaaS", "Docker", "Linux"]
tags: []
---
使事情简单化背后是非常繁重的工作。在dotCloud，我们将非常复杂的事务（例如部署和扩展web应用）打包进一个尽可能简单的环境中。但是我们在这样的环境中，如何进行工作呢？从kernel-level的虚拟化到监控，从高吞吐量忘了路由到分布式锁，从EBS处理到每分钟手机数百万的系统数据。。。如同一些人提到过的，弹性调度一个PaaS 就像是系统工程师的迪斯尼乐园。

本文是第一期文章，关于PaaS的架构和内部进行探索，并对dotCloud做更详细的说明。在第一段中，我们将介绍namespace，dotCloud平台用来对应用进行隔离的Linux kernel的特性。

**Part 1: 命名空间（namespace）**

初次接触[Linux Containers (LXC)](http://en.wikipedia.org/wiki/LXC)，会有一个非常错误的印象，就是LXC主要依赖于control groups（cgroup）。这是一个很容易发生的误解：当你创建一个新的container“Jose”，那么同时会产生一个同样名字的cgroup，“/cgroup/jose”。但是实际上，即使cgroup对于LXC非常有用，他们真正重要的基础架构是通过命名空间（namespace）来提供的。

NameSpace是LXC背后真正的容器。Namespace有很多种，每种都提供一个指定的资源。并且每个namespace都会创建对进程的隔离。这些隔离可以分为不同的级别。

## pidnamespace

这大概是对基础隔离最有效的命名空间。

每个PID namespace都有自己独立的进程编号。不同的PID namespace形成了一个等级划分：内核来持续追踪哪个namespace创建了其它的namespace。一个父namespace可以看到并操作他的子namespace；但是子namespace不能对父namespace做任何操作。由此产生如下结果：

* 每个PID namespace有它独立的“PID 1”像进程一样被初始化；
* 在一个namespace中的进程不能通过系统调用（例如kill或者ptrace）来影响父namespace或兄弟namespace中的进程，因为进程ID只在指定的namespace中有意义；
* 如果一个伪文件系统（例如proc）被一个PID namespace中的进程挂载，他会只显示属于这个namespace的进程；
* 因为不同的namespace中的进程编号是不同的，这意味着子namespace中的进程将会拥有不同的PID：一个属于自己namespace的，另一个属于父namespace的。

最后一项，说明从最顶层的PID namespace，你能看到运行在所有namespace中的全部进程，但是他们是不同的PID。当然，如果一个进程处在多于2层的namespace等级中，它也可以拥有多于2个PID。

## Thenetnamespace

在PID namespace中，你可以在多个隔离环境中启动进程（就让我们一劳永逸的称之为“容器”）。但是如果想要在每个container中，运行例如Apache这类服务，同一时间只能有一个进程监听80/tcp端口。你可以配置你的Apache实例来监听不同端口。。。或者使用net namespace。

如同名字一样，net namespace 是关于网络的命名空间。每个不同的net namespace可以拥有不同的网卡。即使lo这种支持127.0.0.1的loopback网络，在每个net namespace中也是不同的。

它可以创建成对的指定网络接口，这些接口将会出现在2个不同的net namespace中，并且允许net namespace和外部网络通信。

一个典型的container会包含自己的loopback网口，以及这样一个特殊的网口，一端命名为eth0，另一端则会在初始namespace中，显示为诸如veth42xyz0这样命名规则的网口。这是通过Enternet bridge来连接的2个网卡，或者在他们之间路由网络封包。（如果你熟悉Xen 网络模型，那么这没什么新鲜的）

每个net namespace都有自己的INADDR\_ANY即0.0.0.0；所以，你的Apache进程在它的namespace中绑定到\*:80，它只会监听直接发送到它所在的namespace的IP地址或网络端口 - 这允许你使用运行多个Apache实例，同时使用默认配置来监听80端口。

如果你还有疑惑，可以这样理解，每个net namespace有自己的路由表，自己的iptables链和规则。

## Theipcnamespace

IPC 提供信号量、消息队列和共享存储片段。

在几乎所有UNIX版本都支持的同事，这些功能也被很多人认为已经过时了，并且将会被[POSIX semaphores](http://linux.die.net/man/7/sem_overview), [POSIX message queues](http://linux.die.net/man/7/mq_overview),和[mmap](http://en.wikipedia.org/wiki/Mmap)取代。尽管如此，很多程序包括[PostgreSQL](http://www.postgresql.org/docs/9.1/static/kernel-resources.html)依然在使用IPC。

这跟namespace有什么联系呢？每个IPC资源都有一个独一无二的32位ID。IPC实现了对资源的访问权限，尽管如此，一个应用访问指定资源的时候可能会失败，因为该资源可能已经被其它容易所使用了。

Introduce theipcnamespace: processes within a givenipcnamespace cannot access (or even see at all) IPC resources living in otheripcnamespaces. And now you can safely run a PostgreSQL instance in each container without fearing IPC key collisions!

介绍一下IPC namespace：指定IPC namespace中的进程无法访问甚至无法见到其它IPC namespace中的进程。现在，你可以安全的在每个容器中，运行postgreSQL实例，而不需要担心IPC key 冲突。

## Themntnamespace

你可能已经对 [chroot](http://en.wikipedia.org/wiki/Chroot)很熟悉了，这套机制允许基于一个指定目录，对进程及其子进程创建一个沙箱。mnt namespace在其上更进了一步。如名所示，mnt namespace基于挂载点来进行处理。运行在不同的mnt namespace上的进程看也看见不同的挂载文件系统和不同的根目录。如果一个文件系统挂载到mnt namespace中，它只能被这个namespace中的进程访问到；在其它namespace中则是不可见的。起初，这似乎很有用，它允许每个container拥有自己独立的目录，隐藏其它的container。仔细想一下，这真的有用么？如果每个container在不同的目录中，使用chroot，container C1 看不到 container C2的文件系统，对吧？是的，不过这只是副作用。

在container中检查/proc/mounts，就会显示所有container的所有挂载点。另外，这些挂载点也会被原始的namespace关联，这个namespace可以给你的系统进行一些设置，这就可能会跟你现有的应用产生冲突，如果你的应用是依赖于/proc/mounts的话。

mnt namespace使这种情况变得更加干净整洁，运行不同的container拥有自己的挂载点，只能查看自己的挂载点，他们自己的path被转换为namespace中真实的根目录。

## Theutsnamespace

最后，uts namespace处理一个小细节：hostname可以被一组进程看到。

每个uts namespace将会被不同的hostname持有，并且改变hostname（通过系统调用 [sethostname](http://linux.die.net/man/2/sethostname)）将只会影响到运行在相同namespace中的进程。

## Creating namespaces

namespace创建是通过系统调用 [clone](http://linux.die.net/man/2/clone)来实现的。这个系统调用支持大量的flag，允许指定“我希望创建新的进程来运行属于它自己的pid，net，ipc，mnt和utsnamespace”。在创建container 的时候，步骤如下：在新的namespace中，启动一个新的进程；创建网络接口（包括和外部通信的端口）；运行初始化进程。在namespace中最后一个进程退出之后，相关的资源（IPC，网络接口等等）会被自动回收。如果，因为其他原因，你想要让这些资源继续存在，是有一个方法的。每个namespace都通过一个在/proc/$PID/ns的文件实例化。在指定文件使用 [mount --bind](http://lwn.net/Articles/407495/) 命令，可以使每个namespace的文件被保留下来供以后使用。

每个namespace？不是很确切。3.4及以上内核版本中，只有IPC，net和uts namespace可以，mnt和pid namespace则不会。这在部分场景中可能是个大问题，例如接下来的场景中。

## Attaching to existing namespaces

也可以通过将一个进程附加到已经存在的namespace的方式来进入这个namespace。为什么会有人想要这么做？一般来说，是用于在namespace中运行特定的命令。例如：

* 想要在外部设置网卡，而不是依赖于container中的脚本；
* 想要运行一些特定命令来获取container的信息：你需要从container外部监控container的运行信息，但是有时候，可能需要一些特殊的补丁工具（例如：你想执行netstat）
* 想要在container中获得shell信息

Attaching a process to existing namespaces requires two things:

把进程附加到namespace需要2个条件：

* [setns](http://man7.org/linux/man-pages/man2/setns.2.html) 系统调用（只在kernel 3.0中，旧版本中需要Patch）；
* namespace必须在/proc/$PID/ns 中

我们在之前的段落中提到过的文件和只能在/proc/$PID/ns看到的ipc，net，utsnamespace。那我们如何附加一个已经存在的mnt和pidnamespace呢？我们不能——除非修改内核。

合并必要的patch可能会相当棘手，并且解释如何解决AUFS和GRSEC的冲突也机会需要一整篇博客。如果你想要运行一个有很多patch的kernel，以下是一些workaround。

* 你可以在container中运行sshd， 并且为将要执行的命令预先授权。这是最简单的解决方案之一，但是如果sshd崩溃，或停止运行（人为或者意外），你将会被锁在container之外。同样，如果你想要尽量多的压缩内存使用，你可能想要摆脱sshd。如果后者是你主要的考虑问题之一，你应该运行一个低消耗的SSH服务器，例如[dropbear](http://en.wikipedia.org/wiki/Dropbear_%28software%29)，或者你可以从inetd或类似服务中，启动一个ssh server。
* 如果你想要运行一些比ssh简单的程序（或者如果你想要运行和ssh不同的东西，来避免和ssh客户端配置交互），你可以开个后门。例如在初始化container的时候，运行socat TCP-LISTEN:222,fork,reuseaddr EXEC:/bin/bash,stderr(保证222/tcp端口在防火墙配置正确）。
* 一个更好的方案是在运行init进程的时候，嵌入“control channel“。在改变跟目录的时候，init进程会在container根目录之外的路径上，设置UNIX socket。当根目录改变的时候，它将会继续持有这个文件描述符——因此保留这个control socket。

## How dotCloud uses namespaces

在早期，dotCloud Platform 使用LXC。

非常早的时候，我们部署了patch过的kernel，运行我们把特定进程附加到已经存在的namespace中——因为我们发现这是非常方便并且可靠的部署、控制和编排方式。随着平台逐步进化，和初始”container“逐步剥离，我们依然使用namespace来隔离应用。

[![公众号二维码](/assets/images/2015/12/公众号二维码-150x150.jpg)](/assets/images/2015/12/公众号二维码.jpg)[![微博二维码](/assets/images/2014/07/微博二维码.png)](/assets/images/2014/07/微博二维码.png)

原文链接：<http://blog.dotcloud.com/under-the-hood-linux-kernels-on-dotcloud-part>
