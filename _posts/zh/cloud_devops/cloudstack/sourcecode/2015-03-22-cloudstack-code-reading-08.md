---
layout: post
lang: zh
translations:
  zh: /zh/cloudstack-code-reading-08/
  en: /en/cloudstack-code-reading-08/
permalink: /zh/cloudstack-code-reading-08/
slug: "cloudstack-code-reading-08"
title: "CloudStack 代码阅读（八）—— 存储体系深度解析（Primary/Secondary/Snapshot/StorageMotion）"
date: "2015-03-22 10:55:23"
categories: ["CloudStack"]
tags: ["storage", "primary", "secondary", "snapshot", "storagemotion", "source-analysis"]
draft: false
---
CloudStack 的存储体系比网络模块更隐蔽也更复杂。它涉及模板、卷、快照、跨池迁移（StorageMotion）、Secondary Image Store 结构化管理以及与 Hypervisor 的深度整合。
接下来逐层解析底层方法调用链、数据结构、关键指令以及 Agent 的执行机制。

# 1. 存储模块的层次结构（源码路径）

```
engine/storage/
  ├── volume/VolumeManagerImpl.java
  ├── snapshot/SnapshotManagerImpl.java
  ├── template/TemplateManagerImpl.java
  └── motion/StorageSystemSnapshotStrategy.java

server/src/com/cloud/storage/
  ├── StorageManagerImpl.java
  ├── dao/
  ├── storagepool/
  └── template/

plugins/storage/
  ├── nfs/
  ├── solidfire/
  ├── iscsi/
  └── objectstore/
```

CloudStack 将“存储”拆成逻辑模块，主干负责调度，插件负责与实际后端（NFS/ISCSI/Ceph/SolidFire）交互。

# 2. Primary / Secondary / Image Store：三层模型

CloudStack 的存储体系由三层组成：

## 2.1 Primary Storage（主存储）
- Root Volume（系统盘）
- Data Volume（数据盘）
- VM 实际运行时读写的空间

## 2.2 Secondary Storage（二级存储）
- Template（模板）
- ISO 镜像
- Snapshot（快照备份）

## 2.3 Image Store（抽象统一接口）
Secondary Storage 在 CloudStack 中由 ImageStore（NFS/S3/Swift）抽象：

```
DataStoreProvider
 └── NfsImageStoreProvider
 └── S3ImageStoreProvider
```

# 3. Volume 生命周期：从模板到卷

当用户执行：

```
deployVirtualMachine
```

CloudStack 会自动创建 Root Volume，其调用链：

```
DeployVMCmd.execute()
 → UserVmManagerImpl.deployVirtualMachine()
   → VolumeManagerImpl.allocate()
     → createVolumeFromTemplate()
       → chooseStoragePool()
       → copyTemplateToPrimary()
       → createEmptyVolumeOnPool()
```

# 4. createVolumeFromTemplate() 

源码位置：

```
engine/storage/volume/VolumeServiceImpl.java
```

关键逻辑：

```java
CreateObjectCommand cmd = new CreateObjectCommand(volume.getTO());
EndPoint ep = selector.select(destStore);
Answer answer = ep.sendMessage(cmd);

if (!answer.getResult())
    throw new CloudRuntimeException("Failed to create volume");
```

执行流程：

1. 构造 CreateObjectCommand  
2. Endpoint 选择一个执行者（Host / Storage VM）  
3. 发送指令至 Agent  
4. Agent 在 datastore 上创建卷  
5. 返回新卷路径（例如 /var/lib/libvirt/images/vm-1.qcow2）  

# 5. Template 拷贝流程（Secondary → Primary）

Root Volume 本质来自 Template。  
CloudStack 通过 CopyCommand 完成：

```java
CopyCommand cmd = new CopyCommand(srcTO, destTO, wait);
Answer answer = ep.sendMessage(cmd);
```

KVM 的 Agent 实际执行步骤：

```
1. 下载 template（若尚未在 secondary cache）
2. qemu-img convert 或直接 cp
3. 将模板写入 primary 存储池
4. 返回卷的最终路径
```

VMware 则通过 VCenter API：

```
RelocateVM_Task / CopyVirtualDisk
```

# 6. StoragePool 调度策略（StoragePoolAllocator）

CloudStack 使用 StoragePoolAllocator 为卷选择合适的存储池。

主要实现：

