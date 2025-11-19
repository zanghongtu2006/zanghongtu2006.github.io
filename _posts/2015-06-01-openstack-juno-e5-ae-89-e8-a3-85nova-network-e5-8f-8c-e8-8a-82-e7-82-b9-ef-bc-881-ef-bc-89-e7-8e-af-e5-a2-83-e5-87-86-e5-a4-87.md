---
title: "OpenStack Juno安装nova-network双节点（1）环境准备"
date: "2015-06-01 18:27:00"
slug: "openstack-juno-e5-ae-89-e8-a3-85nova-network-e5-8f-8c-e8-8a-82-e7-82-b9-ef-bc-881-ef-bc-89-e7-8e-af-e5-a2-83-e5-87-86-e5-a4-87"
layout: "post"
categories: ["OpenStack"]
tags: ["OpenStack", "nova-network", "安装"]
---
本文采用Virtual Box虚拟机安装测试2节点测试环境，网络组建选用nova-network
2个节点，双网卡
Controller Node：1核，2GB内存，8GB硬盘， IP：10.0.2.7，192.168.59.7
Compute Node:1核，2GB内存，20GB硬盘，IP：10.0.2.8
10.0.2.x网段用做管理通信，另一块网卡用做虚拟机网络。

# 配置管理节点

## /etc/hosts

添加
[codesyntax lang="text"]

```
10.0.2.7        controller

10.0.2.8        compute1
```

[/codesyntax]

## NTP

[codesyntax lang="bash"]

```
# yum install -y ntp
```

[/codesyntax]
设置/etc/ntp.conf
[codesyntax lang="text"]

```
restrict -4 default kod notrap nomodify

restrict -6 default kod notrap nomodify
```

[/codesyntax]
设置NTP Server开机自启动
[codesyntax lang="bash"]

```
# systemctl enable ntpd.service

# systemctl start ntpd.service
```

[/codesyntax]

## OpenStack软件包

[codesyntax lang="bash"]

```
# yum install yum-plugin-priorities -y

# yum install -y http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
```

[/codesyntax]

## Juno RDO 源

[codesyntax lang="bash"]

```
# yum install -y https://repos.fedorapeople.org/repos/openstack/openstack-juno/rdo-release-juno-1.noarch.rpm
```

[/codesyntax]

## 更新系统已安装软件包（非必须）

[codesyntax lang="bash"]

```
# yum upgrade -y
```

[/codesyntax]

## OpenStack SeLinux

[codesyntax lang="bash"]

```
# yum install openstack-selinux -y
```

[/codesyntax]

## 数据库

[codesyntax lang="bash"]

```
# yum install -y mariadb mariadb-server MySQL-python
```

[/codesyntax]
编辑/etc/my.cnf
[codesyntax lang="text"]

```
bind-address = controller #设置监听IP，允许其他IP连接mysql

default-storage-engine = innodb #引擎

innodb_file_per_table

collation-server = utf8_general_ci

init-connect = 'SET NAMES utf8'

character-set-server = utf8
```

[/codesyntax]
设置mariadb开机自启动
[codesyntax lang="bash"]

```
# systemctl enable mariadb.service

ln -s '/usr/lib/systemd/system/mariadb.service' '/etc/systemd/system/multi-user.target.wants/mariadb.service'

# systemctl start mariadb.service
```

[/codesyntax]
设置mariadb密码和安全
[codesyntax lang="bash"]

