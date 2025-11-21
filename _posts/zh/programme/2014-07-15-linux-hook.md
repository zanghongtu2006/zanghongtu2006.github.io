---
layout: post
lang: zh
title: "Linux hook"
date: "2014-07-15 17:29:46"
slug: "linux-hook"
categories: ["C&C++", "Linux"]
tags: ["linux", "hook"]
---
开始研究Linux 钩子。
首先确定一个函数，hook之后没有多大危害的，所以试试time()
先写一个同名函数：

hook.c
`#include 
long time(void *unused){
    printf (“\nHook!!\n”);
    return 1234;
}`

编译为共享库：

`# gcc −o hook.so hook.c  −fPIC −shared`

编写测试程序：

test.c
`#include 
#include
int main(){
   long timeval = time(NULL);
   printf ("%d", timeval);
   return 0;
}`

编译为可执行文件：

`# gcc test test.c`

分别以普通方式和LD\_PRELOAD执行test：

`$ ./test
1377840884
$ LD_PRELOAD=./hook.so ./test
Hook!!
1234`

参考页面：<http://ekd123.is-programmer.com/posts/27960.html>