```
FirstFitStoragePoolAllocator
LocalStoragePoolAllocator
ClusterScopeStorageAllocator
```

核心逻辑源码：

```java
for (StoragePoolVO pool : pools) {
    if (!poolIsFull && pool.getAvailableSpace() > volumeSize) {
        return pool;
    }
}
throw new CloudRuntimeException("No suitable pool found");
```

调度因素：

- 校验空间  
- 校验可用性  
- 校验标签（storage tags）  
- 校验网络拓扑是否匹配  

# 7. Snapshot 工作流（SnapshotManagerImpl）

快照不是简单的文件复制，而是完整的备份工作流。

链路：

```
takeSnapshot
 → SnapshotServiceImpl.takeSnapshot()
   → create SnapshotObject
   → CopySnapshotCommand (primary → secondary)
   → update snapshot chain
```

SnapshotObject 负责抽象快照的数据结构：

```java
SnapshotObject snapObj = new SnapshotObject(snapshotVO, store);
```

关键指令：

```
CopySnapshotCommand
DeleteSnapshotCommand
```

Primary 可能支持内建 snapshot（Ceph RBD snapshot），否则通过 qemu-img/mcopy 实现。

# 8. StorageMotion（跨存储池迁移）源码分析

CloudStack 支持 StorageMotion（卷迁移），类似 VMware Storage vMotion。

调用链：

```
migrateVolume()
 → StorageManagerImpl.migrateVolume()
   → CopyCommand(srcPool → destPool)
   → Update VolumeVO.poolId
   → Delete old volume
```

源码关键：

```java
CopyCommand cmd = new CopyCommand(srcData, destData, true);
Answer answer = ep.sendMessage(cmd);

if (!answer.getResult())
    throw new CloudRuntimeException("Fail to migrate volume");
```

KVM 的 Agent 实际执行：

```
qemu-img convert -p -O qcow2 <src> <dest>
```

# 9. VolumeVO / SnapshotVO / TemplateDataStoreVO 结构解析

## 9.1 VolumeVO

字段：

```
id, pool_id, size, path, chain_info, state
```

## 9.2 SnapshotVO

```
volume_id, store_id, prev_snapshot_id, snapshot_type
```

## 9.3 TemplateDataStoreVO

```
template_id, store_id, state, install_path
```

用于描述模板的副本位置。

---

# 10. Agent 层指令（存储核心）

CloudStack 的存储操作全部通过 Command 指令实现：

| Command | 功能 |
|---------|--------|
| CreateObjectCommand | 创建卷 |
| CopyCommand | 拷贝 volume/template/snapshot |
| DeleteCommand | 删除文件 |
| AttachCommand | 挂载卷到 VM |
| DetachCommand | 卸载卷 |

以 CopyCommand 为例：

```java
public class CopyCommand extends Command {
    private DataTO srcTO;
    private DataTO destTO;
}
```

Agent 根据 src/dest 的类型执行不同操作：

- 二级库 → 主存储（模板复制）  
- 主存储 → 主存储（StorageMotion）  
- 主存储 → 二级库（快照备份）  

# 11. 存储时序图

```
deployVM
 |
 +--> VolumeManager.allocate()
 |        |
 |        +--> chooseStoragePool()
 |        +--> createVolumeFromTemplate()
 |
 +--> TemplateService.copyTemplateToPrimary()
 |
 +--> orchestrateDeployVM
          |
          +--> attach volume
          +--> StartCommand
```

# 12. 常见存储问题与源码排查方式

## 12.1 模板复制失败（CopyCommand 错误）

症状：

```
result=false, details="insufficient space"
```

排查：

```
storage_pool.used_bytes
storage_pool.capacity_bytes
primary storage 可写性
```

## 12.2 Snapshot 创建失败（KVM）

可能原因：

```
qemu-img convert 阻塞
卷正在使用（I/O 高负载）
NFS 延迟
```

## 12.3 StorageMotion 中断

检查：

```
agent.log
management-server.log
```

关键日志：

```
CopyCommand failed during qemu-img convert
```

# 13. 小结

CloudStack 存储体系是一个完整的抽象框架：

- DataStoreProvider 插件化架构  
- Template / Volume / Snapshot 全生命周期  
- StoragePoolAllocator 负责调度  
- 多级缓存（SSVM / ImageCache）  
- 统一的 CopyCommand / CreateObjectCommand  

