---
title: "Linux下无限期免激活使用UltraEdit的方法"
date: "2016-07-26 16:33:26"
slug: "linux-e4-b8-8b-e6-97-a0-e9-99-90-e6-9c-9f-e5-85-8d-e6-bf-80-e6-b4-bb-e4-bd-bf-e7-94-a8ultraedit-e7-9a-84-e6-96-b9-e6-b3-95"
layout: "post"
categories: ["Linux"]
tags: ["UltraEdit"]
---
转载自：http://www.myzhenai.com.cn/post/1957.html http://www.myzhenai.com/thread-17381-1-1.html
Linux下无限期免激活的方法网上有很多版本，但现在UltraEdit升级到15.0.0.11版后这些方法都不管用了.其实都是删除UltraEdit的配置文件来重复试用，但是网上的方法漏删了一些文件导致不起作用，按照网上的那些方法仍然会提示30天试用期过期.一点关闭UltraEdit窗口程序就退出了.
网上的方法：
[codesyntax lang="bash"]

```
rm -rf /home/pwd/.idm/uex/uex.conf
rm -rf /root/.idm/uex/uex.conf
```

[/codesyntax]
我按照这些方法来试过，不起作用，我甚至将.idm整个目录删除了还是弹出30天试用期已到期的提示.折腾了几天终于解决了这个问题，我把这些写了个脚本，可以一键解决.
[codesyntax lang="bash"]

```
# !/bin/bash
cuper=`pwd`
rm -rf $cuper/.idm/uex/*
rm -rf $cuper/.idm/*.spl
rm -rf /root/.idm/uex/*
rm -rf /root/.idm/*.spl
rm -rf /tmp/*.spl
rm -rf $cuper/.local/share/Trash/files/usr/local/share/uex
rm -rf $cuper/.local/share/Trash/files/usr/local/share/doc/uex
rm -rf $cuper/.local/share/Trash/files/usr/local/bin/uex
rm -rf $cuper/.local/share/Trash/files/uex
rm -rf /home/.Trash-0/files/*
```

[/codesyntax]
