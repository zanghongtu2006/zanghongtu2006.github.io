---
title: "CloudStack注册模板ISO"
date: "2015-08-14 06:58:20"
slug: "post-483"
layout: "post"
categories: ["CloudStack"]
tags: []
draft: true
---
CloudStack的模板和ISO 管理比较类似，模板和ISO在DB中保存在同一个表内vm\_template、template\_zone\_ref，内容保存在二级存储中。
在UI上注册之后，会将基本信息写入vm\_template表中，并向SSVM发送命令，在SSVM中进行下载，之后启动异步任务，检测下载进度。
下载完成后，会进行一系列检测和处理。
最后，将模板信息写入模板文件同目录的template.properties，则本次下载结束，更新DB状态为可用。
