---
title: "Docker Image操作"
date: "2014-12-17 23:52:27"
slug: "docker-image-e6-93-8d-e4-bd-9c"
layout: "post"
categories: ["Docker"]
tags: ["docker"]
---
## List Images

列出本地所有Docker image
[codesyntax lang="bash"]

```
# docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
centos              centos6             25c5298b1a36        2 weeks ago         215.8 MB
```

[/codesyntax]
 
可以看到，REPOSITORY是image来源库，此处是centos
TAG：每个image有自己的tag，此处是centos6
使用该image启动Docker container的时候，名字为：centos:centos6
IMAGE ID：每个image有自己独立的ID下载新的image

## 查找新的image

众多Docker的使用者会创建自己的image，有部分image就会上传到[Docker Hub](https://hub.docker.com/)中，我们可以直接在Docker Hub中查找合适的image。
也可以使用`docker search`命令查找image
[codesyntax lang="bash"]

```
# docker search centos | more
NAME                                              DESCRIPTION                                     STARS     OFFICIAL   AUTOMATED
centos                                            The official build of CentOS.                   685       [OK]       
tianon/centos                                     CentOS 5 and 6, created using rinse instea...   29                   
ansible/centos7-ansible                           Ansible on Centos7                              22                   [OK]
ariya/centos6-teamcity-server                     TeamCity Server 8.1 on CentOS 6                 8                    [OK]
tutum/centos                                      Centos image with SSH access. For the root...   8                    [OK]
berngp/docker-zabbix                              Runs Zabbix Server and Zabbix Web UI on a ...   8                    [OK]
saltstack/centos-6-minimal                                                                        8                    [OK]
blalor/centos                                     Bare-bones base CentOS 6.5 image                7                    [OK]
centos/freeipa                                    FreeIPA in Docker on CentOS                     7                    
steeef/graphite-centos                            CentOS 6.x with Graphite and Carbon via ng...   6                    [OK]
dockerfiles/centos-lamp                                                                           6                    [OK]
gluster/gluster                                   GlusterFS 3.5 - CentOS 6.5 Docker repo          6                    [OK]
ariya/centos6-teamcity-agent                      Build agent for TeamCity 8.1                    5                    [OK]
tutum/centos-6.4                                  DEPRECATED. Use tutum/centos:6.4 instead. ...   5                    [OK]
jdeathe/centos-ssh-apache-php                     CentOS-6 6.5 x86_64 / Apache / PHP / PHP m...   5                    [OK]
cern/centos-wlcg-wn                               CentosOS 6 image with pre-installed softwa...   4
```

[/codesyntax]

## 创建新的image

### 更新现有的image

交互模式启动centos:centos6，安装mysql
[codesyntax lang="bash"]

```
# docker run -t -i centos:centos6 /bin/bash
bash-4.1# 
bash-4.1# yum install -y mysql mysql-serve
```

[/codesyntax]
完成后，`exit`退出交互模式
[codesyntax lang="bash"]

```
# docker ps -a
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS                         PORTS               NAMES
2e9de4d9c350        centos:centos6      /bin/bash           2 minutes ago       Exited (0) 7 seconds ago                           mad_colden
```

[/codesyntax]
可以看到刚刚关掉的container ID
[codesyntax lang="bash"]

```
# docker commit -m="install mysql" -a="Hongtu Zang" 2e9de4d9c350 centos6:hongtu
5f3bca7952cac8900e08b5fac11cdd1a4941803edbb5442593a171fe574ed961
```

[/codesyntax]
-m Message，描述信息
-a author，image的创建者
[codesyntax lang="bash"]

```
# docker images
REPOSITORY          TAG                 IMAGE ID            CREATED              VIRTUAL SIZE
centos6             hongtu              5f3bca7952ca        About a minute ago   320.3 MB
centos              centos6             25c5298b1a36        2 weeks ago          215.8 MB
```

[/codesyntax]
可以看到，多出来一个TAG为hongtu的image，是我们刚刚创建好的

### 从Dockerfile创建image

创建一个Dockerfile
[codesyntax lang="bash"]

```
# mkdir hongtu
# cd hongtu/
# touch Dockerfile
```

[/codesyntax]
编辑Dockerfile内容：
[codesyntax lang="text"]

```
# This is a comment
FROM centos:centos6
MAINTAINER Hongtu Zang <hongtu_zang@chinacloudly.com>
RUN yum install -y mysql mysql-server
```

[/codesyntax]
FROM 基础image
MAINTAINER 作者
RUN 需要执行的命令，此处是安装mysql-server
`docker run`创建新的模板
[codesyntax lang="bash"]

```
# docker build -t="hongtu/centos6:v2" .
Sending build context to Docker daemon  2.56 kB
Sending build context to Docker daemon 
Step 0 : FROM centos:centos6
 ---> 25c5298b1a36
Step 1 : MAINTAINER Hongtu Zang <hongtu_zang@chinacloudly.com>
 ---> Using cache
 ---> 52f35fcefd08
Step 2 : RUN yum install -y mysql mysql-server
 ---> Running in 35ab46137fe7
Loaded plugins: fastestmirror
Setting up Install Process
Resolving Dependencies
--> Running transaction check
---> Package mysql.x86_64 0:5.1.73-3.el6_5 will be installed
--> Processing Dependency: mysql-libs = 5.1.73-3.el6_5 for package: mysql-5.1.73-3.el6_5.x86_64
--> Processing Dependency: perl(Sys::Hostname) for package: mysql-5.1.73-3.el6_5.x86_64
--> Processing Dependency: perl(IPC::Open3) for package: mysql-5.1.73-3.el6_5.x86_64
--> Processing Dependency: perl(Getopt::Long) for package: mysql-5.1.73-3.el6_5.x86_64
--> Processing Dependency: perl(File::Temp) for package: mysql-5.1.73-3.el6_5.x86_64
--> Processing Dependency: perl(Fcntl) for package: mysql-5.1.73-3.el6_5.x86_64
--> Processing Dependency: perl(Exporter) for package: mysql-5.1.73-3.el6_5.x86_64
--> Processing Dependency: libmysqlclient_r.so.16(libmysqlclient_16)(64bit) for package: mysql-5.1.73-3.el6_5.x86_64
--> Processing Dependency: libmysqlclient.so.16(libmysqlclient_16)(64bit) for package: mysql-5.1.73-3.el6_5.x86_64
--> Processing Dependency: /usr/bin/perl for package: mysql-5.1.73-3.el6_5.x86_64
--> Processing Dependency: libmysqlclient_r.so.16()(64bit) for package: mysql-5.1.73-3.el6_5.x86_64
--> Processing Dependency: libmysqlclient.so.16()(64bit) for package: mysql-5.1.73-3.el6_5.x86_64
---> Package mysql-server.x86_64 0:5.1.73-3.el6_5 will be installed
--> Processing Dependency: perl-DBI for package: mysql-server-5.1.73-3.el6_5.x86_64
--> Processing Dependency: perl-DBD-MySQL for package: mysql-server-5.1.73-3.el6_5.x86_64
--> Processing Dependency: perl(DBI) for package: mysql-server-5.1.73-3.el6_5.x86_64
--> Running transaction check
---> Package mysql-libs.x86_64 0:5.1.73-3.el6_5 will be installed
---> Package perl.x86_64 4:5.10.1-136.el6_6.1 will be installed
--> Processing Dependency: perl-libs = 4:5.10.1-136.el6_6.1 for package: 4:perl-5.10.1-136.el6_6.1.x86_64
--> Processing Dependency: perl-libs for package: 4:perl-5.10.1-136.el6_6.1.x86_64
--> Processing Dependency: perl(version) for package: 4:perl-5.10.1-136.el6_6.1.x86_64
--> Processing Dependency: perl(Pod::Simple) for package: 4:perl-5.10.1-136.el6_6.1.x86_64
--> Processing Dependency: perl(Module::Pluggable) for package: 4:perl-5.10.1-136.el6_6.1.x86_64
--> Processing Dependency: libperl.so()(64bit) for package: 4:perl-5.10.1-136.el6_6.1.x86_64
---> Package perl-DBD-MySQL.x86_64 0:4.013-3.el6 will be installed
---> Package perl-DBI.x86_64 0:1.609-4.el6 will be installed
--> Running transaction check
---> Package perl-Module-Pluggable.x86_64 1:3.90-136.el6_6.1 will be installed
---> Package perl-Pod-Simple.x86_64 1:3.13-136.el6_6.1 will be installed
--> Processing Dependency: perl(Pod::Escapes) >= 1.04 for package: 1:perl-Pod-Simple-3.13-136.el6_6.1.x86_64
---> Package perl-libs.x86_64 4:5.10.1-136.el6_6.1 will be installed
---> Package perl-version.x86_64 3:0.77-136.el6_6.1 will be installed
--> Running transaction check
---> Package perl-Pod-Escapes.x86_64 1:1.04-136.el6_6.1 will be installed
--> Finished Dependency Resolution

Dependencies Resolved

================================================================================
 Package                  Arch      Version                    Repository  Size
================================================================================
Installing:
 mysql                    x86_64    5.1.73-3.el6_5             base       894 k
 mysql-server             x86_64    5.1.73-3.el6_5             base       8.6 M
Installing for dependencies:
 mysql-libs               x86_64    5.1.73-3.el6_5             base       1.2 M
 perl                     x86_64    4:5.10.1-136.el6_6.1       updates     10 M
 perl-DBD-MySQL           x86_64    4.013-3.el6                base       134 k
 perl-DBI                 x86_64    1.609-4.el6                base       705 k
 perl-Module-Pluggable    x86_64    1:3.90-136.el6_6.1         updates     40 k
 perl-Pod-Escapes         x86_64    1:1.04-136.el6_6.1         updates     32 k
 perl-Pod-Simple          x86_64    1:3.13-136.el6_6.1         updates    212 k
 perl-libs                x86_64    4:5.10.1-136.el6_6.1       updates    578 k
 perl-version             x86_64    3:0.77-136.el6_6.1         updates     51 k

Transaction Summary
================================================================================
Install      11 Package(s)

Total download size: 23 M
Installed size: 69 M
Downloading Packages:
--------------------------------------------------------------------------------
Total                                           104 kB/s |  23 MB     03:42     
warning: rpmts_HdrFromFdno: Header V3 RSA/SHA1 Signature, key ID c105b9de: NOKEY
Retrieving key from file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-6
Importing GPG key 0xC105B9DE:
 Userid : CentOS-6 Key (CentOS 6 Official Signing Key) <centos-6-key@centos.org>
 Package: centos-release-6-6.el6.centos.12.2.x86_64 (@CentOS/$releasever)
 From   : /etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-6
Running rpm_check_debug
Running Transaction Test
Transaction Test Succeeded
Running Transaction
Warning: RPMDB altered outside of yum.
  Installing : mysql-libs-5.1.73-3.el6_5.x86_64                            1/11 
  Installing : 1:perl-Pod-Escapes-1.04-136.el6_6.1.x86_64                  2/11 
  Installing : 4:perl-libs-5.10.1-136.el6_6.1.x86_64                       3/11 
  Installing : 1:perl-Module-Pluggable-3.90-136.el6_6.1.x86_64             4/11 
  Installing : 1:perl-Pod-Simple-3.13-136.el6_6.1.x86_64                   5/11 
  Installing : 3:perl-version-0.77-136.el6_6.1.x86_64                      6/11 
  Installing : 4:perl-5.10.1-136.el6_6.1.x86_64                            7/11 
  Installing : perl-DBI-1.609-4.el6.x86_64                                 8/11 
  Installing : perl-DBD-MySQL-4.013-3.el6.x86_64                           9/11 
  Installing : mysql-5.1.73-3.el6_5.x86_64                                10/11 
  Installing : mysql-server-5.1.73-3.el6_5.x86_64                         11/11 
  Verifying  : 3:perl-version-0.77-136.el6_6.1.x86_64                      1/11 
  Verifying  : perl-DBD-MySQL-4.013-3.el6.x86_64                           2/11 
  Verifying  : mysql-libs-5.1.73-3.el6_5.x86_64                            3/11 
  Verifying  : mysql-server-5.1.73-3.el6_5.x86_64                          4/11 
  Verifying  : mysql-5.1.73-3.el6_5.x86_64                                 5/11 
  Verifying  : perl-DBI-1.609-4.el6.x86_64                                 6/11 
  Verifying  : 1:perl-Pod-Simple-3.13-136.el6_6.1.x86_64                   7/11 
  Verifying  : 4:perl-5.10.1-136.el6_6.1.x86_64                            8/11 
  Verifying  : 4:perl-libs-5.10.1-136.el6_6.1.x86_64                       9/11 
  Verifying  : 1:perl-Module-Pluggable-3.90-136.el6_6.1.x86_64            10/11 
  Verifying  : 1:perl-Pod-Escapes-1.04-136.el6_6.1.x86_64                 11/11 

Installed:
  mysql.x86_64 0:5.1.73-3.el6_5       mysql-server.x86_64 0:5.1.73-3.el6_5      

Dependency Installed:
  mysql-libs.x86_64 0:5.1.73-3.el6_5                                            
  perl.x86_64 4:5.10.1-136.el6_6.1                                              
  perl-DBD-MySQL.x86_64 0:4.013-3.el6                                           
  perl-DBI.x86_64 0:1.609-4.el6                                                 
  perl-Module-Pluggable.x86_64 1:3.90-136.el6_6.1                               
  perl-Pod-Escapes.x86_64 1:1.04-136.el6_6.1                                    
  perl-Pod-Simple.x86_64 1:3.13-136.el6_6.1                                     
  perl-libs.x86_64 4:5.10.1-136.el6_6.1                                         
  perl-version.x86_64 3:0.77-136.el6_6.1                                        

Complete!
 ---> 4ee0c1aacb0e
Removing intermediate container 35ab46137fe7
Successfully built 4ee0c1aacb0
```

[/codesyntax]
成功创建新的image
`-t` 定义image属性，属于 `hongtu` 用户，`repository` 为 `centos`， `tag`指定为 `v2`
`.` 指定在当前目录寻找 `Dockerfile`
[codesyntax lang="bash"]

```
# docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
hongtu/centos6      v2                  4ee0c1aacb0e        2 minutes ago       323.1 MB
centos6             hongtu              5f3bca7952ca        31 minutes ago      320.3 MB
centos              centos6             25c5298b1a36        2 weeks ago         215.8 MB
```

[/codesyntax]
可以看到新建的image id 为 4ee0c1aacb0e

## 向Docker hub上传 image

[codesyntax lang="bash"]

```
# docker push hongtu/centos6
```

[/codesyntax]

## 删除本地image

[codesyntax lang="bash"]

```
# docker rmi -f hongtu/centos6
```

[/codesyntax]
`-f` 强制删除
