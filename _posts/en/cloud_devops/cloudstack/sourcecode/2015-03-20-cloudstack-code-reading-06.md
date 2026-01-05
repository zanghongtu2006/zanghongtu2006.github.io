---
layout: post
lang: en
translations:
  en: /en/cloudstack-code-reading-06/
  zh: /zh/cloudstack-code-reading-06/
permalink: /en/cloudstack-code-reading-06/
slug: "cloudstack-code-reading-06"
title: "CloudStack Code（6）—— Orchestration Engine"
date: "2015-03-20 23:00:03"
categories: ["CloudStack"]
tags: ["orchestration", "workflow", "vm", "source-analysis"]
draft: false
---
CloudStack's Orchestration Engine is the core module of the entire IaaS system.

Any VM lifecycle operation, such as `deployVirtualMachine`, `startVM`, `rebootVM`, and `migrateVM`, ultimately follows this **Workflow + StateMachine + Manager call chain**.

This article explains the entire VM deployment process based on the actual directory structure, class names, and call stack in CloudStack 4.2.2.

# 1. Main modules of Orchestration Engine

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

Module Layering:

- **VM Orchestrator**: Controls the overall VM lifecycle.
- **Deploy Planner**: Responsible for selecting the physical host.
- **Network Orchestrator**: Prepares the VM network, NIC, and VR.
- **Volume/Storage Orchestrator**: Prepares the Root/Data volume, templates, and storage pool.
- **Guru (Virtual Machine Expert)**: Guru determines the implementation differences for each Hypervisor.
- **Workflow Engine**: Executes steps sequentially.

# 2. From API to Orchestration: Complete Call Chain

User Invocation:

```text
deployVirtualMachine
```

corresponding Class:

```java
org.apache.cloudstack.api.command.user.vm.DeployVMCmd
```

`execute()` method call:

```java
UserVm result = _userVmService.deployVirtualMachine(this);
```

We follow code into `_userVmService`:

```java
UserVmManagerImpl.deployVirtualMachine()
```

Then we enter the Orchestration Engine:

```java
VirtualMachineManagerImpl.orchestrateDeployVM()
```

The complete call stack is as follows:

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

# 3. DeploymentPlanningManager:Host Selection Core

Located at:
```text
engine/orchestration/src/com/cloud/deploy/DeploymentPlanningManagerImpl.java
```
Core Methods:

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

Key logical steps:

1. Obtain the list of zone/pod/cluster
2. Traverse the cluster and check if it meets the VM specifications
3. Select a Host within the cluster
4. Select a suitable storage pool within the cluster
5. Assemble the `DeployDestination`

# 4. FirstFitPlanner: The default scheduler for CloudStack

位于:

```text
engine/orchestration/src/com/cloud/deploy/FirstFitPlanner.java
```

Key Strategies:

- Ensure sufficient CPU/Memory requirements
- Consider StoragePool capacity as well
- Prioritize low-load clusters
- Filter out hosts/pools from the avoid list

Example:

```java
List<Host> hosts = _hostDao.listAllUpAndEnabledByCluster(clusterId);
for (Host host : hosts) {
    if (host.getCpu() > vmCpu && host.getRam() > vmMem) {
        return host;
    }
}
```

# 5. NetworkOrchestrator: Preparing the network environment

Located at:

```text
engine/orchestration/src/com/cloud/network/NetworkOrchestrator.java
```

Network preparation process for deploying VMs:
```text
prepare(vm, destination)
 → allocateNIC()
 → implementNetwork()
 → configureVirtualRouter()
```

### 5.1 NIC Allocation

```java
NicProfile nic = new NicProfile();
nic.setIPv4Address(ip);
nic.setNetwork(network);
```

### 5.2 implementNetwork()

Call NetworkGuru:

```text
BridgeGuru
PodBasedNetworkGuru
OvsGuestNetworkGuru
```

Guru decide:

- Network Type（Isolated/Shared）  
- VLAN Allocation  
- Broadcast Domain structrure  

# 6. Storage/Volume Orchestrator:Volume preparation process

Before launching a VM, CloudStack ensures the following:

- The Root Volume has been created
- The Template has been copied from Secondary Storage to Primary Storage
- The Data Volume is ready

Located at:

```text
engine/storage/VolumeManagerImpl.java
```

Key processes:

```java
createVolumeFromTemplate()
chooseStoragePool()
copyTemplateToPool()
```

Example:

```java
StoragePool pool = _storagePoolAllocator.allocateToPool(template, vm);
VolumeVO vol = new VolumeVO(...);
vol.setPoolId(pool.getId());
_volumeDao.persist(vol);
```

# 7. Guru: Hypervisor Specific Logic

Located at:
```text
com.cloud.vm.VirtualMachineGuru
```

Different Hypervisor implementations:

- KVMGuru  
- XenServerGuru  
- VMwareGuru  

Guru decide:

- generate VM Name  
- attach Volume  
- attach NIC  
- finalizeDeployment()

Example:

```java
@Override
public void finalizeVirtualMachineProfile(VirtualMachineProfile profile, DeployDestination dest) {
    profile.setBootLoader(BootloaderType.CD);
}
```

# 8. StartCommand: Final VM startup

The actual VM startup is achieved on the Hypervisor Host via an Agent:

Call chain:

```text
VirtualMachineManagerImpl.startVirtualMachine()
 → Commands cmds = new Commands(new StartCommand(...))
 → agentMgr.send(hostId, cmds)
```

StartCommand Example:

```java
public class StartCommand extends Command {
    private String vmName;
    private List<DiskTO> disks;
    private NicTO[] nics;
}
```

Upon receiving the StartCommand, the Agent will:

- Create libvirt XML (KVM)
- Or call the XenAPI / VMware API
- Start the VM

# 9. State Machine: The Core of the VM Lifecycle

VM has the following states:

```text
Created → Starting → Running → Stopping → Stopped → Destroyed → Expunging
```

Status Machine Located at:

```text
engine/schema/src/com/cloud/vm/VirtualMachineState.java
```

State transition through:

```java
_stateMachine.transitTo(vm, Event.StartRequested, State.Starting)
```

And persist to the database:

```java
UPDATE vm_instance SET state='Starting' WHERE id=? AND state='Created'
```

# 10. Complete VM startup timing diagram

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

# 11. Common Deployment Failure

## 11.1 Failure: Host Unavailable

DeploymentPlanningManager throws:

```text
InsufficientServerCapacityException
```

## 11.2 Network failure（Guru）

NetworkOrchestrator:

```text
Unable to implements network
```

This is usually related to VLAN or VR startup failure.

## 11.3 StartCommand Failure

Agent returns:

```text
Answer == null or !Answer.getResult()
```

Log Location:

```text
/var/log/cloudstack/agent/agent.log
```

# 12. Summary

The CloudStack Orchestration Engine utilizes:

**Planner (Scheduling)**
**Orchestrators (Orchestration)**
**Guru (Hypervisor Logic)**
**StateMachine (Lifecycle)**
**Agent (Underlying Execution)**

to form a highly modular, replaceable, and scalable architecture.
