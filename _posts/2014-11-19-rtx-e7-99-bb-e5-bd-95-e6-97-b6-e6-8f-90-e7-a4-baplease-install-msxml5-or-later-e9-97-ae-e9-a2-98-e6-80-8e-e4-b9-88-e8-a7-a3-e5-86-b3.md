---
title: "RTX登录时提示“please install msxml5 or later”问题怎么解决"
date: "2014-11-19 13:57:48"
slug: "rtx-e7-99-bb-e5-bd-95-e6-97-b6-e6-8f-90-e7-a4-baplease-install-msxml5-or-later-e9-97-ae-e9-a2-98-e6-80-8e-e4-b9-88-e8-a7-a3-e5-86-b3"
layout: "post"
categories: ["Windows"]
tags: ["RTX", "msxml5"]
---
公司用腾讯RTX作为内部通讯。
我把原有的Office 2007换成2010之后，就无法登陆了。
提示please install msxml5 or later。应该是属于版本兼容问题。2010删掉了msxml5的dll文件，换用了更高版本的。
解决方案：下载原有的2个dll，msxml5.dll和msxml5r.dll
32位系统：复制到c:\windows\system32
64位系统：复制到c:\Windows\SysWOW64
以管理员模式打开cmd，在相应目录下执行命令 regsvr32 msxml5.dll
 
 
相关文件下载：[http://pan.baidu.com/s/1fbKpo](http://pan.baidu.com/s/1fbKpo "http://pan.baidu.com/s/1fbKpo")
