---
title: "CentOS 6.3 搭建hadoop伪分布式"
date: "2014-08-05 17:43:24"
slug: "centos-6-3-e6-90-ad-e5-bb-bahadoop-e4-bc-aa-e5-88-86-e5-b8-83-e5-bc-8f"
layout: "post"
categories: ["Hadoop"]
tags: ["伪分布式"]
lang: zh
permalink: /zh/centos-6-3-e6-90-ad-e5-bb-bahadoop-e4-bc-aa-e5-88-86-e5-b8-83-e5-bc-8f/
translations:
  zh: /zh/centos-6-3-e6-90-ad-e5-bb-bahadoop-e4-bc-aa-e5-88-86-e5-b8-83-e5-bc-8f/
---
以Basic Server 模式安装CentOS 6.3，将机器名设置为hadoop1.cloud.com  
安装完成后，在/etc/hosts中把hadoop1.cloud.com 写入 127.0.0.1 后面  
1、安装jdk，本人较懒，所以直接yum，这样可以省去配置环境变量  
```shell
yum install java-1.6.0-openjdk java-1.6.0-openjdk-devel -y
```
2、配置本机无密码登陆
```shell
# ssh-keygen -t dsa -P '' -f ~/.ssh/id\_dsa
# cat .ssh/id\_dsa.pub >> .ssh/authorized\_keys
```
之后可以ssh localhost，无密码可登陆即说明配置成功
 
3、下载并安装hadoop，我使用的是hadoop-1.2.1，直接下载的rpm安装
官网下载成功后，运行命令：
```shell
# rpm -Uvh hadoop-1.2.1-1.x86\_64.rpm
```
4、修改/etc/hadoop/hadoop-env.sh，将JAVA\_HOME修改为真实值
 
因为是yum安装，所以是默认设置，需要修改为：
```shell
# export JAVA\_HOME=/usr/lib/jvm/java-1.6.0-openjdk-1.6.0.0.x86\_64/
```
5、进入/etc/hadoop/，修改mapred-site.xml，core-site.xml，hdfs-site.xml

core-site.xml
```xml
<configuration>
    <property>
        <name>fs.default.name</name>
        <value>hdfs://hadoop1.cloud.com:9000</value>
    </property>
    <property>
        <name>hadoop.tmp.dir</name>
        <value>/home/hadoop/tmp</value>
        <description>A base for other temporary directories.</description>
    </property>
</configuration>
```
mapred-site.xml
```xml
<configuration>
    <property>
        <name>mapred.job.tracker</name>
        <value>hadoop1.cloud.com:9001</value>
    </property>
</configuration>
```
hdfs-site.xml
```xml
<configuration>
    <property>
        <name>dfs.name.dir</name>
        <value>/home/hadoop/dfs/name</value>
    </property>
    <property>
        <name>dfs.data.dir</name>
        <value>/home/hadoop/dfs/data</value>
    </property>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.permissions</name>
        <value>false</value>
    </property>
</configuration>
```
配置完成。
 
6、运行hadoop
1）格式化HDFS：
```
# hadoop namenode -format
```
 
正确输出结果如下：
```shell
13/08/13 23:25:51 INFO namenode.NameNode: STARTUP\_MSG:
/\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*
STARTUP\_MSG: Starting NameNode
STARTUP\_MSG:   host = hadoop1.cloud.com/127.0.0.1
STARTUP\_MSG:   args = [-format]
STARTUP\_MSG:   version = 1.2.1
STARTUP\_MSG:   build = https://svn.apache.org/repos/asf/hadoop/common/branches/branch-1.2 -r 1503152; compiled by 'mattf' on Mon Jul 22 15:27:42 PDT 2013
STARTUP\_MSG:   java = 1.6.0\_24
\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*/
Re-format filesystem in /home/hadoop/dfs/name ? (Y or N) Y
13/08/13 23:25:57 INFO util.GSet: Computing capacity for map BlocksMap
13/08/13 23:25:57 INFO util.GSet: VM type       = 64-bit
13/08/13 23:25:57 INFO util.GSet: 2.0% max memory = 1013645312
13/08/13 23:25:57 INFO util.GSet: capacity      = 2^21 = 2097152 entries
13/08/13 23:25:57 INFO util.GSet: recommended=2097152, actual=2097152
13/08/13 23:25:57 INFO namenode.FSNamesystem: fsOwner=root
13/08/13 23:25:57 INFO namenode.FSNamesystem: supergroup=supergroup
13/08/13 23:25:57 INFO namenode.FSNamesystem: isPermissionEnabled=false
13/08/13 23:25:57 INFO namenode.FSNamesystem: dfs.block.invalidate.limit=100
13/08/13 23:25:57 INFO namenode.FSNamesystem: isAccessTokenEnabled=false accessKeyUpdateInterval=0 min(s), accessTokenLifetime=0 min(s)
13/08/13 23:25:57 INFO namenode.FSEditLog: dfs.namenode.edits.toleration.length = 0
13/08/13 23:25:57 INFO namenode.NameNode: Caching file names occuring more than 10 times
13/08/13 23:25:57 INFO common.Storage: Image file /home/hadoop/dfs/name/current/fsimage of size 110 bytes saved in 0 seconds.
13/08/13 23:25:57 INFO namenode.FSEditLog: closing edit log: position=4, editlog=/home/hadoop/dfs/name/current/edits
13/08/13 23:25:57 INFO namenode.FSEditLog: close success: truncate to 4, editlog=/home/hadoop/dfs/name/current/edits
13/08/13 23:25:58 INFO common.Storage: Storage directory /home/hadoop/dfs/name has been successfully formatted.
13/08/13 23:25:58 INFO namenode.NameNode: SHUTDOWN\_MSG:
/\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*
SHUTDOWN\_MSG: Shutting down NameNode at hadoop1.cloud.com/127.0.0.1
\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*/
```
 
2）启动hadoop守护进程
使用rpm安装后，hadoop的start-all.sh等脚本存放在/usr/sbin/下，默认并没有执行权限
```shell
# chmod u+x /usr/sbin/\*.sh
# start-all.sh
```
输出结果如下：
```shell
# start-all.sh
starting namenode, logging to /var/log/hadoop/root/hadoop-root-namenode-hadoop1.cloud.com.out
localhost: starting datanode, logging to /var/log/hadoop/root/hadoop-root-datanode-hadoop1.cloud.com.out
localhost: starting secondarynamenode, logging to /var/log/hadoop/root/hadoop-root-secondarynamenode-hadoop1.cloud.com.out
starting jobtracker, logging to /var/log/hadoop/root/hadoop-root-jobtracker-hadoop1.cloud.com.out
localhost: starting tasktracker, logging to /var/log/hadoop/root/hadoop-root-tasktracker-hadoop1.cloud.com.out<span style="font-family: Arial, Helvetica, sans-serif;"> </span>
```
 
3）通过浏览器查看hadoop运行状态
NameNode: http://192.168.168.113:50070
JobTracker: http://192.168.168.113:50030
7、关闭Hadoop
```shell
# stop-all.sh
stopping jobtracker
localhost: stopping tasktracker
stopping namenode
localhost: stopping datanode
localhost: stopping secondarynamenode
```