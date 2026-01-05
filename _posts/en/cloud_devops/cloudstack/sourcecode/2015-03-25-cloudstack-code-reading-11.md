---
layout: post
lang: en
translations:
  en: /en/cloudstack-code-reading-11/
  zh: /zh/cloudstack-code-reading-11/
permalink: /en/cloudstack-code-reading-11/
slug: "cloudstack-code-reading-11"
title: "CloudStack Code（11）—— Analysis of the user system（Account / Domain / Project / Role / AccessControl）"
date: "2015-03-25 15:54:43"
categories: ["CloudStack"]
tags: ["account", "domain", "acl", "accesscontrol", "rbac", "source-analysis"]
draft: false
---

CloudStack's user system is a **multi-tenant isolation model**, which consists of multiple mechanisms such as Domain Tree, Account, Role, Resource Ownership, and Access Control Service.
# 1. Main Components of CloudStack User Model

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

# 2. Domain: The Core of the CloudStack User System

## 2.1 Domain is the highest-level unit of resource isolation

Domains form a tree:

```
ROOT DOMAIN
   ├── Department A
   │      ├── Team A1
   │      └── Team A2
   └── Department B
          ├── ...
```

souce code structure:

```
DomainVO
    id
    name
    parent
    path
```

Domain path:

```
/ROOT/DepartmentA/TeamA2/
```

Domain decides:

- Account hierarchy
- Visible resource scope
- Network accessibility
- Permitted operations (superior has administrative privileges over subordinates)

# 3. Account: Entities that truly own the resources

The account is the owner of the CloudStack resources.

- VM  
- Volume  
- Network  
- Snapshot  
- Template  
- IP Address  

Account Type:

```
ADMIN = Administrator account
DOMAIN ADMIN = Manages subdomain resources
USER = Regular user
PROJECT = Project account (virtual account)
```

AccountVO（key fields）:

```
id
account_name
domain_id
type  (0=user, 1=domain-admin, 2=root-admin)
state
uuid
```

# 4. User and UserAccount

A User is the login subject under an Account. An Account can contain multiple Users.
UserAccountVO:

```
id
account_id
username
password
state
api_key
secret_key
```

User is bound to API Key/Secret Key to achieve API authentication.
# 5. Project: Cross-Account Collaboration Mechanism

A Project is a "shared account" in CloudStack that allows multiple accounts to collaborate on using resources within the same Project.  

Key Classes:

```
ProjectManagerImpl
ProjectAccountVO
ProjectInvitationVO
```

When accessing resources, Project replaces Account, providing a virtual shared identity.

# 6. Ownership

All resources (VM/Network/Volume) come with:
```
account_id
domain_id
```

typical VO:

VolumeVO:

```
private long accountId;
private long domainId;
```

Resource permission check:

```
Account caller = CallContext.current().getCallingAccount();
_accessControlService.checkAccess(caller, null, true, resourceObj);
```

# 7. AccessControlService: Access verification core

Located at:

```
com.cloud.api.acl.AccessControlService
```

Default implementation:

```
com.cloud.api.acl.DomainChecker
```

key function:

```java
public void checkAccess(Account caller, AccessType accessType, boolean sameOwner, ControlledEntity... entities)
```

### 7.1 Access Control Rules

- Root admin can access all resources.
- Domain admin can manage resources within the current domain and subdomains.
- User can only access their own resources.
- Project members can access Project resources.
- ControlledEntity is bound to an Account.

### 7.2 checkAccess source code

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

Check items:

1. Account type
2. Domain hierarchy
3. Resource ownership
4. Special rules (Network, Template public properties, etc.)

# 8. API layer access control（@APICommand）

Each API command uses:

```
@APICommand(authorized = {RoleType.Admin, RoleType.DomainAdmin})
```

Example:

```java
@APICommand(name = "deleteVirtualMachine",
            authorized = {RoleType.Admin, RoleType.ResourceAdmin})
```

When mapping APIs, ApiServer first checks whether the caller belongs to the authorized list.

Source Path:

```
ApiServer.checkCommandAvailable(cmdClass, callerAccount)
```

# 9. RBAC（Role Based Access Control）

CloudStack's RBAC model is based on:

- Roles
- RolePermissions
- API to Role mapping table

DB Table:
```
roles
role_permissions
```

RolePermissionsDaoImpl:

```java
boolean isPermitted(long roleId, String apiName) {
    RolePermissionVO perm = _rolePermDao.findByRoleAndApi(roleId, apiName);
    return perm != null && perm.isAllowed();
}
```

# 10. User system sequence diagram (login and API calls)

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

# 11. Comprehensive Interaction Diagram of Domain / Account / Project / Role Permissions

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

API call permissions are jointly determined by:

- Caller type
- Domain level
- Resource account/domain
- Project membership
- Role permission
- List of API authorized permissions

# 12. Common permission issues and source code troubleshooting

## 12.1 PermissionDeniedException

```
AccessControlService.checkAccess() failed
```

Check:

- Is resource.domain_id within the caller's visibility range?
- Does resource.account_id match?
- Are the project members correct?

## 12.2 API call error 531 - Insufficient permissions.

ApiServer:

```
API is not permitted for this role
```

Check if role_permissions is configured correctly.
## 12.3 Resources are "domain isolated"

If the VM belongs to a subdomain, but the caller is in a sibling domain:

```
Domain mismatch
```

# 13. Summary

CloudStack's user system consists of the following components:

- **Domain (Domain Level)**: Determines the visibility scope
- **Account (Resource Ownership)**: Determines resource ownership
- **User (Login Principal)**
- **Project (Shared Account)**
- **Role (Role)**
- **AccessControlService (Access Control Service)**
- **Authorized rules for @APICommand**

While CloudStack's multi-tiered ACL model is complex, its source code is very clear: **it always revolves around validating the resource's account/domain fields**.
