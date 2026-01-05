---
layout: post
lang: zh
translations:
  en: /en/cloudstack-code-reading-03/
  zh: /zh/cloudstack-code-reading-03/
permalink: /zh/cloudstack-code-reading-03/
slug: "cloudstack-code-reading-03"
title: "CloudStack 代码阅读（三）—— 整体架构概览"
date: "2015-03-17 22:32:39"
categories: ["CloudStack"]
tags: ["architecture", "orchestration", "overview"]
draft: false
---

本篇从系统级别介绍 CloudStack 的宏观架构，帮助你在进入后续模块（网络、存储、Hypervisor、Orchestration）前有一个整体地图。

# 1. CloudStack 的整体形态  
CloudStack 是典型的 IaaS（Infrastructure as a Service）平台，其设计思想是：  
**以 API 为中心，构建 VM / 网络 / 存储 资源的可编排系统。**

总体层次划分如下：

```text
API 层（cloud-api）
Service 层（Management Server）
Orchestration Engine（资源编排）
Agent 层（Hypervisor）
Data Store 层（Primary/Secondary Storage）
```

# 2. Management Server（管理服务器）  
CloudStack 的控制平面由一组 Management Server 组成，可水平扩展。

核心模块：

| 模块 | 作用 |
|------|------|
| server/ | VM、Network、Volume 管理实现 |
| engine/ | Orchestration Engine，执行编排流 |
| plugins/ | 各类插件，如 VMware/Xen/KVM/S3/Nicira 等 |
| framework/ | 公共基础设施，比如 config、schema、事件系统 |

## 2.1 调度器（Allocator/Scheduler）

选择资源：

- Host 分配
- Storage Pool 分配
- 网络分配（NetworkGuru）

## 2.2 Manager 层

例如：

- `UserVmManagerImpl`
- `NetworkManagerImpl`
- `VolumeManagerImpl`

这些是业务逻辑核心。

# 3. Orchestration Engine（资源编排引擎）  
位于：

```text
engine/orchestration
```

作用：

- 控制虚拟机生命周期
- 控制网络资源准备流程
- 控制卷挂载/卸载
- 调用调度器
- 调用 agent 发送指令
- 更新状态机

VM 启动是一个典型工作流：

```text
DeployVMWorkFlow
  → allocate resources
  → prepare network
  → prepare storage
  → start on hypervisor
```

# 4. Agent 层（Hypervisor Host）  
每台物理主机上运行一个 Java Agent：

```text
agent/src/com/cloud/agent/
```

它的职责：

- 监听 Management Server 的 Command  
- 执行超管操作（start/stop/migrate）  
- 回报心跳（Ping Command）  
- 回报 host stats  
- 管理本机网络、存储、VM 进程  

通信协议使用 NIO + 自定义 JSON 指令格式。

这是 CloudStack 与 Hypervisor 交互的核心。

# 5. 存储体系  
CloudStack 的存储分为：

| 类型 | 说明 |
|------|------|
| Primary Storage | VM 运行盘（root + data volume） |
| Secondary Storage | ISO / Template / Snapshot |

存储子系统组件：

- Storage Pool（NFS / iSCSI / Ceph / local）
- Volume Manager
- TemplateManager
- SnapshotManager
- StorageMotion（池间迁移）

存储逻辑在：

```text
engine/storage
plugins/storage
server/storage
```

# 6. Network 体系（网络编排）  
CloudStack 网络体系非常复杂，包含多层：

- Public Network
- Guest Network
- Storage Network
- Private/Control Network

网络工作者：

- NetworkOffering  
- NetworkGuru（决定网络类型）  
- NetworkElement（VR，LB，DHCP，ACL）  
- VirtualRouter（控制面设备）  
- SDN 插件（Nicira, Midonet 等）

# 7. 插件体系（Plugins Architecture）  
CloudStack 的插件机制非常强大，支持：

- Hypervisor 插件
- Storage 插件
- Network 插件
- Authentication 插件
- EventBus 插件
- Usage 插件

插件可以无缝地注册进 Orchestration Engine。

# 8. 状态机（StateMachine）  
CloudStack 所有资源都采用状态机驱动，例如：

- VM: Stopped → Starting → Running → Stopping
- Volume: Ready → Allocated → Creating → Ready
- Network: Allocated → Implemented → Shutdown

状态机定义在：

```text
engine/schema
engine/orchestration
```

状态变化经过：

```text
event → new state
```

持久化在 DB。

# 9. 小结  
CloudStack 的架构设计目标：

- 模块化  
- 插件化  
- 高可扩展  
- 强隔离性（Account/Domain）  
- 强资源编排能力（Orchestration Engine）  
