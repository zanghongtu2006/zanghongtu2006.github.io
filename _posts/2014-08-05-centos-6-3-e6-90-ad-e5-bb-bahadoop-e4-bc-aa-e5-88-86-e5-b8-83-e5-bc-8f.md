---
title: "CentOS 6.3 搭建hadoop伪分布式"
date: "2014-08-05 17:43:24"
slug: "centos-6-3-e6-90-ad-e5-bb-bahadoop-e4-bc-aa-e5-88-86-e5-b8-83-e5-bc-8f"
layout: "post"
categories: ["Hadoop"]
tags: ["伪分布式"]
---
以Basic Server 模式安装CentOS 6.3，将机器名设置为hadoop1.cloud.com
安装完成后，在/etc/hosts中把hadoop1.cloud.com 写入 127.0.0.1 后面
1、安装jdk，本人较懒，所以直接yum，这样可以省去配置环境变量

1. yum install java-1.6.0-openjdk java-1.6.0-openjdk-devel -y

2、配置本机无密码登陆

1. ssh-keygen -t dsa -P '' -f ~/.ssh/id\_dsa
2. cat .ssh/id\_dsa.pub >> .ssh/authorized\_keys

之后可以ssh localhost，无密码可登陆即说明配置成功
 
3、下载并安装hadoop，我使用的是hadoop-1.2.1，直接下载的rpm安装
官网下载成功后，运行命令：

1. rpm -Uvh hadoop-1.2.1-1.x86\_64.rpm

4、修改/etc/hadoop/hadoop-env.sh，将JAVA\_HOME修改为真实值
 
因为是yum安装，所以是默认设置，需要修改为：

1. export JAVA\_HOME=/usr/lib/jvm/java-1.6.0-openjdk-1.6.0.0.x86\_64/

5、进入/etc/hadoop/，修改mapred-site.xml，core-site.xml，hdfs-site.xml

1. core-site.xml
2. <configuration>
3. <property>
4. <name>fs.default.name</name>
5. <value>hdfs://hadoop1.cloud.com:9000</value>
6. </property>
7. <property>
8. <name>hadoop.tmp.dir</name>
9. <value>/home/hadoop/tmp</value>
10. <description>A base for other temporary directories.</description>
11. </property>
12. </configuration>

1. mapred-site.xml
2. <configuration>
3. <property>
4. <name>mapred.job.tracker</name>
5. <value>hadoop1.cloud.com:9001</value>
6. </property>
7. </configuration>

1. hdfs-site.xml
2. <configuration>
3. <property>
4. <name>dfs.name.dir</name>
5. <value>/home/hadoop/dfs/name</value>
6. </property>
7. <property>
8. <name>dfs.data.dir</name>
9. <value>/home/hadoop/dfs/data</value>
10. </property>
11. <property>
12. <name>dfs.replication</name>
13. <value>1</value>
14. </property>
15. <property>
16. <name>dfs.permissions</name>
17. <value>false</value>
18. </property>
19. </configuration>

配置完成。
 
6、运行hadoop
1）格式化HDFS：

1. # hadoop namenode -format

 
正确输出结果如下：

1. 13/08/13 23:25:51 INFO namenode.NameNode: STARTUP\_MSG:
2. /\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*
3. STARTUP\_MSG: Starting NameNode
4. STARTUP\_MSG:   host = hadoop1.cloud.com/127.0.0.1
5. STARTUP\_MSG:   args = [-format]
6. STARTUP\_MSG:   version = 1.2.1
7. STARTUP\_MSG:   build = https://svn.apache.org/repos/asf/hadoop/common/branches/branch-1.2 -r 1503152; compiled by 'mattf' on Mon Jul 22 15:27:42 PDT 2013
8. STARTUP\_MSG:   java = 1.6.0\_24
9. \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*/
10. Re-format filesystem in /home/hadoop/dfs/name ? (Y or N) Y
11. 13/08/13 23:25:57 INFO util.GSet: Computing capacity for map BlocksMap
12. 13/08/13 23:25:57 INFO util.GSet: VM type       = 64-bit
13. 13/08/13 23:25:57 INFO util.GSet: 2.0% max memory = 1013645312
14. 13/08/13 23:25:57 INFO util.GSet: capacity      = 2^21 = 2097152 entries
15. 13/08/13 23:25:57 INFO util.GSet: recommended=2097152, actual=2097152
16. 13/08/13 23:25:57 INFO namenode.FSNamesystem: fsOwner=root
17. 13/08/13 23:25:57 INFO namenode.FSNamesystem: supergroup=supergroup
18. 13/08/13 23:25:57 INFO namenode.FSNamesystem: isPermissionEnabled=false
19. 13/08/13 23:25:57 INFO namenode.FSNamesystem: dfs.block.invalidate.limit=100
20. 13/08/13 23:25:57 INFO namenode.FSNamesystem: isAccessTokenEnabled=false accessKeyUpdateInterval=0 min(s), accessTokenLifetime=0 min(s)
21. 13/08/13 23:25:57 INFO namenode.FSEditLog: dfs.namenode.edits.toleration.length = 0
22. 13/08/13 23:25:57 INFO namenode.NameNode: Caching file names occuring more than 10 times
23. 13/08/13 23:25:57 INFO common.Storage: Image file /home/hadoop/dfs/name/current/fsimage of size 110 bytes saved in 0 seconds.
24. 13/08/13 23:25:57 INFO namenode.FSEditLog: closing edit log: position=4, editlog=/home/hadoop/dfs/name/current/edits
25. 13/08/13 23:25:57 INFO namenode.FSEditLog: close success: truncate to 4, editlog=/home/hadoop/dfs/name/current/edits
26. 13/08/13 23:25:58 INFO common.Storage: Storage directory /home/hadoop/dfs/name has been successfully formatted.
27. 13/08/13 23:25:58 INFO namenode.NameNode: SHUTDOWN\_MSG:
28. /\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*
29. SHUTDOWN\_MSG: Shutting down NameNode at hadoop1.cloud.com/127.0.0.1
30. \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*/

 
2）启动hadoop守护进程
使用rpm安装后，hadoop的start-all.sh等脚本存放在/usr/sbin/下，默认并没有执行权限

1. # chmod u+x /usr/sbin/\*.sh
2. # start-all.sh

输出结果如下：

1. # start-all.sh
2. starting namenode, logging to /var/log/hadoop/root/hadoop-root-namenode-hadoop1.cloud.com.out
3. localhost: starting datanode, logging to /var/log/hadoop/root/hadoop-root-datanode-hadoop1.cloud.com.out
4. localhost: starting secondarynamenode, logging to /var/log/hadoop/root/hadoop-root-secondarynamenode-hadoop1.cloud.com.out
5. starting jobtracker, logging to /var/log/hadoop/root/hadoop-root-jobtracker-hadoop1.cloud.com.out
6. localhost: starting tasktracker, logging to /var/log/hadoop/root/hadoop-root-tasktracker-hadoop1.cloud.com.out<span style="font-family: Arial, Helvetica, sans-serif;"> </span>

 
3）通过浏览器查看hadoop运行状态
NameNode: http://192.168.168.113:50070
JobTracker: http://192.168.168.113:50030
7、关闭Hadoop

1. # stop-all.sh
2. stopping jobtracker
3. localhost: stopping tasktracker
4. stopping namenode
5. localhost: stopping datanode
6. localhost: stopping secondarynamenode
