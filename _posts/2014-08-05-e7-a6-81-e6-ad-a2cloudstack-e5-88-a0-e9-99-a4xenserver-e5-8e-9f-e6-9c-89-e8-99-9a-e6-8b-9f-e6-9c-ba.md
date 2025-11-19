---
title: "禁止CloudStack删除Xenserver原有虚拟机"
date: "2014-08-05 16:51:22"
slug: "e7-a6-81-e6-ad-a2cloudstack-e5-88-a0-e9-99-a4xenserver-e5-8e-9f-e6-9c-89-e8-99-9a-e6-8b-9f-e6-9c-ba"
layout: "post"
categories: ["CloudStack"]
tags: ["xenserver", "删除vm"]
---
CloudStack在文档中指明需要加入一台干净的Xenserver作为hyperviser。

但是实际使用中，总会存在不同的需求，很多场景是试用CloudStack接管当前已有的hyperviser而非完整重新部署，那么之前在hyperviser中启动的vm，则会被判断为非CloudStack管理而被关闭或删除，如此则会产生对现有环境的不良影响。现实部署环境中，总有些情况，是要求保留现有环境中已有的vm。

以Xenserver为例，非CS管理的vm，会被关闭，CS对于xenserver中vm生命周期的管理比较特殊，在关闭vm之后，还会删除vm实例，只保留磁盘文件，即vdi，这样的结果，对于原有vm设置并不熟悉的管理员来说，相当于噩梦一般的存在了。

那么我们从代码中来看一下为什么虚拟机会被删除。以CS 4.0.2为例：

在XenCenter中新建一台vm，等待一段时间就会发现，该vm关机并且消失了。

此时查看log，会发现如下信息：

2013-08-05 20:19:47,038 WARN [cloud.vm.VirtualMachineManagerImpl](DirectAgent-84:null) Found an alien VM Windows 7 (32-bit) (1)

2013-08-05 20:19:47,038 DEBUG[cloud.vm.VirtualMachineManagerImpl] (DirectAgent-84:null) Cleaningup a VM that is no longer found : Windows 7 (32-bit) (1)

2013-08-05 20:19:47,045 DEBUG [agent.transport.Request](DirectAgent-84:null) Seq 1-229638607: Sending  {Cmd , MgmtId: 345049672023, via: 1, Ver: v1, Flags: 100111,[{"StopCommand":{"isProxy":false,"vmName":"Windows 7 (32-bit)(1)","wait":0}}] }

2013-08-05 20:19:47,045 DEBUG [agent.transport.Request](DirectAgent-84:null) Seq 1-229638607: Executing: { Cmd , MgmtId: 345049672023, via: 1, Ver: v1,Flags: 100111, [{"StopCommand":{"isProxy":false,"vmName":"Windows 7(32-bit) (1)","wait":0}}] }

“Windows 7 (32-bit) (1)” 是我所建vm的名字。

第一行log出现在VirtualMachineManagerImpl.java中的convertToInfos(Map>)方法中，

1. protected Map<Long, AgentVmInfo> convertToInfos(final Map<String, Pair<String, State>> newStates) {
2. final HashMap<Long, AgentVmInfo> map = new HashMap<Long, AgentVmInfo>();
3. if (newStates == null) {
4. return map;
5. }
6. Collection<VirtualMachineGuru<? extends VMInstanceVO>> vmGurus = \_vmGurus.values();
7. boolean is\_alien\_vm = true;
8. long alien\_vm\_count = -1;
9. for (Map.Entry<String, Pair<String, State>> entry : newStates.entrySet()) {
10. is\_alien\_vm = true;
11. for (VirtualMachineGuru<? extends VMInstanceVO> vmGuru : vmGurus) {
12. String name = entry.getKey();
13. VMInstanceVO vm = vmGuru.findByName(name);
14. if (vm != null) {
15. map.put(vm.getId(), new AgentVmInfo(entry.getKey(), vmGuru, vm, entry.getValue().second(), entry.getValue().first()));
16. is\_alien\_vm = false;
17. break;
18. }
19. Long id = vmGuru.convertToId(name);
20. if (id != null) {
21. map.put(id, new AgentVmInfo(entry.getKey(), vmGuru, null, entry.getValue().second(), entry.getValue().first()));
22. is\_alien\_vm = false;
23. break;
24. }
25. }
26. // alien VMs
27. if (is\_alien\_vm){
28. map.put(alien\_vm\_count--, new AgentVmInfo(entry.getKey(), null, null, entry.getValue().second(), entry.getValue().first()));
29. s\_logger.warn("Found an alien VM " + entry.getKey());
30. }
31. }
32. return map;
33. }

