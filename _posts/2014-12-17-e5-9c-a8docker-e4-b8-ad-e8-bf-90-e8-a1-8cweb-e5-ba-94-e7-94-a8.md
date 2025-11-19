---
title: "在Docker中运行web应用"
date: "2014-12-17 10:52:50"
slug: "e5-9c-a8docker-e4-b8-ad-e8-bf-90-e8-a1-8cweb-e5-ba-94-e7-94-a8"
layout: "post"
categories: ["Docker"]
tags: ["docker"]
---
# 启动一个简单的web 应用

[codesyntax lang="bash"]

```
# docker run -d -P training/webapp python app.py
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
d00f94a31e8767271f68ab72eab15a8e805c416b0636877f22a31572d10b718d
```

[/codesyntax]
 
`-d` 启动一个daemon并在后台运行
`-P` 映射一个网络端口
`training/webapp` docker社区提供的，预先创建好的模板，里面包含一个简单的Python Flask web应用
[codesyntax lang="bash"]

```
# docker ps -l
CONTAINER ID        IMAGE                    COMMAND             CREATED             STATUS              PORTS                     NAMES
d00f94a31e87        training/webapp:latest   "python app.py"     59 seconds ago      Up 56 seconds       0.0.0.0:49153->5000/tcp   hopeful_lalande
```

[/codesyntax]
 
`-l 查看详细信息`
PORTS显示 0.0.0.0:49153->5000/tcp
意思是将container中的5000端口，映射到host的49153端口。5000是Python Flask 的默认端口。
也可以使用 `-p container-port:host-port` 命令来指定映射端口号
[codesyntax lang="bash"]

```
# docker run -d -p 5000:5000 training/webapp python app.py
```

[/codesyntax]
 
[![QQ图片20141217103052](/assets/images/2014/12/QQ图片20141217103052.jpg)](/assets/images/2014/12/QQ图片20141217103052.jpg)

# 查看web应用信息

## 查看名为hopeful\_lalande的docker container中，5000端口的映射信息

[codesyntax lang="bash"]

```
# docker port hopeful_lalande 5000
0.0.0.0:49153
```

[/codesyntax]

## 查看web应用日志

[codesyntax lang="bash"]

```
# docker logs -f hopeful_lalande
 * Running on http://0.0.0.0:5000/
192.168.254.1 - - [17/Dec/2014 02:30:32] "GET / HTTP/1.1" 200 -
192.168.254.1 - - [17/Dec/2014 02:30:32] "GET /favicon.ico HTTP/1.1" 404 -
192.168.254.1 - - [17/Dec/2014 02:30:32] "GET /favicon.ico HTTP/1.1" 404 -
```

[/codesyntax]
 
`-f` 持续查看container日志的标准化输出，类似`tail -f`

## 查看进程详细信息

[codesyntax lang="bash"]

```
# docker top hopeful_lalande
UID                 PID                 PPID                C                   STIME               TTY                 TIME                CMD
root                15189               2447                0                   10:24               ?                   00:00:00            python app.py
```

[/codesyntax]

## 查看web应用容器详细信息

[codesyntax lang="bash"]

