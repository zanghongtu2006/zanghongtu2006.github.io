---
layout: post
lang: zh
translations:
  en: /en/e7-a6-81-e6-ad-a2cloudstack-e5-88-a0-e9-99-a4xenserver-e5-8e-9f-e6-9c-89-e8-99-9a-e6-8b-9f-e6-9c-ba/
  de: /de/e7-a6-81-e6-ad-a2cloudstack-e5-88-a0-e9-99-a4xenserver-e5-8e-9f-e6-9c-89-e8-99-9a-e6-8b-9f-e6-9c-ba/
title: "禁止CloudStack删除Xenserver原有虚拟机"
date: "2014-08-05 16:51:22"
slug: "e7-a6-81-e6-ad-a2cloudstack-e5-88-a0-e9-99-a4xenserver-e5-8e-9f-e6-9c-89-e8-99-9a-e6-8b-9f-e6-9c-ba"
categories: ["CloudStack"]
tags: ["xenserver", "删除vm"]
---
CloudStack在文档中指明需要加入一台干净的Xenserver作为hyperviser。

但是实际使用中，总会存在不同的需求，很多场景是试用CloudStack接管当前已有的hyperviser而非完整重新部署，那么之前在hyperviser中启动的vm，则会被判断为非CloudStack管理而被关闭或删除，如此则会产生对现有环境的不良影响。现实部署环境中，总有些情况，是要求保留现有环境中已有的vm。

以Xenserver为例，非CS管理的vm，会被关闭，CS对于xenserver中vm生命周期的管理比较特殊，在关闭vm之后，还会删除vm实例，只保留磁盘文件，即vdi，这样的结果，对于原有vm设置并不熟悉的管理员来说，相当于噩梦一般的存在了。

那么我们从代码中来看一下为什么虚拟机会被删除。以CS 4.0.2为例：

在XenCenter中新建一台vm，等待一段时间就会发现，该vm关机并且消失了。

此时查看log，会发现如下信息：

2013-08-05 20:19:47,038 WARN [cloud.vm.VirtualMachineManagerImpl](DirectAgent-84:null) Found an alien VM Windows 7 (32-bit) (1)

2013-08-05 20:19:47,038 DEBUG[cloud.vm.VirtualMachineManagerImpl] (DirectAgent-84:null) Cleaningup a VM that is no longer found : Windows 7 (32-bit) (1)

2013-08-05 20:19:47,045 DEBUG [agent.transport.Request](DirectAgent-84:null) Seq 1-229638607: Sending  {Cmd , MgmtId: 345049672023, via: 1, Ver: v1, Flags: 100111,[{"StopCommand":{"isProxy":false,"vmName":"Windows 7 (32-bit)(1)","wait":0}}] }

2013-08-05 20:19:47,045 DEBUG [agent.transport.Request](DirectAgent-84:null) Seq 1-229638607: Executing: { Cmd , MgmtId: 345049672023, via: 1, Ver: v1,Flags: 100111, [{"StopCommand":{"isProxy":false,"vmName":"Windows 7(32-bit) (1)","wait":0}}] }

“Windows 7 (32-bit) (1)” 是我所建vm的名字。

第一行log出现在VirtualMachineManagerImpl.java中的convertToInfos(Map>)方法中，
```java
protected Map<Long, AgentVmInfo> convertToInfos(final Map<String, Pair<String, State>> newStates) {
    final HashMap<Long, AgentVmInfo> map = new HashMap<Long, AgentVmInfo>();
    if (newStates == null) {
        return map;
    }
    Collection<VirtualMachineGuru<? extends VMInstanceVO>> vmGurus = _vmGurus.values();
    boolean is_alien_vm = true;
    long alien_vm_count = -1;
    for (Map.Entry<String, Pair<String, State>> entry : newStates.entrySet()) {
        is_alien_vm = true;
        for (VirtualMachineGuru<? extends VMInstanceVO> vmGuru : vmGurus) {
            String name = entry.getKey();
            VMInstanceVO vm = vmGuru.findByName(name);
            if (vm != null) {
                map.put(vm.getId(), new AgentVmInfo(entry.getKey(), vmGuru, vm, entry.getValue().second(), entry.getValue().first()));
                is_alien_vm = false;
                break;
            }
            Long id = vmGuru.convertToId(name);
            if (id != null) {
                map.put(id, new AgentVmInfo(entry.getKey(), vmGuru, null, entry.getValue().second(), entry.getValue().first()));
                is_alien_vm = false;
                break;
            }
        }
        // alien VMs
        if (is_alien_vm){
            map.put(alien_vm_count--, new AgentVmInfo(entry.getKey(), null, null, entry.getValue().second(), entry.getValue().first()));
            s_logger.warn("Found an alien VM " + entry.getKey());
        }
    }
    return map;
}
```
该方法会在开始定义一个map作为返回值，之后遍历db中所有的vm（vmGurus)并与newStates比较，判断为alien的vm会赋一个负数值，并放入map中返回给上一级方法，其中map的value是newAgentVmInfo(),传入参数中guru和vm为null。上一级方法调用者为：deltaSync和fullSync。

