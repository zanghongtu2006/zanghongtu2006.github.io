---
layout: post
lang: en
translations:
  en: /en/cloudstack-code-reading-10/
  zh: /zh/cloudstack-code-reading-10/
permalink: /en/cloudstack-code-reading-10/
slug: "cloudstack-code-reading-10"
title: "CloudStack Code（10）—— Scheduler and Resource Allocation（Host / Storage / Network Allocator）"
date: "2015-03-24 12:33:54"
categories: ["CloudStack"]
tags: ["scheduler", "allocator", "deploy", "host", "storage", "source-analysis"]
draft: false
---
The scheduler (or allocator) is a core component of CloudStack, responsible for determining:

- Which host a VM should run on
- Which StoragePool a volume should be stored in
- Network resource availability
- How to avoid unhealthy or resource-insufficient nodes
- How to work with the Orchestration Engine to perform complex deployments

# 1. Scheduling System Architecture Overview (Source Code Location)

The CloudStack scheduler is divided into three layers:

``` text
1. DeploymentPlanningManager (responsible for the overall scheduling entry point of orchestrateDeployVM)
2. Host Allocator (selects hosts)
3. StoragePool Allocator (selects storage pools)

```
Source Code Path:

```
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

# 2. DeploymentPlanningManager:Dispatch Entry

## 2.1 Dispatch chain

VM Dispatch Chain:

```
orchestrateDeployVM()
 → DeploymentPlanningManager.plan()
    → Planner.design()
    → HostAllocator.getHostsToUse()
    → StoragePoolAllocator.select()
```

Key methods:

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

# 3. Planner（Level 1 Scheduling）

The Planner determines which algorithm to use to select resources.

CloudStack Default Planner:

- **FirstFitPlanner**（Most commonly used）
- ClusterBasedPlanner
- ImplicitPlanner

## 3.1 FirstFitPlanner Key Logic

Located at:
```
engine/orchestration/com/cloud/deploy/FirstFitPlanner.java
```

Souce code:

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

FirstFit = Find the first cluster that meets the CPU/MEM/Storage criteria.

The Planner determines the overall direction, but the Allocator below is responsible for providing the actual candidate resources.

# 4. HostAllocator

Located at:

```
server/src/com/cloud/agent/manager/allocator/HostAllocator.java
```

Main implementations:

- **FirstFitAllocator**
- UserConcentratedPodAllocator (selects hosts based on user concentration)
- RandomAllocator (random selection)

Key interfaces:
```java
List<Host> allocateTo(VirtualMachineProfile vm, DeployDestination dest, ExcludeList avoid);
```

## 4.1 FirstFitAllocator implementation

Key function:

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

### Check CPU and MEM:

```java
host.getTotalMemory() - host.getUsedMemory() > vmMemRequired
host.getCpus() * host.getCpuSpeed() > vmCpuRequired
```

Additionally, the following will be checked:

- Whether the host is in maintenance mode
- Whether the host is compatible with the hypervisor
- Whether the network can be routed from this host

# 5. StoragePoolAllocator

Storage scheduling is also modular:

```
StoragePoolAllocator
  ├── FirstFitStoragePoolAllocator
  ├── LocalStoragePoolAllocator
  └── ClusterScopeStorageAllocator
```

Key interface:

```java
List<StoragePool> select(VirtualMachineProfile vm, Long dataCenterId, Long podId, Long clusterId);
```

## 5.1 FirstFitStoragePoolAllocator

Souce code:

```java
for (StoragePoolVO pool : availablePools) {
    if (pool.getStatus() == Status.Up &&
        pool.getAvailableSpace() > volumeSize &&
        checkTags(pool, vm)) {
        return Arrays.asList(pool);
    }
}
```

Scheduling factors:

- Pool capacity
- Pool reachability (network topology)
- Storage tags
- Template existence in the pool

# 6. Network Allocator

Scheduling also requires verifying whether the network can operate on the target host.

Schedule chain:

```
DeploymentPlanningManager.plan()
 → _networkModel.isVmNetworksPresentOnHost(vm, host)
```

Network matching logic:

```java
List<NicProfile> nics = vm.getNics();
for (NicProfile nic : nics) {
    if (!networkAvailableOnHost(nic.getNetwork(), host)) return false;
}
return true;
```

Network reachability includes:

- BroadcastDomain type matching
- Whether the VLAN is trunked on the target host
- Whether the VR exists and can serve this host

# 7. ExcludeList

ExcludeList is a crucial but often overlooked structure in scheduling.

It is used to record **resources that should not be used**.
```
hostsToAvoid
poolsToAvoid
clustersToAvoid
podsToAvoid
```

When scheduling fails:

```java
avoid.addHost(hostId);
avoid.addPool(poolId);
```

Retry scheduling will avoid problematic resources based on the ExcludeList.
# 8. Complete scheduling sequence diagram

```
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

# 9. Scheduling failure

## 9.1 Host has no available resources

```
InsufficientServerCapacityException
```

Reasons:

- Insufficient CPU/MEM
- Host is in maintenance mode
- AvoidList avoids all hosts

## 9.2 StoragePool FULL

```
No suitable storage pool
```

Check:

```
storage_pool.used_bytes
storage_pool.capacity_bytes
```

## 9.3 Network unreachable

```
Network is not available on host
```

Check VLAN trunk and VR status.

# 10. Host / Storage Capacity Table Structure

## 10.1 op_host_capacity

Storage host capacity information:

```
host_id
capacity_type
total_capacity
used_capacity
```

Update capacity after VM starts:

```
UPDATE op_host_capacity SET used += vm_mem
```

## 10.2 storage_pool

```
id
available_bytes
capacity_bytes
status
scope
```

# 11. Summary of Key Scheduling Classes

| Hierarchy | Class | Function |
|------|------|------|
| Scheduling Entry Point | DeploymentPlanningManager | Calls Planner |
| Planner | FirstFitPlanner | Overall Scheduling Strategy |
| HostAllocator | FirstFitAllocator | Host Selection |
| StorageAllocator | FirstFitStoragePoolAllocator | Storage Pool Selection |
| Network Authentication | NetworkModelImpl | VLAN/trunk/VR Check |
| ExcludeList | ExcludeList | Dynamically Avoids Bad Hosts/Pools |

# 12. Summary

CloudStack's scheduling system is not a single-layer algorithm, but a multi-layer collaborative structure:

- **Planner → Allocators → NetworkModel → ExcludeList**
- Joint decision-making across CPU/MEM/Storage/Network
- Pluggable HostAllocator / StoragePoolAllocator
- ExcludeList provides "dynamic learning" capabilities
