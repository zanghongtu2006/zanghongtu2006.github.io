---
layout: post
lang: zh
translations:
  en: /en/cloudstack-debug-e7-8e-af-e5-a2-83vmware-e7-bc-96-e8-af-91-e9-94-99-e8-af-af/
  de: /de/cloudstack-debug-e7-8e-af-e5-a2-83vmware-e7-bc-96-e8-af-91-e9-94-99-e8-af-af/
title: "CloudStack debug环境vmware编译错误"
date: "2014-08-05 16:50:17"
slug: "cloudstack-debug-e7-8e-af-e5-a2-83vmware-e7-bc-96-e8-af-91-e9-94-99-e8-af-af"
categories: ["CloudStack"]
tags: ["Failed to executegoal"]
---
继续编译以支持vmware/netscaler/netapp等nonoss的plugin。

按社区文档，下载一堆包到deps，运行install-non-oss.sh

结果如下:

[ERROR] Failed to executegoal

org.apache.maven.plugins:maven-surefire-plugin:2.12:test

(default-test) on projectcloud-plugin-hypervisor-vmware: There are

test failures.

[ERROR]

[ERROR] Please referto

/opt/cloudstack/plugins/hypervisors/vmware/target/surefire-reports

for the individual testresults.

[ERROR] -> [Help1]

[ERROR]

[ERROR] To see the full stacktrace of the

errors, re-run Maven with the-e switch.

[ERROR] Re-run Maven using the-X switch to

enable full debuglogging.

[ERROR]

[ERROR] For more informationabout the errors

and possible solutions, pleaseread the following

articles:

[ERROR] [Help 1]

http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException

[ERROR]

[ERROR] After correcting theproblems, you can

resume the build with thecommand

[ERROR]   mvn-rf

:cloud-plugin-hypervisor-vmware

神一般的错误再现。

接受上次教训，自己读文档，发现一个缺失的步骤....

In case of 4.2/master, Minsuggests on ML: To build non-oss build, you need to first downloadVmware 5.1 SDK from<https://my.vmware.com/group/vmware/get-download?downloadGroup=VSP510-WEBSDK-510> (Version:5.1, Release-date: 2012-09-10, Build: 774886) to a temp directory.This is a zip file, unzip file and you will see a vim25.jar in/vsphere-ws/java/JAXWS/lib. Place this vim25.jar in deps folder andrename it as vim25\_51.jar, then run: deps/install-non-oss.sh toinstall it into your m2 repo.

意思就是要下载新版的vim25，覆盖掉之前下载放到deps下的

然后再次运行install-non-oss.sh

clean之后重新编译。。。终于过去了

总结：依然是坑啊。。。

仔细读文档是必须的：https://cwiki.apache.org/confluence/display/CLOUDSTACK/How+to+build+CloudStack

一行都不能落下啊，英文不想读的童鞋。。。看我的教训也成
