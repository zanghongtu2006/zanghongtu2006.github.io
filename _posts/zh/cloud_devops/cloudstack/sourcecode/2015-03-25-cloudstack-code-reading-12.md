---
layout: post
lang: zh
translations:
  en: /en/cloudstack-code-reading-12/
  zh: /zh/cloudstack-code-reading-12/
permalink: /zh/cloudstack-code-reading-12/
slug: "cloudstack-code-reading-12"
title: "CloudStack 代码阅读（十二）—— 安全模型深度解析（API Key / Signature / RBAC / ACL / 防越权）"
date: "2015-03-25 22:46:33"
categories: ["CloudStack"]
tags: ["security", "signature", "api", "rbac", "acl", "source-analysis"]
draft: false
---
CloudStack 的安全体系由以下部分构成：

- API Key / Secret Key → 请求签名  
- HMAC-SHA1 → 参数签名校验  
- RBAC（基于角色的访问控制）  
- AccessControlService → 资源级权限检查  
- Domain / Account 隔离  
- 系统行为审计（CallContext）  

# 1. API 安全体系结构（源码路径）

```
server/src/com/cloud/api/
    ├── ApiServer.java
    ├── ApiServlet.java
    ├── dispatcher/
    │       └── ApiDispatcher.java
    ├── auth/
    │       ├── APIAuthenticationManagerImpl.java
    │       └── APIAuthenticator.java
api/src/org/apache/cloudstack/api/
    ├── APICommand.java
    ├── ResponseObject.java
server/src/com/cloud/api/acl/
    ├── AccessControlService.java
    ├── DomainChecker.java
```

# 2. API Key / Secret Key：认证基础

UserAccountVO 包含：

```
api_key
secret_key
```

当用户调用：

```
https://cs/api?command=listVirtualMachines&apiKey=...&signature=...
```

CloudStack 在 ApiServer 中执行：

```
validateRequest(params)
 → verifySignature(apiKey, signature)
 → authenticateUser()
```

# 3. Signature 计算流程（源码级）

## 3.1 客户端签名步骤

Pseudo:

```
1. 所有参数转小写
2. 按字母排序
3. URL encode
4. 拼成 "key=value&key=value"
5. 使用 secretKey 做 HMAC-SHA1
6. 结果做 Base64 encode
```

## 3.2 服务端校验流程

ApiServer.java：

```java
String signature = params.remove("signature");
String unsignedRequest = signRequest(params);
String computedSignature = signRequest(unsignedRequest, secretKey);

if (!computedSignature.equals(signature)) {
    throw new ServerApiException(ApiErrorCode.PARAM_ERROR, "signature mismatch");
}
```

核心方法：

```java
private String signRequest(String request, String key) {
    SecretKeySpec keySpec = new SecretKeySpec(key.getBytes(), "HmacSHA1");
    Mac mac = Mac.getInstance("HmacSHA1");
    mac.init(keySpec);
    return Base64.encode(mac.doFinal(request.getBytes()));
}
```

# 4. APIAuthenticator：用户认证逻辑

```
APIAuthenticationManagerImpl
```

认证顺序：

```
1. 如果提供 sessionKey → 尝试登录 session
2. 如果提供 apiKey → 校验签名
3. 如果仍无身份 → 抛出未认证
```

# 5. CallContext：请求上下文与审计

CallContext 是 CloudStack 所有 API 调用的上下文记录器。

关键内容：

```
caller userId
caller accountId
context parameters
event type
```

源码：

```java
public static void registerCaller(User callingUser, Account callingAccount) {
    current.set(new CallContext(callingUser, callingAccount));
}
```

CallContext 贯穿整个调用链，为审计提供依据。

# 6. API 权限控制（@APICommand）

每个 API 必须声明自己的权限：

```java
@APICommand(name = "deleteUser",
            authorized = {RoleType.Admin},
            responseObject = SuccessResponse.class)
```

ApiServer 验证：

```java
if (!cmdSpec.isAuthorized(callerRole)) {
    throw new ServerApiException(ApiErrorCode.UNAUTHORIZED, "Denied");
}
```

# 7. AccessControlService：资源级别安全检查（ACL）

ACL 核心类：

```
AccessControlService
DomainChecker（默认实现）
```

核心方法：

```java
checkAccess(caller, AccessType.UseEntry, true, resourceObj);
```

## 7.1 关键检查逻辑

DomainChecker：

```java
if (caller.getType() == ROOT_ADMIN) return;

long resourceDomain = entity.getDomainId();

if (!isInDomainTree(callerDomain, resourceDomain)) {
    throw new PermissionDeniedException("Domain mismatch");
}

if (entity.getAccountId() != caller.getAccountId() &&
    callerNotParentDomainAdmin) {
    throw new PermissionDeniedException("Account mismatch");
}
```

---

# 8. Resource Ownership（资源所有权隔离）

每个资源（VM / Volume / Network）都实现：

```
ControlledEntity
```

字段：

```
account_id
domain_id
```

CloudStack 的隔离逻辑基于这两个字段。

举例：用户 A 无法访问域 B 的 VM，因为：

```
caller.domain != resource.domain
caller.account != resource.account
```

# 9. RBAC：角色权限模型

### 角色（Role）

```
roles.id
roles.name
```

### 权限（Role Permissions）

```
role_permissions.role_id
role_permissions.api_name
role_permissions.allow
```

RolePermissionsDaoImpl：

```java
boolean isPermitted(long roleId, String apiName) {
    RolePermissionVO perm = findByRoleAndApi(roleId, apiName);
    return perm != null && perm.isAllowed();
}
```

# 10. 防越权机制

## 10.1 资源 belong-to 检查

```
if (resource.accountId != caller.accountId)
```

## 10.2 域继承关系检查

```
isChildDomain(caller.domain, resource.domain)
```

## 10.3 特权 API 限制

```
@APICommand(authorized = {RoleType.Admin})
```

## 10.4 身份上下文检查

```
CallContext.current().getCallingAccount()
```

# 11. API 安全时序图（ASCII）

```
API Request
  |
  +--> ApiServer.receiveRequest()
          |
          +--> validateSignature()
          |
          +--> authenticateUser()
          |
          +--> ApiDispatcher.dispatch(cmd)
                  |
                  +--> AccessControlService.checkAccess()
                  |
                  +--> execute()
```

# 12. 常见安全问题与解决方法（源码级）

## 12.1 签名不匹配（Signature mismatch）

原因：

- 参数大小写错误  
- URL encode 不一致  
- 参数排序不一致  

## 12.2 越权访问资源

报错：

```
PermissionDeniedException
```

检查：

- domain_id 是否属于子树  
- account_id 是否一致  
- rolePermissions 是否允许调用 API  

## 12.3 跨域访问网络失败

```
Network is owned by another domain
```

# 13. 小结

CloudStack 安全体系由多个层级构成：

- API Key / Secret Key（鉴权）
- HMAC-SHA1（签名）
- RBAC（角色能力）
- AccessControlService（资源访问控制）
- Domain / Account（层级隔离）
- Project（协作安全边界）
- CallContext（审计）

CloudStack 的安全设计在多租户环境中极其严谨，并通过严格的资源 ownership、domain tree、角色权限模型构成完整闭环。
