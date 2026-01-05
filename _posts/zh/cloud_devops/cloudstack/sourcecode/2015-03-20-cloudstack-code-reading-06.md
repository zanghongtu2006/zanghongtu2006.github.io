---
layout: post
lang: zh
translations:
  en: /en/cloudstack-code-reading-06/
  zh: /zh/cloudstack-code-reading-06/
permalink: /zh/cloudstack-code-reading-06/
slug: "cloudstack-code-reading-06"
title: "CloudStack 代码阅读（六）—— Orchestration Engine 源码阅读"
date: "2015-03-20 23:00:03"
categories: ["CloudStack"]
tags: ["orchestration", "workflow", "vm", "source-analysis"]
draft: false
---
CloudStack 的 Orchestration Engine（资源编排引擎）是整个 IaaS 系统的“中央神经系统”。任何 VM 生命周期操作，例如 `deployVirtualMachine`、`startVM`、`rebootVM`、`migrateVM`，最终都会走入这一套 **Workflow + StateMachine + Manager 调用链**。

本篇按照“源码走读”方式，不会只讲概念，而是依据 CloudStack 4.2.2 中真实的目录结构、类名、调用栈来解释整个 VM 部署流程。

# 1. Orchestration Engine 的主要模块

```text
engine/
  └ orchestration/
       ├── src/com/cloud/vm/VirtualMachineManagerImpl.java
       ├── src/com/cloud/vm/VirtualMachineGuru.java
       ├── src/com/cloud/deploy/
       │      ├── DeploymentPlanningManagerImpl.java
       │      ├── FirstFitPlanner.java
       │      └── DeploymentPlan.java
       ├── src/com/cloud/network/NetworkOrchestrator.java
       ├── src/com/cloud/storage/VolumeManagerImpl.java
       └── workflow/
             ├── VMOperationListener.java
             └── orchestrateDeployVM
```

模块分层：

- **VM Orchestrator**：控制 VM 整体生命周期  
- **Deploy Planner**：负责选择物理主机  
- **Network Orchestrator**：准备 VM 网络、NIC、VR  
- **Volume/Storage Orchestrator**：准备 Root/Data 卷、模板、存储池  
- **Guru（虚拟机专家）**：每种 Hypervisor 的实现差异由 Guru 决定  
- **Workflow Engine**：顺序执行步骤（Steps）

# 2. 从 API 到 Orchestration：完整调用链

用户调用：

```text
deployVirtualMachine
```

对应类：

```java
org.apache.cloudstack.api.command.user.vm.DeployVMCmd
```

其 `execute()` 方法调用：

```java
UserVm result = _userVmService.deployVirtualMachine(this);
```

我们跟进 `_userVmService`：

```java
UserVmManagerImpl.deployVirtualMachine()
```

再进入 Orchestration Engine：

```java
VirtualMachineManagerImpl.orchestrateDeployVM()
```

完整调用栈如下：

```text
DeployVMCmd.execute()
 → UserVmManagerImpl.deployVirtualMachine()
   → VirtualMachineManagerImpl.orchestrateDeployVM()
     → DeploymentPlanningManagerImpl.plan()
     → NetworkOrchestrator.prepare()
     → VolumeManagerImpl.prepare()
     → Guru.finalizeDeployment()
     → send(StartCommand) to Agent
```

# 3. DeploymentPlanningManager：主机选择核心

位于：

```text
engine/orchestration/src/com/cloud/deploy/DeploymentPlanningManagerImpl.java
```

核心方法：

```java
@Override
public DeployDestination plan(VirtualMachineProfile vmProfile, DeploymentPlan plan, ExcludeList avoid) {
    DataCenter dc = _dcDao.findById(plan.getDataCenterId());
    List<Cluster> clusters = _clusterDao.listByDcId(dc.getId());
    for (Cluster cluster : clusters) {
        if (suitable(cluster, vmProfile)) {
            Host host = findHost(cluster, vmProfile);
            StoragePool pool = findStorage(cluster, vmProfile);
            return new DeployDestination(dc, pod, cluster, host, pool);
        }
    }
    throw new InsufficientServerCapacityException();
}
```

关键逻辑步骤：

1. 获取 zone/pod/cluster 列表  
2. 遍历 cluster，检查是否满足 VM 规格  
3. 在 cluster 内部选择 Host  
4. 在 cluster 内选择合适存储池  
5. 组成 `DeployDestination`

# 4. FirstFitPlanner：CloudStack 的默认调度器

位于：

```text
engine/orchestration/src/com/cloud/deploy/FirstFitPlanner.java
```

主要策略：

- CPU/Memory 要求足够  
- 同时考虑 StoragePool 容量  
- 优先选择低负载 Cluster  
- 过滤掉 avoid 列表中的 host/pool

示例源码：

