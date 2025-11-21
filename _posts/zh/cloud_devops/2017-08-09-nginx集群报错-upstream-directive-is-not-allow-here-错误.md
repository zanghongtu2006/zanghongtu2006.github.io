---
title: "nginx集群报错“upstream”directive is not allow here 错误"
date: "2017-08-09 10:23:08"
slug: "nginx-e9-9b-86-e7-be-a4-e6-8a-a5-e9-94-99upstreamdirective-is-not-allow-here-e9-94-99-e8-af-af"
layout: "post"
categories: ["运维管理"]
tags: ["nginx"]
---
nginx集群报错“upstream”directive is not allow here 错误  

当设定好 upstream 如下:

```
upstream chinacloudly {
	server www.chinacloudly.com;
}
```

执行命令:/usr/local/nginx/sbin/nginx -s reload 时 报错如下:

```
nginx: [emerg] "upstream" directive is not allowed here in C:\nginx/conf/nginx.conf:1
```

后来百度了一下原来是upstream 位置放错了, upstream位置应该放在http模块里面，但必须是在server模块的外面. 应该是下面这样的结构:

```
http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;

	upstream chinacloudly {
		server www.chinacloudly.com;
	}

	server {
		listen       80;
		server_name  chinacloudly.max.com;

		#charset koi8-r;

		#access_log  logs/host.access.log  main;

		location / {
			proxy_pass   http://chinacloudly;
			index  index.html index.htm;
		}        
	}
}
```
