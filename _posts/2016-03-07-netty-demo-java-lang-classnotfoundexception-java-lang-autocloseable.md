---
title: "Netty Demo java.lang.ClassNotFoundException: java.lang.AutoCloseable"
date: "2016-03-07 18:11:07"
slug: "netty-demo-java-lang-classnotfoundexception-java-lang-autocloseable"
layout: "post"
categories: ["未分类", "Java"]
tags: []
---
按照Netty权威指南，学习Netty中...
按照书上的Demo，写了一个TimeServer，遇到如下异常
[codesyntax lang="java"]

```
java.lang.NoClassDefFoundError: java/lang/AutoCloseable
	at java.lang.ClassLoader.defineClass1(Native Method)
	at java.lang.ClassLoader.defineClassCond(ClassLoader.java:631)
	at java.lang.ClassLoader.defineClass(ClassLoader.java:615)
	at java.security.SecureClassLoader.defineClass(SecureClassLoader.java:141)
	at java.net.URLClassLoader.defineClass(URLClassLoader.java:283)
	at java.net.URLClassLoader.access$000(URLClassLoader.java:58)
	at java.net.URLClassLoader$1.run(URLClassLoader.java:197)
	at java.security.AccessController.doPrivileged(Native Method)
	at java.net.URLClassLoader.findClass(URLClassLoader.java:190)
	at java.lang.ClassLoader.loadClass(ClassLoader.java:306)
	at sun.misc.Launcher$AppClassLoader.loadClass(Launcher.java:301)
	at java.lang.ClassLoader.loadClass(ClassLoader.java:247)
	at java.lang.ClassLoader.defineClass1(Native Method)
	at java.lang.ClassLoader.defineClassCond(ClassLoader.java:631)
	at java.lang.ClassLoader.defineClass(ClassLoader.java:615)
	at java.security.SecureClassLoader.defineClass(SecureClassLoader.java:141)
	at java.net.URLClassLoader.defineClass(URLClassLoader.java:283)
	at java.net.URLClassLoader.access$000(URLClassLoader.java:58)
	at java.net.URLClassLoader$1.run(URLClassLoader.java:197)
	at java.security.AccessController.doPrivileged(Native Method)
	at java.net.URLClassLoader.findClass(URLClassLoader.java:190)
	at java.lang.ClassLoader.loadClass(ClassLoader.java:306)
	at sun.misc.Launcher$AppClassLoader.loadClass(Launcher.java:301)
	at java.lang.ClassLoader.loadClass(ClassLoader.java:247)
Caused by: java.lang.ClassNotFoundException: java.lang.AutoCloseable
	at java.net.URLClassLoader$1.run(URLClassLoader.java:202)
	at java.security.AccessController.doPrivileged(Native Method)
	at java.net.URLClassLoader.findClass(URLClassLoader.java:190)
	at java.lang.ClassLoader.loadClass(ClassLoader.java:306)
	at sun.misc.Launcher$AppClassLoader.loadClass(Launcher.java:301)
	at java.lang.ClassLoader.loadClass(ClassLoader.java:247)
	... 24 more
Exception in thread "main"
```

[/codesyntax]
百度了一下，提示换用jdk7再次尝试。
本人运行环境为1.6.0\_39，引入jar包为netty-all-5.0.0.Alpha2.jar，更换成1.7.0\_71之后，运行成功。
java.lang.AutoCloseable：该Class只在jdk 7 以上版本可用。
如果要求使用jdk 1.6版本环境运行，可以切换netty版本到 4.0.33.Final。