```java
List<Host> hosts = _hostDao.listAllUpAndEnabledByCluster(clusterId);
for (Host host : hosts) {
    if (host.getCpu() > vmCpu && host.getRam() > vmMem) {
        return host;
    }
}
```

# 5. NetworkOrchestrator：准备网络环境

位于：

```text
engine/orchestration/src/com/cloud/network/NetworkOrchestrator.java
```

部署 VM 的网络准备流程：

```text
prepare(vm, destination)
 → allocateNIC()
 → implementNetwork()
 → configureVirtualRouter()
```

### 5.1 NIC 分配

```java
NicProfile nic = new NicProfile();
nic.setIPv4Address(ip);
nic.setNetwork(network);
```

### 5.2 implementNetwork()

调用 NetworkGuru：

```text
BridgeGuru
PodBasedNetworkGuru
OvsGuestNetworkGuru
```

Guru 决定：

- 网络类型（Isolated/Shared）  
- VLAN 分配  
- Broadcast Domain 结构  

# 6. Storage/Volume Orchestrator：卷准备流程

CloudStack 启动 VM 前会确保：

- Root Volume 已创建  
- Template 已从 Secondary Storage 拷贝到 Primary Storage  
- Data Volume 已准备好

位于：

```text
engine/storage/VolumeManagerImpl.java
```

关键流程：

```java
createVolumeFromTemplate()
chooseStoragePool()
copyTemplateToPool()
```

示例源码：

```java
StoragePool pool = _storagePoolAllocator.allocateToPool(template, vm);
VolumeVO vol = new VolumeVO(...);
vol.setPoolId(pool.getId());
_volumeDao.persist(vol);
```

# 7. Guru 层：Hypervisor 特定逻辑

位于：

```text
com.cloud.vm.VirtualMachineGuru
```

不同 Hypervisor 的实现：

- KVMGuru  
- XenServerGuru  
- VMwareGuru  

Guru 决定：

- generate VM Name  
- attach Volume  
- attach NIC  
- finalizeDeployment()

示例：

```java
@Override
public void finalizeVirtualMachineProfile(VirtualMachineProfile profile, DeployDestination dest) {
    profile.setBootLoader(BootloaderType.CD);
}
```

# 8. StartCommand：VM 最终启动

真正启动 VM 在 Hypervisor Host 上通过 Agent 实现：

调用链：

```text
VirtualMachineManagerImpl.startVirtualMachine()
 → Commands cmds = new Commands(new StartCommand(...))
 → agentMgr.send(hostId, cmds)
```

StartCommand 示例：

```java
public class StartCommand extends Command {
    private String vmName;
    private List<DiskTO> disks;
    private NicTO[] nics;
}
```

Agent 收到 StartCommand 后会：

- 创建 libvirt XML（KVM）  
- 或调用 XenAPI / VMware API  
- 启动 VM  

# 9. 状态机：VM 生命周期的核心

VM 有以下状态：

```text
Created → Starting → Running → Stopping → Stopped → Destroyed → Expunging
```

状态机位于：

```text
engine/schema/src/com/cloud/vm/VirtualMachineState.java
```

状态转移通过：

```java
_stateMachine.transitTo(vm, Event.StartRequested, State.Starting)
```

并持久化到数据库：

```java
UPDATE vm_instance SET state='Starting' WHERE id=? AND state='Created'
```

# 10. VM 启动完整时序图（源码级 ASCII）

```text
User Request
  |
  v
DeployVMCmd.execute()
  |
  v
UserVmManagerImpl.deployVirtualMachine()
  |
  v
VirtualMachineManagerImpl.orchestrateDeployVM()
  |
  +--> DeploymentPlanningManager.plan()
  |        |
  |        +--> FirstFitPlanner.chooseHost()
  |
  +--> NetworkOrchestrator.prepare()
  |
  +--> VolumeManager.prepare()
  |
  +--> Guru.finalizeDeployment()
  |
  +--> agentMgr.send(StartCommand)
  |
  v
VM Running
```

# 11. 常见部署失败点（源码级分析）

## 11.1 失败点：Host 不可用

DeploymentPlanningManager 抛：

```text
InsufficientServerCapacityException
```

## 11.2 网络失败（Guru）

NetworkOrchestrator:

```text
Unable to implements network
```

通常与 VLAN 或 VR 启动失败相关。

## 11.3 StartCommand 失败

Agent 返回：

```text
Answer == null or !Answer.getResult()
```

日志位置：

```text
/var/log/cloudstack/agent/agent.log
```

# 12. 小结

CloudStack Orchestration Engine 通过：

- **Planner（调度）**
- **Orchestrators（编排）**
- **Guru（Hypervisor 逻辑）**
- **StateMachine（生命周期）**
- **Agent（底层执行）**

组成了高度模块化、可替换、可扩展的架构。
