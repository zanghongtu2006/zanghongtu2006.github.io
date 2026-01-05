---
layout: post
lang: en
translations:
  en: /zh/cloudstack-code-reading-10/
slug: "cloudstack-code-reading-10"
title: "CloudStack Code Reading 10 —— Scheduler and Resource（Host / Storage / Network Allocator）"
date: "2015-03-24 12:33:54"
categories: ["CloudStack"]
tags: ["scheduler", "allocator", "deploy", "host", "storage", "source-analysis"]
draft: false
---
调度（Scheduler / Allocator）是 CloudStack 的“大脑之一”，负责决定：
- VM 应该运行在哪台 Host 上  
- Volume 应该存储在哪个 StoragePool  
- 网络资源是否可用  
- 如何回避不健康节点、资源不足节点  
- 如何配合 Orchestration Engine 执行复杂部署

# 1. 调度体系架构总览（源码定位）

CloudStack 调度器被拆成三层：

```text
1. DeploymentPlanningManager（负责 orchestrateDeployVM 的整体调度入口）
2. Host Allocator（挑选 Host）
3. StoragePool Allocator（挑选存储池）
```

源码路径：

```text
engine/orchestration/src/com/cloud/deploy/
    ├── DeploymentPlanningManagerImpl.java
    ├── FirstFitPlanner.java
    ├── ClusterBasedPlanner.java

server/src/com/cloud/agent/manager/allocator/
    ├── HostAllocator.java
    ├── FirstFitAllocator.java

engine/storage/src/com/cloud/storage/allocator/
    ├── StoragePoolAllocator.java
    ├── FirstFitStoragePoolAllocator.java
```

# 2. DeploymentPlanningManager：调度入口

## 2.1 调用链

VM 调度链路：

```text
orchestrateDeployVM()
 → DeploymentPlanningManager.plan()
    → Planner.design()
    → HostAllocator.getHostsToUse()
    → StoragePoolAllocator.select()
```

关键方法：

```java
@Override
public DeployDestination plan(VirtualMachineProfile vmProfile, DeploymentPlan plan, ExcludeList avoid) {
    DataCenter dc = _dcDao.findById(plan.getDataCenterId());
    List<Planner> planners = getPlanners(offering, vmProfile);

    for (Planner planner : planners) {
        DeployDestination dest = planner.plan(vmProfile, plan, avoid);
        if (dest != null) return dest;
    }
    throw new InsufficientServerCapacityException(...);
}
```

# 3. Planner（第一层调度）

Planner 决定使用何种算法挑选资源。

CloudStack 默认 Planner：

- **FirstFitPlanner**（最常用）
- ClusterBasedPlanner
- ImplicitPlanner

## 3.1 FirstFitPlanner 关键逻辑

位置：

```text
engine/orchestration/com/cloud/deploy/FirstFitPlanner.java
```

源码：

```java
public DeployDestination plan(...) {
    List<Cluster> clusters = listAllClusters();
    for (Cluster c : clusters) {
        Host host = findHost(c, vmProfile);
        StoragePool pool = findPool(c, vmProfile);
        if (host != null && pool != null) {
            return new DeployDestination(dc, pod, c, host, pool);
        }
    }
    return null;
}
```

FirstFit = 先找到第一个满足 CPU/MEM/Storage 条件的 Cluster。

Planner 决定整体方向，而真正提供候选资源的，是下面的 Allocator。

# 4. HostAllocator（主机选择 · 源码级解析）

位置：

```text
server/src/com/cloud/agent/manager/allocator/HostAllocator.java
```

主要实现：

- **FirstFitAllocator**
- UserConcentratedPodAllocator（按用户集中度选 host）
- RandomAllocator（随机）

核心接口：

```java
List<Host> allocateTo(VirtualMachineProfile vm, DeployDestination dest, ExcludeList avoid);
```

## 4.1 FirstFitAllocator 实现

关键方法（缩写）：

```java
hosts = _hostDao.listAllUpAndEnabledByCluster(clusterId);

for (Host host : hosts) {
    if (checkHostCapacity(host, vmProfile) &&
        !avoid.shouldAvoid(host)) {
        return Arrays.asList(host);
    }
}
return null;
```

### 检查 CPU 和内存：

```java
host.getTotalMemory() - host.getUsedMemory() > vmMemRequired
host.getCpus() * host.getCpuSpeed() > vmCpuRequired
```

另外还会检查：

