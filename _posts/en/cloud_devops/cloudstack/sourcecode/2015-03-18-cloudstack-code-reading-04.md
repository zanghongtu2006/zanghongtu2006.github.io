---
layout: post
lang: en
translations:
  en: /en/cloudstack-code-reading-04/
  zh: /zh/cloudstack-code-reading-04/
permalink: /en/cloudstack-code-reading-04/
slug: "cloudstack-code-reading-04"
title: "CloudStack Code（4）—— Database Schema"
date: "2015-03-18 13:33:09"
categories: ["CloudStack"]
tags: ["schema", "database", "storage", "network", "vm"]
draft: false
---

This article provides an in-depth analysis of CloudStack's database schema.

# 1. CloudStack Database Architecture Overview
Data Layering:

```text
Core Data
  → VM、Volume、Network、Host、Cluster
Async/Orchestration Data
  → async_job、event、op_host_capacity
Usage/Analytics
  → usage_event、cloud_usage
```

The database is the **core of the state machine** in CloudStack, and all Manager layers and Orchestration Engines need to synchronize it.

# 2. VM Related Table Structure

Key Tables:

| Table | Function |
|----|------|
| vm_instance | VM Entity |
| user_vm | Additional Attributes of User VMs |
| nics | VM Network Interface Card |
| vm_network_map | Mapping between VMs and networks |

## 2.1 vm_instance Field Parsing

Key Fields:

- state (Running/Stopped/Expunging/Destroyed)
- host_id (On which physical host)
- last_host_id (Last host, used for HA)
- hypervisor_type
- uuid 
- account_id

State management relies entirely on the state field.

# 3. Network-related structure
Core tables:

- networks
- network_offerings
- network_acl
- nics
- ip_address
- user_ip_address

## 3.1 The `networks` table contains the following fields:

Network type:
- Guest
- Public
- Storage
- Control

Also includes：

- broadcast_domain
- traffic_type
- guru_name（corresponding to NetworkGuru）
- element status

# 4. Storage Schema

Related Tables:
- volumes
- snapshots
- storage_pool
- template_store_ref
- volume_store_ref
- disk_offering

## 4.1 volumes fields

- state（Allocated/Ready/Migrating）
- pool_id
- format（RAW/QCOW2/VHD）
- chain_info（snapshot chain）

## 4.2 snapshot table contains the following fields

A snapshot is a point-in-time version of a volume.

# 5. async_job
fields：

- job_id
- job_status
- job_result
- job_instance_type
- job_result_code

job_status：

| Status | Meaning |
|------|------|
| 0 | Processing |
| 1 | Success |
| 2 | Failure |

# 6. Capacity and Scheduling

Related Tables:

- op_host_capacity
- cluster_details
- storage_pool_details

Used by the scheduler for resource evaluation.

# 7. State Machine

Many table fields contain "state":

- VM
- Network
- Volume
- Snapshot

State transitions are caused by:
```text
event → new state
```
persistence in database.

# 8. Summary

Schema is the foundation of CloudStack.

Understanding it helps in:

- Troubleshooting resource anomalies
- Writing new APIs
- Debugging the Orchestration Engine
- Understanding Host/VM migration behavior
