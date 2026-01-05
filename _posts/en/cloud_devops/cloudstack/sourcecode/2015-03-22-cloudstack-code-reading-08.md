---
layout: post
lang: en
translations:
  zh: /zh/cloudstack-code-reading-08/
  en: /en/cloudstack-code-reading-08/
permalink: /en/cloudstack-code-reading-08/
slug: "cloudstack-code-reading-08"
title: "CloudStack Code（8）—— In-depth analysis of storage system（Primary/Secondary/Snapshot/StorageMotion）"
date: "2015-03-22 10:55:23"
categories: ["CloudStack"]
tags: ["storage", "primary", "secondary", "snapshot", "storagemotion", "source-analysis"]
draft: false
---
CloudStack's storage architecture is more hidden and complex than its network module. It involves templates, volumes, snapshots, cross-pool migration (StorageMotion), structured management of the Secondary Image Store, and deep integration with the Hypervisor.

The following analysis will break down the underlying method call chain, data structures, key instructions, and the Agent's execution mechanism layer by layer.

# 1. Storage module hierarchy (source code path)

```text
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

CloudStack breaks down "storage" into logical modules, with the backbone responsible for scheduling and the plug-ins responsible for interacting with the actual backend (NFS/iSCSI/Ceph/SolidFire).
# 2. Primary / Secondary / Image Store:3 layer model

CloudStack's storage system consists of three layers:

## 2.1 Primary Storage
- Root Volume (System Disk)
- Data Volume
- The space actually read and written by the VM during runtime

## 2.2 Secondary Storage
- Template
- ISO Image
- Snapshot Backup

## 2.3 Image Store (Abstract Unified Interface)
Secondary Storage in CloudStack is abstracted by ImageStore (NFS/S3/Swift):

```text
DataStoreProvider
 └── NfsImageStoreProvider
 └── S3ImageStoreProvider
```

# 3. Volume Lifecycle: From Template to Volume

When the user executes:

```text
deployVirtualMachine
```
CloudStack automatically creates the Root Volume, its call chain is:

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

Source code:

```
engine/storage/volume/VolumeServiceImpl.java
```

Key Logic:

```java
CreateObjectCommand cmd = new CreateObjectCommand(volume.getTO());
EndPoint ep = selector.select(destStore);
Answer answer = ep.sendMessage(cmd);

if (!answer.getResult())
    throw new CloudRuntimeException("Failed to create volume");
```

Process flow:
1. Construct CreateObjectCommand
2. Endpoint: Select an executor (Host/Storage VM)
3. Send the command to the Agent
4. Agent: Creates the volume on the datastore
5. Returns the new volume path (e.g., /var/lib/libvirt/images/vm-1.qcow2)

# 5. Template Copy Process (Secondary → Primary)

The Root Volume essentially originates from the Template.

CloudStack completes this via CopyCommand:

```java
CopyCommand cmd = new CopyCommand(srcTO, destTO, wait);
Answer answer = ep.sendMessage(cmd);
```

The actual execution steps of the KVM Agent:
```
1. Download the template (if it's not already in the secondary cache)
2. Use `qemu-img convert` or simply `cp`
3. Write the template to the primary storage pool
4. Return the final path of the volume
```

VMware, on the other hand, uses the VCenter API:

```
RelocateVM_Task / CopyVirtualDisk
```

# 6. StoragePool scheduling policy (StoragePoolAllocator)

CloudStack uses StoragePoolAllocator to select the appropriate storage pool for a volume.

Main implementation:
```
FirstFitStoragePoolAllocator
LocalStoragePoolAllocator
ClusterScopeStorageAllocator
```

Core logic source code:

```java
for (StoragePoolVO pool : pools) {
    if (!poolIsFull && pool.getAvailableSpace() > volumeSize) {
        return pool;
    }
}
throw new CloudRuntimeException("No suitable pool found");
```

Scheduling factors:

- Verification space
- Verification availability
- Verification tags
- Verification network topology matching
# 7. Snapshot workflow（SnapshotManagerImpl）

A snapshot is not simply a file copy; it's a complete backup workflow.

Chain:
```text
takeSnapshot
 → SnapshotServiceImpl.takeSnapshot()
   → create SnapshotObject
   → CopySnapshotCommand (primary → secondary)
   → update snapshot chain
```

SnapshotObject is responsible for abstracting the data structure of snapshots:

```java
SnapshotObject snapObj = new SnapshotObject(snapshotVO, store);
```

Key instructions:
```
CopySnapshotCommand
DeleteSnapshotCommand
```
Primary may support built-in snapshots (Ceph RBD snapshots), otherwise it is implemented via qemu-img/mcopy.

# 8. StorageMotion (Cross-Storage Pool Migration) Source Code Analysis

CloudStack supports StorageMotion (volume migration), similar to VMware Storage vMotion.

Call Chain:

```
migrateVolume()
 → StorageManagerImpl.migrateVolume()
   → CopyCommand(srcPool → destPool)
   → Update VolumeVO.poolId
   → Delete old volume
```

key source code:

```java
CopyCommand cmd = new CopyCommand(srcData, destData, true);
Answer answer = ep.sendMessage(cmd);

if (!answer.getResult())
    throw new CloudRuntimeException("Fail to migrate volume");
```

The KVM Agent actually executes:

```
qemu-img convert -p -O qcow2 <src> <dest>
```

# 9. VolumeVO / SnapshotVO / TemplateDataStoreVO Structure Analysis

## 9.1 VolumeVO

fields:

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

It is used to describe the copy location of the template。

---

# 10. Agent layer instructions

All storage operations in CloudStack are performed using Command statements:

| Command | Function |
|---------|--------|
| CreateObjectCommand | Create a volume |
| CopyCommand | Copy volume/template/snapshot |
| DeleteCommand | Delete a file |
| AttachCommand | Mount a volume to a VM |
| DetachCommand | Unmount a volume |

For example, using CopyCommand:

```java
public class CopyCommand extends Command {
    private DataTO srcTO;
    private DataTO destTO;
}
```

The agent performs different operations based on the type of src/dest:

- Secondary database → Primary storage (template replication)
- Primary storage → Primary storage (StorageMotion)
- Primary storage → Secondary database (snapshot backup)

# 11. Storage timing diagram

```text
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

# 12. Common Storage Issues and Source Code Troubleshooting Methods

## 12.1 Template Copying Failure (CopyCommand Error)

Exception:

```
result=false, details="insufficient space"
```

Check:

```
storage_pool.used_bytes
storage_pool.capacity_bytes
primary storage writability
```

## 12.2 Snapshot creation failed (KVM)

Possible causes:

```
`qemu-img convert` is blocking.
Volume is in use (high I/O load).
NFS latency.
```

## 12.3 StorageMotion Interruption

Check:
```
agent.log
management-server.log
```

Log keywords:

```
CopyCommand failed during qemu-img convert
```

# 13. Summary

The CloudStack storage system is a complete abstract framework:

- Plug-in architecture for DataStoreProvider
- Full lifecycle management of Templates, Volumes, and Snapshots
- Scheduling handled by StoragePoolAllocator
- Multi-level caching (SSVM/ImageCache)
- Unified CopyCommand/CreateObjectCommand
