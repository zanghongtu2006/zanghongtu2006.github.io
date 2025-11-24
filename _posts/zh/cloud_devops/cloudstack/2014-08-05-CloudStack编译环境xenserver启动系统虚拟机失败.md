---
layout: post
lang: zh
translations:
  en: /en/cloudstack-e7-bc-96-e8-af-91-e7-8e-af-e5-a2-83xenserver-e5-90-af-e5-8a-a8-e7-b3-bb-e7-bb-9f-e8-99-9a-e6-8b-9f-e6-9c-ba-e5-a4-b1-e8-b4-a5/
  de: /de/cloudstack-e7-bc-96-e8-af-91-e7-8e-af-e5-a2-83xenserver-e5-90-af-e5-8a-a8-e7-b3-bb-e7-bb-9f-e8-99-9a-e6-8b-9f-e6-9c-ba-e5-a4-b1-e8-b4-a5/
title: "CloudStack编译环境xenserver启动系统虚拟机失败"
date: "2014-08-05 16:49:30"
slug: "cloudstack-e7-bc-96-e8-af-91-e7-8e-af-e5-a2-83xenserver-e5-90-af-e5-8a-a8-e7-b3-bb-e7-bb-9f-e8-99-9a-e6-8b-9f-e6-9c-ba-e5-a4-b1-e8-b4-a5"
categories: ["CloudStack"]
tags: ["can not create vdi", "copy_vhd_from_second"]
---
在社区git到最新的代码，编译测试一切正常。

添加xenserver主机之后，主存储二级存储也正常添加，看似一切正常。

确认启用资源域，之后开始创建系统虚拟机。

创建系统虚拟机第一步需要将系统虚拟机模板在二级存储上传至主存储：copy\_vhd\_from\_secondarystorage，此时开始出现异常

2013-07-31 15:03:52,077 WARN [xen.resource.XenServerStorageProcessor](DirectAgent-5:null) Catch Exceptioncom.cloud.utils.exception.CloudRuntimeException for template + due tocom.cloud.utils.exception.CloudRuntimeException: can not create vdiin sr 0ff33805-a202-a833-e5c5-f434a6a90a51

com.cloud.utils.exception.CloudRuntimeException:can not create vdi in sr0ff33805-a202-a833-e5c5-f434a6a90a51

atcom.cloud.hypervisor.xen.resource.XenServerStorageProcessor.copy\_vhd\_from\_secondarystorage(XenServerStorageProcessor.java:793)

atcom.cloud.hypervisor.xen.resource.XenServerStorageProcessor.copyTemplateToPrimaryStorage(XenServerStorageProcessor.java:864)

atcom.cloud.storage.resource.StorageSubsystemCommandHandlerBase.execute(StorageSubsystemCommandHandlerBase.java:70)

atcom.cloud.storage.resource.StorageSubsystemCommandHandlerBase.handleStorageCommands(StorageSubsystemCommandHandlerBase.java:49)

atcom.cloud.hypervisor.xen.resource.CitrixResourceBase.executeRequest(CitrixResourceBase.java:623)

atcom.cloud.hypervisor.xen.resource.XenServer56Resource.executeRequest(XenServer56Resource.java:73)

atcom.cloud.agent.manager.DirectAgentAttache$Task.run(DirectAgentAttache.java:186)

atjava.util.concurrent.Executors$RunnableAdapter.call(Executors.java:471)

atjava.util.concurrent.FutureTask$Sync.innerRun(FutureTask.java:334)

atjava.util.concurrent.FutureTask.run(FutureTask.java:166)

atjava.util.concurrent.ScheduledThreadPoolExecutor$ScheduledFutureTask.access$101(ScheduledThreadPoolExecutor.java:165)

atjava.util.concurrent.ScheduledThreadPoolExecutor$ScheduledFutureTask.run(ScheduledThreadPoolExecutor.java:266)

atjava.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1146)

atjava.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:615)

atjava.lang.Thread.run(Thread.java:679)

几多查找询问之后，是因为4.1之后代码中，因为版权问题，去掉了一个叫做vhd-utils的文件

该文件应该存放在代码的scripts/vm/hypervisor/xenserver/ 目录下

现在需要手动下载该文件，URL: [http://download.cloud.com.s3.amazonaws.com/tools/vhd-util](https://cwiki.apache.org/confluence/display/CLOUDSTACK/How+to+build+CloudStack)

下载完成之后，放到相应目录下，重新编译，启动。。。。

结果，不好使。。。。

重新初始化db重新部署，一切正常了。。。

系统虚拟机也创建成功。

所以，主机应该是需要重新添加，才会把该文件复制到主机中相应位置，我的测试环境只有一台xenserver，所以就直接初始化db了。

总结：到处是坑啊。。。。

参考页面：<https://cwiki.apache.org/confluence/display/CLOUDSTACK/How+to+build+CloudStack>