在deltaSync会遍历返回的map，对于vm为null的项，则判定为非CS管理的alien vm，之后进入cleanup发送StopCommand，此时则会看到之前的第二行log。
```java
public void deltaSync(Map<String, Pair<String, State>> newStates) {
    Map<Long, AgentVmInfo> states = convertToInfos(newStates);
    for (Map.Entry<Long, AgentVmInfo> entry : states.entrySet()) {
        AgentVmInfo info = entry.getValue();
        VMInstanceVO vm = info.vm;
        Command command = null;
        if (vm != null) {
            Host host = _resourceMgr.findHostByGuid(info.getHostUuid());
            long hId = host.getId();
            HypervisorGuru hvGuru = _hvGuruMgr.getGuru(vm.getHypervisorType());
            command = compareState(hId, vm, info, false, hvGuru.trackVmHostChange());
        } else {
            if (s_logger.isDebugEnabled()) {
            s_logger.debug("Cleaning up a VM that is no longer found <deltaSync>: " + info.name);
        }
        command = cleanup(info.name);
    }
    if (command != null){
        try {
            Host host =_resourceMgr.findHostByGuid(info.getHostUuid());
            if (host != null) {
                Answer answer = _agentMgr.send(host.getId(), cleanup(info.name));
                if (!answer.getResult()) {
                    s_logger.warn("Unable to stop a VM due to " + answer.getDetails());
                }
            }
        } catch (Exception e) {
            s_logger.warn("Unable to stop a VM due to " + e.getMessage());
        }
    }
}
```
fullSync中有类似逻辑，会在host刚刚加入CS或者重启CSmanagement-server的时候调用到，代码见fullSync最后一段逻辑：

```java
for (final AgentVmInfo left : infos.values()) {
    if (!VirtualMachineName.isValidVmName(left.name)) continue;  // if the vm doesn't follow CS naming ignore it for stopping
    try {
        Host host = _hostDao.findByGuid(left.getHostUuid());
        if (host != null){
            s_logger.warn("Stopping a VM which we do not have any record of " + left.name);
            Answer answer = _agentMgr.send(host.getId(), cleanup(left.name));
            if (!answer.getResult()) {
                s_logger.warn("Unable to stop a VM due to " + answer.getDetails());
            }
        }
    } catch (Exception e) {
        s_logger.warn("Unable to stop a VM due to " + e.getMessage());
    }
}

```
第一行中的if语句给出了一个合理的设计，如果命名不符合CS命名规则，则不对该VM做任何处理，如果命名规则符合CS的命名规则，则会进入cleanup流程，这样既不会删除原有vm，同时又保证了CS的管理的虚拟机有唯一的命名。

但是fullSync只在host和CS连接的时候运行一次，其他时候都是由deltaSync对vm状态进行处理，所以，alienvm仍然会被删除。

这应该是4.0.2在尝试兼容额外虚拟机的时候，所遗留的bug。

可以参考fullSync的逻辑，将上面deltaSync稍作修改，对**command =cleanup(info.name);**进行判断，修改为：

```java
if (VirtualMachineName.isValidVmName(info.name)){
    command =cleanup(info.name);
}
```
如此则可避免CS对非CS管理的vm做额外处理，从而删除掉我们并不想删除的vm。

后果：cloudstack的capacity是根据db来计算的，如此修改则可能对capacity造成影响，使统计值与真实值出现偏差。此方法仅可用于特殊需求环境，或者暂时无法移除额外虚拟机的情况。