- host 是否维护模式  
- host 是否兼容 hypervisor  
- 网络是否能从该 host 路由  

# 5. StoragePoolAllocator（存储池选择 · 源码级解析）

存储调度同样插件化：

```text
StoragePoolAllocator
  ├── FirstFitStoragePoolAllocator
  ├── LocalStoragePoolAllocator
  └── ClusterScopeStorageAllocator
```

关键接口：

```java
List<StoragePool> select(VirtualMachineProfile vm, Long dataCenterId, Long podId, Long clusterId);
```

## 5.1 FirstFitStoragePoolAllocator

源码逻辑：

```java
for (StoragePoolVO pool : availablePools) {
    if (pool.getStatus() == Status.Up &&
        pool.getAvailableSpace() > volumeSize &&
        checkTags(pool, vm)) {
        return Arrays.asList(pool);
    }
}
```

调度因素：

- 池容量  
- 池可达性（网络拓扑）  
- 存储标签（Storage Tags）  
- 模板是否存在于 pool 中  

# 6. Network Allocator（网络可达性验证）

调度还需验证网络是否能在目标 Host 运行。

调用链：

```text
DeploymentPlanningManager.plan()
 → _networkModel.isVmNetworksPresentOnHost(vm, host)
```

网络匹配逻辑：

```java
List<NicProfile> nics = vm.getNics();
for (NicProfile nic : nics) {
    if (!networkAvailableOnHost(nic.getNetwork(), host)) return false;
}
return true;
```

网络可达性包括：

- BroadcastDomain 类型匹配  
- VLAN 在目标 host 是否 trunk  
- VR 是否存在且能为该 host 服务  

# 7. 限制与回避（ExcludeList）

ExcludeList 是调度中非常关键但常被忽视的结构。

它用于记录**不应使用的资源**：

```text
hostsToAvoid
poolsToAvoid
clustersToAvoid
podsToAvoid
```

调度失败时：

```java
avoid.addHost(hostId);
avoid.addPool(poolId);
```

调度重试会根据 ExcludeList 避开问题资源。

# 8. 调度完整时序图（ASCII）

```text
orchestrateDeployVM
 |
 v
DeploymentPlanningManager.plan()
 |
 +--> FirstFitPlanner.plan()
 |       |
 |       +--> HostAllocator.allocateTo()
 |       |       |
 |       |       +--> check CPU/MEM/capacity
 |       |       +--> avoid list
 |       |
 |       +--> StoragePoolAllocator.select()
 |               |
 |               +--> check space/tags/pool status
 |
 +--> Build DeployDestination(dc,pod,cluster,host,pool)
```

# 9. 调度失败点 · 源码级分析

## 9.1 Host 无可用资源

```text
InsufficientServerCapacityException
```

原因：
- CPU/MEM 不足
- host 处于维护模式
- AvoidList 避开了所有 host

## 9.2 StoragePool 满

```text
No suitable storage pool
```

检查：

```text
storage_pool.used_bytes
storage_pool.capacity_bytes
```

## 9.3 网络不可达

```
Network is not available on host
```

检查 VLAN trunk、VR 状态。

# 10. Host / Storage Capacity 表结构（DB 层）

## 10.1 op_host_capacity

存储 host 的容量信息：

```text
host_id
capacity_type
total_capacity
used_capacity
```

VM 启动后更新容量：

```text
UPDATE op_host_capacity SET used += vm_mem
```

## 10.2 storage_pool 表

```text
id
available_bytes
capacity_bytes
status
scope
```

# 11. 调度关键类小结

| 层级 | 类 | 作用 |
|------|------|------|
| 调度入口 | DeploymentPlanningManager | 调用 Planner |
| Planner | FirstFitPlanner | 整体调度策略 |
| HostAllocator | FirstFitAllocator | 主机选择 |
| StorageAllocator | FirstFitStoragePoolAllocator | 存储池选择 |
| 网络验证 | NetworkModelImpl | VLAN/trunk/VR 检查 |
| 回避列表 | ExcludeList | 动态避免 bad host/pool |

# 12. 总结

CloudStack 的调度体系不是单层算法，而是多层协同结构：

- **Planner → Allocators → NetworkModel → ExcludeList**  
- CPU/MEM/Storage/Network 联合决策  
- 插件化的 HostAllocator / StoragePoolAllocator  
- ExcludeList 提供“动态学习”能力  

理解这个流程，就能完全掌握 CloudStack 部署失败、资源不足、调度异常的根本原因。