```
# docker inspect hopeful_lalande
[{
    "AppArmorProfile": "",
    "Args": [
        "app.py"
    ],
    "Config": {
        "AttachStderr": false,
        "AttachStdin": false,
        "AttachStdout": false,
        "Cmd": [
            "python",
            "app.py"
        ],
        "CpuShares": 0,
        "Cpuset": "",
        "Domainname": "",
        "Entrypoint": null,
        "Env": [
            "HOME=/",
            "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        ],
        "ExposedPorts": {
            "5000/tcp": {}
        },
        "Hostname": "d00f94a31e87",
        "Image": "training/webapp",
        "Memory": 0,
        "MemorySwap": 0,
        "NetworkDisabled": false,
        "OnBuild": null,
        "OpenStdin": false,
        "PortSpecs": null,
        "StdinOnce": false,
        "Tty": false,
        "User": "",
        "Volumes": null,
        "WorkingDir": "/opt/webapp"
    },
    "Created": "2014-12-17T02:24:09.468631143Z",
    "Driver": "devicemapper",
    "ExecDriver": "native-0.2",
    "HostConfig": {
        "Binds": null,
        "CapAdd": null,
        "CapDrop": null,
        "ContainerIDFile": "",
        "Devices": [],
        "Dns": null,
        "DnsSearch": null,
        "ExtraHosts": null,
        "Links": null,
        "LxcConf": [],
        "NetworkMode": "bridge",
        "PortBindings": {},
        "Privileged": false,
        "PublishAllPorts": true,
        "RestartPolicy": {
            "MaximumRetryCount": 0,
            "Name": ""
        },
        "SecurityOpt": null,
        "VolumesFrom": null
    },
    "HostnamePath": "/var/lib/docker/containers/d00f94a31e8767271f68ab72eab15a8e805c416b0636877f22a31572d10b718d/hostname",
    "HostsPath": "/var/lib/docker/containers/d00f94a31e8767271f68ab72eab15a8e805c416b0636877f22a31572d10b718d/hosts",
    "Id": "d00f94a31e8767271f68ab72eab15a8e805c416b0636877f22a31572d10b718d",
    "Image": "31fa814ba25ae3426f8710df7a48d567d4022527ef2c14964bb8bc45e653417c",
    "MountLabel": "",
    "Name": "/hopeful_lalande",
    "NetworkSettings": {
        "Bridge": "docker0",
        "Gateway": "172.17.42.1",
        "IPAddress": "172.17.0.8",
        "IPPrefixLen": 16,
        "MacAddress": "02:42:ac:11:00:08",
        "PortMapping": null,
        "Ports": {
            "5000/tcp": [
                {
                    "HostIp": "0.0.0.0",
                    "HostPort": "49153"
                }
            ]
        }
    },
    "Path": "python",
    "ProcessLabel": "",
    "ResolvConfPath": "/var/lib/docker/containers/d00f94a31e8767271f68ab72eab15a8e805c416b0636877f22a31572d10b718d/resolv.conf",
    "State": {
        "ExitCode": 0,
        "FinishedAt": "0001-01-01T00:00:00Z",
        "Paused": false,
        "Pid": 15189,
        "Restarting": false,
        "Running": true,
        "StartedAt": "2014-12-17T02:24:11.279426855Z"
    },
    "Volumes": {},
    "VolumesRW": {}
}
]
```

[/codesyntax]
 
输出一个JSON格式的Docker container配置和状态。
也可以通过指定名称，获取某项信息值，如下：
[codesyntax lang="bash"]

```
# docker inspect -f '{{ .NetworkSettings.IPAddress }}' hopeful_lalande
172.17.0.8
```

[/codesyntax]

# 停止Web应用

[codesyntax lang="bash"]

```
# docker stop hopeful_lalande
hopeful_lalande
```

[/codesyntax]
 
停止后，可以使用docker ps -a命令，列出之前所有docker容器
[codesyntax lang="bash"]

```
# docker ps -a
CONTAINER ID        IMAGE                    COMMAND                CREATED             STATUS                         PORTS               NAMES
d00f94a31e87        training/webapp:latest   "python app.py"        21 minutes ago      Exited (-1) 43 seconds ago                         hopeful_lalande     
7f22b335fb2c        fedora:latest            "/bin/sh -c 'while t   49 minutes ago      Exited (-1) 40 minutes ago                         silly_archimedes    
。。。
```

[/codesyntax]

# 重启Web应用

[codesyntax lang="bash"]

```
# docker start hopeful_lalande
hopeful_lalande
```

[/codesyntax]

# 删除Web应用

[codesyntax lang="bash"]

```
# docker rm hopeful_lalande
Error response from daemon: You cannot remove a running container. Stop the container before attempting removal or use -f
2014/12/17 10:49:32 Error: failed to remove one or more containers
```

[/codesyntax]
提示无法删除一个正在运行的container。
停止该container后，重新执行上条命令，成功删除container
