---
layout: post
lang: en
translations:
  en: /en/cloudstack-code-reading-05/
  zh: /zh/cloudstack-code-reading-05/
permalink: /en/cloudstack-code-reading-05/
slug: "cloudstack-code-reading-05"
title: "CloudStack Code（5）—— Resource Model and Entity Object（VO/DAO）"
date: "2015-03-19 15:55:33"
categories: ["CloudStack"]
tags: ["dao", "vo", "resource-model"]
draft: false
---
This article introduces the resource model design of CloudStack: VO (Persistent Object) and DAO (Data Access Object).
# 1. CloudStack Data Layer Structure

The data layer is divided into:

```text
VO (Value Object → DB Row)
DAO (Data Access → SQL Operation)
Manager (Business Logic)
Orchestration Engine
Agent (Execution)
```

VO and DAO patterns are extremely critical in CloudStack.

# 2. VO（Value Object）  
A VO is a direct mapping to a database table. For example:

| VO | Corresponding Table |
|------|---------|
| VirtualMachineVO | vm_instance |
| VolumeVO | volumes |
| NetworkVO | networks |
| HostVO | hosts |

## 2.1 Characteristics of a VO (Value Object):

- Fields correspond one-to-one with the database (DB).
- Includes resource state fields.
- Typically immutable objects.
- Used solely for data storage; does not contain business logic.
# 3. DAO（Data Access Object）  

DAO's responsibilities include:

- CRUD operations
- Primary key/foreign key based queries
- State-based conditional queries
- Optimistic locking operations
- State machine transitions

Example:

```text
VirtualMachineDao
VolumeDao
NetworkDao
IpAddressDao
```

## 3.1 Optimistic Locking
DAO Uses：
```shell
UPDATE vm_instance SET state = ? WHERE id = ? AND state = oldState
```
ensures concurrency safety.

# 4. State Machine Combined with DAO
VM state updates typically use:
```java
_stateMachine.transitTo(vm, newState, event);
```
Internally, it will：  
1. Validate valid migrations
2. Call the DAO to update the database
3. Publish the event (EventBus)

# 5. Resource Object Model  
CloudStack resource model process:

```text
VO (Persistent Data Layer)
  → DAO (SQL Access)
  → Manager (Business Logic)
  → Orchestration (Cross-Module Orchestration)
  → AgentCommand (Physical Execution)
```

For Example Start a VM：

```java
vmDao.findById()
vmDao.update()
networkMgr.prepare()
volumeMgr.prepare()
agentMgr.send(StartCommand)
```
