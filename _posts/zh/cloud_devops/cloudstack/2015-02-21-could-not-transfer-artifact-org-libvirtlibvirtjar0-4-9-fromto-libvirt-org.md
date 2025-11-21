---
title: "Could not transfer artifact org.libvirt:libvirt:jar:0.4.9 from/to libvirt-org "
date: "2015-02-21 10:23:38"
slug: "could-not-transfer-artifact-org-libvirtlibvirtjar0-4-9-fromto-libvirt-org"
layout: "post"
categories: ["CloudStack"]
tags: ["CloudStack"]
---
CloudStack编译源码出现以下错误
[codesyntax lang="text"]

```
[ERROR] Failed to execute goal on project cloud-plugin-hypervisor-kvm: Could not resolve dependencies for project org.apache.cloudstack:cloud-plugin-hypervisor-kvm:jar:4.2.0: Could not transfer artifact org.libvirt:libvirt:jar:0.4.9 from/to libvirt-org (http://libvirt.org/maven2): GET request of: org/libvirt/libvirt/0.4.9/libvirt-0.4.9.jar from libvirt-org failed: Premature end of Content-Length delimited message body (expected: 70699; received: 42064 -> [Help 1]
[ERROR] 
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
```

[/codesyntax]

查看良久，发现是libvirt0.4.9.jar下载失败
从另一个源中copy一份覆盖到本地，成功编译通过