```
# mysql_secure_installation 

/usr/bin/mysql_secure_installation: line 379: find_mysql_client: command not found



NOTE: RUNNING ALL PARTS OF THIS SCRIPT IS RECOMMENDED FOR ALL MariaDB

      SERVERS IN PRODUCTION USE!  PLEASE READ EACH STEP CAREFULLY!



In order to log into MariaDB to secure it, we'll need the current

password for the root user.  If you've just installed MariaDB, and

you haven't set the root password yet, the password will be blank,

so you should just press enter here.



Enter current password for root (enter for none): 

OK, successfully used password, moving on...



Setting the root password ensures that nobody can log into the MariaDB

root user without the proper authorisation.



Set root password? [Y/n] Y

New password: 

Re-enter new password: 

Password updated successfully!

Reloading privilege tables..

 ... Success!





By default, a MariaDB installation has an anonymous user, allowing anyone

to log into MariaDB without having to have a user account created for

them.  This is intended only for testing, and to make the installation

go a bit smoother.  You should remove them before moving into a

production environment.



Remove anonymous users? [Y/n] Y

 ... Success!



Normally, root should only be allowed to connect from 'localhost'.  This

ensures that someone cannot guess at the root password from the network.



Disallow root login remotely? [Y/n] Y

 ... Success!



By default, MariaDB comes with a database named 'test' that anyone can

access.  This is also intended only for testing, and should be removed

before moving into a production environment.



Remove test database and access to it? [Y/n] Y

 - Dropping test database...

 ... Success!

 - Removing privileges on test database...

 ... Success!



Reloading the privilege tables will ensure that all changes made so far

will take effect immediately.



Reload privilege tables now? [Y/n] Y

 ... Success!



Cleaning up...



All done!  If you've completed all of the above steps, your MariaDB

installation should now be secure.



Thanks for using MariaDB!
```

[/codesyntax]

## 消息队列服务器

RabbitMQ
[codesyntax lang="bash"]

```
# yum install -y rabbitmq-server
```

[/codesyntax]
设置RabbitMQ Server开机自启动
[codesyntax lang="bash"]

```
# systemctl enable rabbitmq-server.service

ln -s '/usr/lib/systemd/system/rabbitmq-server.service' '/etc/systemd/system/multi-user.target.wants/rabbitmq-server.service'

# systemctl start rabbitmq-server.service
```

[/codesyntax]
设置RabbitMQ guest用户密码
[codesyntax lang="bash"]

```
# rabbitmqctl change_password guest password

Changing password for user "guest" ...

...done.
```

[/codesyntax]

# 配置计算节点服务器

/etc/hosts
[codesyntax lang="text"]

```
10.0.2.7        controller

10.0.2.8        compute1
```

[/codesyntax]
网卡设置
[codesyntax lang="text"]

```
HWADDR=08:00:27:A5:8B:FA

TYPE=Ethernet

BOOTPROTO=none #此处设为none

DEFROUTE=yes

PEERDNS=yes

PEERROUTES=yes

NAME=enp0s8

UUID=fbff6f14-817c-404b-bd3d-a961cb07eea7

ONBOOT=yes
```

[/codesyntax]
NTP
[codesyntax lang="bash"]

```
# yum install -y ntp
```

[/codesyntax]
设置/etc/ntp.conf
[codesyntax lang="text"]

```
server controller iburst #指定和controller进行时间同步
```

[/codesyntax]
设置NTP开机自启动
[codesyntax lang="bash"]

```
# systemctl enable ntpd.service

ln -s '/usr/lib/systemd/system/ntpd.service' '/etc/systemd/system/multi-user.target.wants/ntpd.service'

# systemctl start ntpd.service
```

[/codesyntax]

## OpenStack软件包

[codesyntax lang="bash"]

```
# yum install yum-plugin-priorities -y

# yum install -y http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
```

[/codesyntax]

## Juno RDO 源

[codesyntax lang="bash"]

```
# yum install -y https://repos.fedorapeople.org/repos/openstack/openstack-juno/rdo-release-juno-1.noarch.rpm
```

[/codesyntax]

## 更新系统已安装软件包（非必须）

[codesyntax lang="bash"]

```
# yum upgrade -y
```

[/codesyntax]

## OpenStack SeLinux

[codesyntax lang="bash"]

```
# yum install openstack-selinux -y
```

[/codesyntax]
