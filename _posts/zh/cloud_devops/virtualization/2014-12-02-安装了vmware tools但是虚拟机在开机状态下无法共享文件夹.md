---
title: "安装了vmware tools但是虚拟机在开机状态下无法共享文件夹"
date: "2014-12-02 11:01:55"
slug: "e5-ae-89-e8-a3-85-e4-ba-86vmware-tools-e4-bd-86-e6-98-af-e8-99-9a-e6-8b-9f-e6-9c-ba-e5-9c-a8-e5-bc-80-e6-9c-ba-e7-8a-b6-e6-80-81-e4-b8-8b-e6-97-a0-e6-b3-95-e5-85-b1-e4-ba-ab-e6-96-87-e4-bb-b6"
layout: "post"
categories: ["Linux"]
tags: ["Vmware", "hgfs"]
---
产生根源是因为Linux kernel升级之后，vmware-tools没有及时更新。
网上有个第三方的解决方案。测试centos6.4和Ubuntu 14.04 desktop可用
1、将vmware-tools复制出来
2、下载patch文件，链接见底部
3、`[codesyntax lang="bash"]`

```
# cd ~/vmware-tools-distrib/lib/modules/source
# sudo tar xf vmhgfs.tar
# sudo wget https://raw.github.com/rasa/vmware-tools-patches/master/patches/vmhgfs/vmhgfs-d_count-kernel-3.11-tools-9.6.0.patch
# sudo patch -p0 <vmhgfs-d_count-kernel-3.11-tools-9.6.0.patch
# sudo mv vmhgfs.tar vmhgfs.orig.tar
# sudo tar cf vmhgfs.tar vmhgfs-only
#cd ~/vmware-tools-distrib
```

`[/codesyntax]`
4、./vmware-install.pl 重新编译安装
 
如果patch失败，可以尝试手动将patch中的内容替换到相应文件中，patch内容见链接下
[https://raw.githubusercontent.com/rasa/vmware-tools-patches/master/patches/vmhgfs/vmhgfs-d\_count-kernel-3.11-tools-9.6.0.patch](https://raw.githubusercontent.com/rasa/vmware-tools-patches/master/patches/vmhgfs/vmhgfs-d_count-kernel-3.11-tools-9.6.0.patch "https://raw.githubusercontent.com/rasa/vmware-tools-patches/master/patches/vmhgfs/vmhgfs-d_count-kernel-3.11-tools-9.6.0.patch")
`Patch：`
[codesyntax lang="diff"]

```
--- vmhgfs-only/inode.c 2013-08-15 22:32:22.000000000 -0700
+++ vmhgfs-only.patched/inode.c 2013-09-16 21:31:12.323041668 -0700
@@ -31,6 +31,9 @@
#include
#endif
#include
+#if LINUX_VERSION_CODE >= KERNEL_VERSION(3, 11, 0)
+#include
+#endif
#include "compat_cred.h"
#include "compat_fs.h"
@@ -1890,7 +1893,11 @@
#endif
&inode->i_dentry,
d_alias) {
+#if LINUX_VERSION_CODE >= KERNEL_VERSION(3, 11, 0)
+ int dcount = d_count(dentry);
+#else
int dcount = dentry->d_count;
+#endif
if (dcount) {
LOG(4, ("Found %s %d \n", dentry->d_name.name, dcount));
return HgfsAccessInt(dentry, mask & (MAY_READ | MAY_WRITE | MAY_EXEC));
@@ -1943,10 +1950,12 @@
list_for_each(pos, &inode->i_dentry) {
int dcount;
struct dentry *dentry = list_entry(pos, struct dentry, d_alias);
-#if LINUX_VERSION_CODE d_count);
-#else
+#if LINUX_VERSION_CODE >= KERNEL_VERSION(3, 11, 0)
+ dcount = d_count(dentry);
+#elif LINUX_VERSION_CODE >= KERNEL_VERSION(2, 6, 38)
dcount = dentry->d_count;
+#else
+ dcount = atomic_read(&dentry->d_count);
#endif
if (dcount) {
LOG(4, ("Found %s %d \n", (dentry)->d_name.name, dcount));
```

[/codesyntax]
