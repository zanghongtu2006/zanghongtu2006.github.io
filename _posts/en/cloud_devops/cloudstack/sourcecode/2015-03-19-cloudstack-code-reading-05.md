---
layout: post
lang: en
translations:
  en: /zh/cloudstack-code-reading-05/
slug: "cloudstack-code-reading-05"
title: "CloudStack Code Reading 05 —— VO/DAO"
date: "2015-03-19 15:55:33"
categories: ["CloudStack"]
tags: ["dao", "vo", "resource-model"]
draft: false
---
本篇介绍 CloudStack 的资源模型设计：VO（持久化对象）与 DAO（数据访问对象）。

# 1. CloudStack 的数据层结构  
数据层分为：

```
VO（值对象 → DB Row）
DAO（数据访问 → SQL 操作）
Manager（业务逻辑）
Orchestration Engine（编排）
Agent（执行）
```

VO 与 DAO 模式在 CloudStack 中极其关键。

# 2. VO（Value Object）  
VO 是数据库表的直接映射对象，例如：

| VO | 对应表 |
|------|---------|
| VirtualMachineVO | vm_instance |
| VolumeVO | volumes |
| NetworkVO | networks |
| HostVO | hosts |

## 2.1 VO 的特点  
- 字段与 DB 一一对应  
- 包含资源状态字段（state）  
- 通常是不可变对象  
- 仅用于存储数据，不包含业务逻辑  

# 3. DAO（Data Access Object）  

DAO 作用：

- CRUD 操作  
- 基于主键 / 外键查询  
- 基于状态的条件查询  
- 乐观锁操作  
- 状态机 transition  

示例：

```
VirtualMachineDao
VolumeDao
NetworkDao
IpAddressDao
```

## 3.1 乐观锁  
DAO 使用：

```
UPDATE vm_instance SET state = ? WHERE id = ? AND state = oldState
```

保证并发安全。

# 4. 状态机结合 DAO  
VM 状态更新通常使用：

```java
_stateMachine.transitTo(vm, newState, event);
```

内部会：

1. 校验合法迁移  
2. 调用 DAO 更新数据库  
3. 发布事件（EventBus）

# 5. Resource Object Model  
CloudStack 的资源模型流程：

```
VO（持久化层数据）
 → DAO（SQL 访问）
 → Manager（业务逻辑）
 → Orchestration（跨模块编排）
 → AgentCommand（物理执行）
```

例如启动 VM：

```
vmDao.findById()
vmDao.update()
networkMgr.prepare()
volumeMgr.prepare()
agentMgr.send(StartCommand)
```

# 6. 小结  
VO/DAO 是 CloudStack 最基础的数据访问与状态管理模型。
