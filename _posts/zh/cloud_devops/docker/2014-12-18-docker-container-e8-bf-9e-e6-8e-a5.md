---
title: "Docker container 连接"
date: "2014-12-18 17:39:30"
slug: "docker-container-e8-bf-9e-e6-8e-a5"
layout: "post"
categories: ["Docker"]
tags: ["docker"]
---
## 端口映射

[前文](http://www.chinacloudly.com/%e5%9c%a8docker%e4%b8%ad%e8%bf%90%e8%a1%8cweb%e5%ba%94%e7%94%a8/ "在Docker中运行web应用")中，我们创建了一个container并运行了简单的Python Flask web 应用。
[codesyntax lang="bash"]

```
# docker run -d -p 5000:5000 training/webapp python app.py
Unable to find image 'training/webapp' locally
Pulling repository training/webapp
31fa814ba25a: Download complete 
511136ea3c5a: Download complete 
f10ebce2c0e1: Download complete 
82cdea7ab5b5: Download complete 
5dbd9cb5a02f: Download complete 
74fe38d11401: Download complete 
64523f641a05: Download complete 
0e2afc9aad6e: Download complete 
e8fc7643ceb1: Download complete 
733b0e3dbcee: Download complete 
a1feb043c441: Download complete 
e12923494f6a: Download complete 
a15f98c46748: Download complete 
Status: Downloaded newer image for training/webapp:latest
276dcd3d9a277b604a3b7b3a99052c7511c2a8f9774a8ca70d5043741a8b8673
```

[/codesyntax]
启动container并将端口5000映射到host的5000端口

## Docker container 协作

Docker有一个Linking系统，允许多个container协同工作，互相发送链接信息。当2个container链接时，可以由其中某一台向另一台发送信息。

### container 命名

Docker使用container的名字来创建链接。
启动container的时候，可以使用默认命名，也可以使用`--name`来手动命名
[codesyntax lang="bash"]

```
# docker run -d -p 5000:5000 --name="web" training/webapp python app.py
```

[/codesyntax]
运行 `docker ps` 可以看到启动了一个名为 `web` 的container
[codesyntax lang="bash"]

```
# docker ps
CONTAINER ID        IMAGE                    COMMAND             CREATED             STATUS              PORTS                    NAMES
be66d08de541        training/webapp:latest   "python app.py"     41 seconds ago      Up 39 seconds       0.0.0.0:5000->5000/tcp   web
```

[/codesyntax]

### container连接

再新启动一个db的container
[codesyntax lang="bash"]

```
# docker run -d --name="db" training/postgres
2ba6ed92ed36db90582d637797228d703ed0c1686664775ad200eef52aaa861c
```

[/codesyntax]
连接两个container
[codesyntax lang="bash"]

```
# docker run -d -p 5000:5000 --name="web" --link db:db training/webapp python app.py  
345e4002f031598ce4fc7da0edd0ad84990da88cf325ccb46a68956770669044
```

[/codesyntax]
结果
[codesyntax lang="bash"]

```
# docker ps
CONTAINER ID        IMAGE                      COMMAND                CREATED             STATUS              PORTS                    NAMES
9ec4237961f9        training/webapp:latest     python app.py          4 seconds ago       Up 3 seconds        0.0.0.0:5000->5000/tcp   web                 
6153f738de6a        training/postgres:latest   su postgres -c '/usr   16 seconds ago      Up 15 seconds       5432/tcp                 db,web/webdb
```

[/codesyntax]
看到后面，NAMES显示 db,web/webdb，但是执行
[codesyntax lang="bash"]

```
# docker inspect -f "{{ .HostConfig.Links }}" web
<no value>
```

[/codesyntax]
不知道是否算是成功，期待下次测试
