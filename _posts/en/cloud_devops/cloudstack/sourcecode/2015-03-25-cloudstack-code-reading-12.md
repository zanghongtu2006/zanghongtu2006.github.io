---
layout: post
lang: en
translations:
  en: /en/cloudstack-code-reading-12/
  zh: /zh/cloudstack-code-reading-12/
permalink: /en/cloudstack-code-reading-12/
slug: "cloudstack-code-reading-12"
title: "CloudStack Code（12）—— Analysis of security models (API Key / Signature / RBAC / ACL / prevention of privilege escalation)"
date: "2015-03-25 22:46:33"
categories: ["CloudStack"]
tags: ["security", "signature", "api", "rbac", "acl", "source-analysis"]
draft: false
---
CloudStack's security architecture consists of the following components:

- API Key / Secret Key → Request Signature
- HMAC-SHA1 → Parameter Signature Verification
- RBAC (Role-Based Access Control)
- AccessControlService → Resource-Level Permission Check
- Domain / Account Isolation
- System Behavior Auditing (CallContext)

# 1. API Security Architecture

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

# 2. API Key / Secret Key: Authentication Basics

UserAccountVO contains:

```
api_key
secret_key
```

When a user calls:

```
https://cs/api?command=listVirtualMachines&apiKey=...&signature=...
```

CloudStack executes the following in the APIServer:

```
validateRequest(params)
 → verifySignature(apiKey, signature)
 → authenticateUser()
```

# 3. Signature Calculation Process

## 3.1 Client Signature Steps

Pseudo:

```
1. Convert all parameters to lowercase
2. Sort alphabetically
3. URL encode
4. Concatenate into "key=value&key=value"
5. Perform HMAC-SHA1 using secretKey
6. Base64 encode the result
```

## 3.2 Server-side verification process

ApiServer.java:

```java
String signature = params.remove("signature");
String unsignedRequest = signRequest(params);
String computedSignature = signRequest(unsignedRequest, secretKey);

if (!computedSignature.equals(signature)) {
    throw new ServerApiException(ApiErrorCode.PARAM_ERROR, "signature mismatch");
}
```

Key function:

```java
private String signRequest(String request, String key) {
    SecretKeySpec keySpec = new SecretKeySpec(key.getBytes(), "HmacSHA1");
    Mac mac = Mac.getInstance("HmacSHA1");
    mac.init(keySpec);
    return Base64.encode(mac.doFinal(request.getBytes()));
}
```

# 4. APIAuthenticator: User authentication logic

```text
APIAuthenticationManagerImpl
```

Authentication order:

```text
1. If a sessionKey is provided → Attempt to log in to the session
2. If an apiKey is provided → Verify the signature
3. If no identity is found → Throw an unauthenticated error
```

# 5. CallContext: Request Context and Auditing

CallContext is a context logger for all API calls in CloudStack.

Key Content:

```
caller userId
caller accountId
context parameters
event type
```

Souce code:

```java
public static void registerCaller(User callingUser, Account callingAccount) {
    current.set(new CallContext(callingUser, callingAccount));
}
```

CallContext runs throughout the entire call chain, providing a basis for auditing.
# 6. API access control（@APICommand）

Each API must declare its own permissions:
```java
@APICommand(name = "deleteUser",
            authorized = {RoleType.Admin},
            responseObject = SuccessResponse.class)
```

ApiServer authorzation:

```java
if (!cmdSpec.isAuthorized(callerRole)) {
    throw new ServerApiException(ApiErrorCode.UNAUTHORIZED, "Denied");
}
```

# 7. AccessControlService（ACL）

ACL core classes:

```
AccessControlService
DomainChecker（默认实现）
```

Key function:

```java
checkAccess(caller, AccessType.UseEntry, true, resourceObj);
```

## 7.1 Key inspection logic

DomainChecker:

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

# 8. Resource Ownership

Each resource (VM/Volume/Network) implements:

```
ControlledEntity
```

Fields:

```
account_id
domain_id
```

CloudStack's isolation logic is based on these two fields.

Example: User A cannot access a VM in domain B because:

```
caller.domain != resource.domain
caller.account != resource.account
```

# 9. RBAC 

### Role

```
roles.id
roles.name
```

### Role Permissions

```
role_permissions.role_id
role_permissions.api_name
role_permissions.allow
```

RolePermissionsDaoImpl:

```java
boolean isPermitted(long roleId, String apiName) {
    RolePermissionVO perm = findByRoleAndApi(roleId, apiName);
    return perm != null && perm.isAllowed();
}
```

# 10. Anti-unauthorization mechanism

## 10.1 Resource belong-to check

```
if (resource.accountId != caller.accountId)
```

## 10.2 Domain inheritance relationship check

```
isChildDomain(caller.domain, resource.domain)
```

## 10.3 Privileged API Restrictions

```
@APICommand(authorized = {RoleType.Admin})
```

## 10.4 Identity Context Check

```
CallContext.current().getCallingAccount()
```

# 11. API Security Sequence Diagram

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

# 12. Common security issues and solutions

## 12.1 Signature mismatch

Reasons:

- Incorrect parameter case
- Inconsistent URL encoding
- Inconsistent parameter order
## 12.2 Unauthorized access to resources

Exception:

```
PermissionDeniedException
```

Check:

- Does domain_id belong to a subtree?
- Does account_id match?
- Does rolePermissions allow API calls?

## 12.3 Cross-domain network access failed

```
Network is owned by another domain
```

# 13. Summary

The CloudStack security architecture consists of multiple layers:

- API Key / Secret Key (Authentication)
- HMAC-SHA1 (Signature)
- RBAC (Role-Based Account)
- AccessControlService (Resource Access Control)
- Domain / Account (Hierarchical Isolation)
- Project (Collaboration Security Boundary)
- CallContext (Audit)

CloudStack's security design is extremely rigorous in multi-tenant environments, forming a complete closed loop through strict resource ownership, domain tree, and role-based access control models.