该方法会在开始定义一个map作为返回值，之后遍历db中所有的vm（vmGurus)并与newStates比较，判断为alien的vm会赋一个负数值，并放入map中返回给上一级方法，其中map的value是newAgentVmInfo(),传入参数中guru和vm为null。上一级方法调用者为：deltaSync和fullSync。

在deltaSync会遍历返回的map，对于vm为null的项，则判定为非CS管理的alien vm，之后进入cleanup发送StopCommand，此时则会看到之前的第二行log。

1. public void deltaSync(Map<String, Pair<String, State>> newStates) {
2. Map<Long, AgentVmInfo> states = convertToInfos(newStates);
4. for (Map.Entry<Long, AgentVmInfo> entry : states.entrySet()) {
5. AgentVmInfo info = entry.getValue();
6. VMInstanceVO vm = info.vm;
7. Command command = null;
8. if (vm != null) {
9. Host host = \_resourceMgr.findHostByGuid(info.getHostUuid());
10. long hId = host.getId();
12. HypervisorGuru hvGuru = \_hvGuruMgr.getGuru(vm.getHypervisorType());
13. command = compareState(hId, vm, info, false, hvGuru.trackVmHostChange());
14. } else {
15. if (s\_logger.isDebugEnabled()) {
16. s\_logger.debug("Cleaning up a VM that is no longer found <deltaSync>: " + info.name);
17. }
18. command = cleanup(info.name);
19. }
20. if (command != null){
21. try {
22. Host host = \_resourceMgr.findHostByGuid(info.getHostUuid());
23. if (host != null){
24. Answer answer = \_agentMgr.send(host.getId(), cleanup(info.name));
25. if (!answer.getResult()) {
26. s\_logger.warn("Unable to stop a VM due to " + answer.getDetails());
27. }
28. }
29. } catch (Exception e) {
30. s\_logger.warn("Unable to stop a VM due to " + e.getMessage());
31. }
32. }
33. }
34. }

fullSync中有类似逻辑，会在host刚刚加入CS或者重启CSmanagement-server的时候调用到，代码见fullSync最后一段逻辑：

1. for (final AgentVmInfo left : infos.values()) {
2. if (!VirtualMachineName.isValidVmName(left.name)) continue;  // if the vm doesn't follow CS naming ignore it for stopping
3. try {
4. Host host = \_hostDao.findByGuid(left.getHostUuid());
5. if (host != null){
6. s\_logger.warn("Stopping a VM which we do not have any record of " + left.name);
7. Answer answer = \_agentMgr.send(host.getId(), cleanup(left.name));
8. if (!answer.getResult()) {
9. s\_logger.warn("Unable to stop a VM due to " + answer.getDetails());
10. }
11. }
12. } catch (Exception e) {
13. s\_logger.warn("Unable to stop a VM due to " + e.getMessage());
14. }
15. }

第一行中的if语句给出了一个合理的设计，如果命名不符合CS命名规则，则不对该VM做任何处理，如果命名规则符合CS的命名规则，则会进入cleanup流程，这样既不会删除原有vm，同时又保证了CS的管理的虚拟机有唯一的命名。

但是fullSync只在host和CS连接的时候运行一次，其他时候都是由deltaSync对vm状态进行处理，所以，alienvm仍然会被删除。

这应该是4.0.2在尝试兼容额外虚拟机的时候，所遗留的bug。

可以参考fullSync的逻辑，将上面deltaSync稍作修改，对**command =cleanup(info.name);**进行判断，修改为：

1. if (VirtualMachineName.isValidVmName(info.name)){
2. command =cleanup(info.name);
3. }

如此则可避免CS对非CS管理的vm做额外处理，从而删除掉我们并不想删除的vm。

后果：cloudstack的capacity是根据db来计算的，如此修改则可能对capacity造成影响，使统计值与真实值出现偏差。此方法仅可用于特殊需求环境，或者暂时无法移除额外虚拟机的情况。
