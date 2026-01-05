---
layout: post
lang: en
translations:
  en: /en/cloudstack-code-reading-03/
  zh: /zh/cloudstack-code-reading-03/
permalink: /en/cloudstack-code-reading-03/
slug: "cloudstack-code-reading-03"
title: "CloudStack Code（3）- Overall Architecture Overview"
date: "2015-03-17 22:32:39"
categories: ["CloudStack"]
tags: ["architecture", "orchestration", "overview"]
draft: false
---

This article introduces the macro architecture of CloudStack from a system-level perspective, including (network, storage, hypervisor, and orchestration).

# 1. CloudStack's Overall Structure

CloudStack is a typical IaaS (Infrastructure as a Service) platform. Its design philosophy is:

**A system centered around APIs, building an orchestratable system of VM/network/storage resources.**

The overall layering is as follows:
```text
API （cloud-api）
Service （Management Server）
Orchestration Engine（Resource orchestration）
Agent （Hypervisor）
Data Store （Primary/Secondary Storage）
```

# 2. Management Server  
CloudStack's control plane consists of a set of Management Servers and is horizontally scalable.

Core Modules:

| Module | Function |
|------|------|
| server/ | VM, Network, Volume management implementation |
| engine/ | Orchestration Engine, executes orchestration flow |
| plugins/ | Various plugins, such as VMware/Xen/KVM/S3/Nicira, etc. |
| framework/ | Common infrastructure, such as config, schema, event system |

## 2.1 Allocator/Scheduler

Select Resources:
- Host Allocation
- Storage Pool Allocation
- Network Allocation (NetworkGuru)
## 2.2 Manager

Example：
- `UserVmManagerImpl`
- `NetworkManagerImpl`
- `VolumeManagerImpl`
These are the core of the cloud platform business logic.
- 
# 3. Orchestration Engine  
Located：
```text
engine/orchestration
```
Its responsibilities include:

- Control the virtual machine lifecycle
- Control the network resource preparation process
- Control volume mounting/unmounting
- Invoke the scheduler
- Invoke the agent to send commands
- Update the state machine
VM startup is a typical workflow:

```text
DeployVMWorkFlow
  → allocate resources
  → prepare network
  → prepare storage
  → start on hypervisor
```

# 4. Agent（Hypervisor Host）  
One Java Agent runs on each physical host:
```text
agent/src/com/cloud/agent/
```

Its responsibilities include:

- Listening for commands from the Management Server
- Executing hypervisor operations (start/stop/migrate)
- Reporting heartbeats (Ping Commands)
- Reporting host stats
- Managing the local network, storage, and VM processes

The communication protocol uses NIO + a custom JSON command format.

This is the core of CloudStack's interaction with the Hypervisor.

# 5. Storage Architecture

CloudStack storage is divided into:

| Type | Description |
|------|------|
| Primary Storage | VM runtime disk (root + data volume) |
| Secondary Storage | ISO / Template / Snapshot |

Storage Subsystem Components:

- Storage Pool（NFS / iSCSI / Ceph / local）
- Volume Manager
- TemplateManager
- SnapshotManager
- StorageMotion（migration cross storage pools）

Storage logic located：
```text
engine/storage
plugins/storage
server/storage
```

# 6. Network Orchestration  
The CloudStack network architecture is highly complex, comprising multiple layers:

- Public Network
- Guest Network
- Storage Network
- Private/Control Network

Network workers:

- NetworkOffering
- NetworkGuru (determines network type)
- NetworkElement (VR, LB, DHCP, ACL)
- VirtualRouter (control plane device)
- SDN plugins (Nicira, Midonet, etc.)

# 7. Plugins Architecture
CloudStack's plugin mechanism is very powerful, supporting:

- Hypervisor plugin
- Storage plugin
- Network plugin
- Authentication plugin
- EventBus plugin
- Usage plugin

Plugins can be seamlessly registered with the Orchestration Engine.

# 8. StateMachine
All CloudStack resources are state machine driven, for example:

- VM: Stopped → Starting → Running → Stopping
- Volume: Ready → Allocated → Creating → Ready
- Network: Allocated → Implemented → Shutdown

The state machine is defined in:
```text
engine/schema
engine/orchestration
```
State change process：

```text
event → new state
```
Persistence is performed on the database (DB).

# 9. Summary

CloudStack's architectural design goals:

- Modularization
- Pluggable architecture
- High scalability
- Strong isolation (Account/Domain)
- Strong resource orchestration capabilities (Orchestration Engine)