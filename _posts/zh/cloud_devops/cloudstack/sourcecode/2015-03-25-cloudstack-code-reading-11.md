---
layout: post
lang: zh
translations:
  en: /en/cloudstack-code-reading-11/
  zh: /zh/cloudstack-code-reading-11/
permalink: /zh/cloudstack-code-reading-11/
slug: "cloudstack-code-reading-11"
title: "CloudStack 代码阅读（十一）—— 用户体系深度解析（Account / Domain / Project / Role / AccessControl）"
date: "2015-03-25 15:54:43"
categories: ["CloudStack"]
tags: ["account", "domain", "acl", "accesscontrol", "rbac", "source-analysis"]
draft: false
---

CloudStack 的用户体系是一个 **多租户隔离模型**，采用层级域（Domain Tree）+ 账户（Account）+ 角色（Role）+ 资源所有权（Ownership）+ 访问控制（AccessControlService）等多重机制构成。  

# 1. CloudStack 用户模型主要组件
```
server/src/com/cloud/user/
    ├── AccountManagerImpl.java
    ├── DomainManagerImpl.java
    ├── UserAccountVO.java
    ├── AccountVO.java
    ├── DomainVO.java
    └── dao/

server/src/com/cloud/api/acl/
    ├── AccessControlService.java
    ├── ProjectRoleManagerImpl.java
    ├── RolePermissionsDaoImpl.java
```

# 2. Domain：CloudStack 用户体系核心

## 2.1 Domain 是资源隔离的最上级单位

Domain 构成一棵树：

```
ROOT DOMAIN
   ├── Department A
   │      ├── Team A1
   │      └── Team A2
   └── Department B
          ├── ...
```

源码结构：

```
DomainVO
    id
    name
    parent
    path
```

Domain path 如：

```
/ROOT/DepartmentA/TeamA2/
```

Domain 决定：

- 账户所属层级  
- 可见资源范围  
- 网络可访问性  
- 允许的操作（上级对下级有管理权限）

# 3. Account：真正拥有资源的实体

Account 是 CloudStack 的资源所有者：

- VM  
- Volume  
- Network  
- Snapshot  
- Template  
- IP 地址  

Account 类型：

```
ADMIN = 管理员账户
DOMAIN ADMIN = 管理子域资源
USER = 普通用户
PROJECT = 项目账户（虚拟账户）
```

AccountVO（核心字段）：

```
id
account_name
domain_id
type  (0=user, 1=domain-admin, 2=root-admin)
state
uuid
```

# 4. User 与 UserAccount

User 是 Account 下的登录主体，一个 Account 可以包含多个 User。

UserAccountVO：

```
id
account_id
username
password
state
api_key
secret_key
```

User 绑定 API Key/Secret Key，实现 API 鉴权。

# 5. Project：跨账户协作机制

Project 是 CloudStack 的“共享账户”，允许多个 Account 在放置于同一 Project 中协作使用资源。

关键类：

```
ProjectManagerImpl
ProjectAccountVO
ProjectInvitationVO
```

Project 在资源访问时会替代 Account，提供一个虚拟的共享身份。

# 6. 资源所有权（Ownership）

所有资源（VM/Network/Volume）都带有：

```
account_id
domain_id
```

典型 VO：

VolumeVO:

```
private long accountId;
private long domainId;
```

资源权限检查：

```
Account caller = CallContext.current().getCallingAccount();
_accessControlService.checkAccess(caller, null, true, resourceObj);
```

# 7. AccessControlService：权限验证核心

位置：

```
com.cloud.api.acl.AccessControlService
```

默认实现：

```
com.cloud.api.acl.DomainChecker
```

核心方法：

```java
public void checkAccess(Account caller, AccessType accessType, boolean sameOwner, ControlledEntity... entities)
```

### 7.1 权限规则

- Root admin 可以访问所有资源  
- Domain admin 可以管理本域及子域资源  
- User 仅能访问自己资源  
- Project 成员可访问 Project 资源  
- ControlledEntity 由 Account 绑定  

### 7.2 checkAccess 源码解析

```java
if (caller.getType() == Account.ACCOUNT_TYPE_ADMIN) {
    return;  // root-admin 直接放行
}

for (ControlledEntity entity : entities) {
    if (entity.getAccountId() == caller.getAccountId()) continue;

    if (isChildDomain(caller.domain, entity.domain)) continue;

    throw new PermissionDeniedException(...);
}
```

检查项目：

1. 账户类型  
2. 域层级关系  
3. 资源归属  
4. 特殊规则（Network，Template 公有属性等）

# 8. API 层权限控制（@APICommand）

每个 API 命令使用：

```
@APICommand(authorized = {RoleType.Admin, RoleType.DomainAdmin})
```

例如：

```java
@APICommand(name = "deleteVirtualMachine",
            authorized = {RoleType.Admin, RoleType.ResourceAdmin})
```

ApiServer 在映射 API 时会先校验调用者是否属于 authorized 列表。

源码路径：

```
ApiServer.checkCommandAvailable(cmdClass, callerAccount)
```

# 9. RBAC（Role Based Access Control）角色权限控制

CloudStack 的 RBAC 模型基于：

- 角色（Role）
- 权限（RolePermission）
- API 与 Role 映射表

数据表：

```
roles
role_permissions
```

RolePermissionsDaoImpl：

```java
boolean isPermitted(long roleId, String apiName) {
    RolePermissionVO perm = _rolePermDao.findByRoleAndApi(roleId, apiName);
    return perm != null && perm.isAllowed();
}
```

# 10. 用户体系时序图（登录与 API 调用）

```
User login
  |
  v
UserAuthenticator.authenticate()
  |
  v
ApiServer.authenticateUser(apiKey, signature)
  |
  v
CallContext.create(caller)
  |
  v
ApiDispatcher.dispatch()
  |
  v
AccessControlService.checkAccess()
  |
  v
Execute API
```

# 11. Domain / Account / Project / Role 权限综合交互示意图

```
ROOT DOMAIN (root-admin)
/       
A        B   (domain-admin)
|        |
A1       B1  (regular users)

Project-1 (shared identity for A1 + B1 users)
   |
   |--- owns VMs / Networks / Volumes
```

API 调用权限由：

- 调用者类型  
- 域层级  
- 资源 account/domain  
- project 成员关系  
- role permission  
- API authorized 列表  

共同决定。

# 12. 常见权限问题与源码排查

## 12.1 PermissionDeniedException

```
AccessControlService.checkAccess() failed
```

检查：

- resource.domain_id 是否属于 caller 可见范围  
- resource.account_id 是否匹配  
- project 成员是否正确  

## 12.2 API 调用 531 权限不足

ApiServer：

```
API is not permitted for this role
```

检查 role_permissions 是否配置正确。

## 12.3 资源被“域隔离”

如果 VM 属于子域，而调用者在兄弟域：

```
Domain mismatch
```

# 13. 小结

CloudStack 的用户体系由如下部分组成：

- **Domain（域层级）**：决定可见范围  
- **Account（资源所有权）**：决定资源归属  
- **User（登录主体）**  
- **Project（共享账户）**  
- **Role（角色）**  
- **AccessControlService（权限核心）**  
- **@APICommand 的 authorized 规则**  

CloudStack 的多层 ACL 模型虽然复杂，但其源码非常清晰：**始终围绕资源的 account/domain 两个字段进行验证**。
