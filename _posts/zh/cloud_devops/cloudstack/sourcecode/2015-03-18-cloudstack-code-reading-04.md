---
layout: post
lang: zh
translations:
  en: /en/cloudstack-code-reading-04/
  zh: /zh/cloudstack-code-reading-04/
permalink: /zh/cloudstack-code-reading-04/
slug: "cloudstack-code-reading-04"
title: "CloudStack 代码阅读（四）—— 数据库 Schema"
date: "2015-03-18 13:33:09"
categories: ["CloudStack"]
tags: ["schema", "database", "storage", "network", "vm"]
draft: false
---

本篇深入解析 CloudStack 的数据库 Schema。

# 1. CloudStack 数据库体系概述  
数据分层：

```text
Core Data
  → VM、Volume、Network、Host、Cluster
Async/Orchestration Data
  → async_job、event、op_host_capacity
Usage/Analytics
  → usage_event、cloud_usage
```

数据库是 CloudStack 的 **状态机核心**，所有 Manager 层和 Orchestration Engine 都需要同步它。

# 2. VM 相关表结构  
关键表：

| 表 | 作用 |
|----|------|
| vm_instance | VM 实体 |
| user_vm | 用户 VM 的附加属性 |
| nics | VM 网卡 |
| vm_network_map | VM 与 network 的映射 |

## 2.1 vm_instance 字段解析

主要字段：

- state（Running/Stopped/Expunging/Destroyed）
- host_id（在哪个物理主机上）
- last_host_id（上一次的主机，用于 HA）
- hypervisor_type
- uuid
- account_id

状态管理完全依赖 state 字段。

# 3. 网络相关结构（Network）  
核心表：

- networks
- network_offerings
- network_acl
- nics
- ip_address
- user_ip_address

## 3.1 networks 表字段  
包含网络类型：

- Guest
- Public
- Storage
- Control

还包含：

- broadcast_domain
- traffic_type
- guru_name（对应 NetworkGuru）
- element 状态

# 4. 存储 Schema  
相关表：

- volumes
- snapshots
- storage_pool
- template_store_ref
- volume_store_ref
- disk_offering

## 4.1 volumes 字段

- state（Allocated/Ready/Migrating）
- pool_id
- format（RAW/QCOW2/VHD）
- chain_info（快照链）

## 4.2 snapshot 表字段

快照是基于 volume 的点时间版本。

# 5. 异步任务表（async_job）  
字段：

- job_id
- job_status
- job_result
- job_instance_type
- job_result_code

job_status：

| 状态 | 含义 |
|------|------|
| 0 | 处理中 |
| 1 | 成功 |
| 2 | 失败 |

# 6. 容量与调度  
相关表：

- op_host_capacity
- cluster_details
- storage_pool_details

用于调度器做资源评估。

# 7. 状态机（StateMachine）  
大量表字段包含 state：

- VM
- Network
- Volume
- Snapshot

状态转换由：

```text
event → new state
```

持久化在数据库。

# 8. 小结  
Schema 是 CloudStack 的底座。  
理解它有助于：

- 排查资源异常  
- 编写新 API  
- 调试 Orchestration Engine  
- 理解 Host/VM 迁移行为  
