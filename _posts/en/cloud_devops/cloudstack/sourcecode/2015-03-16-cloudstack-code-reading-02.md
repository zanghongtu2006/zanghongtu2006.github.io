---
layout: post
lang: en
translations:
  en: /en/cloudstack-code-reading-02/
  zh: /zh/cloudstack-code-reading-02/
permalink: /en/cloudstack-code-reading-02/
slug: "cloudstack-code-reading-02"
title: "CloudStack Code（二）- API framework execution mechanism（ApiServer、Dispatcher、Signature、Async）"
date: "2015-03-16 19:00:36"
categories: ["CloudStack"]
tags: ["api-framework", "apiserver", "dispatcher", "signature", "asyncjob"]
draft: false
---

This chapter provides an in-depth analysis of the CloudStack API's **execution chain, reflection mechanism, parameter parsing, permission system, error handling, signature verification, and asynchronous task scheduling**. This is the core of understanding the CloudStack management plane.
# 1. API Execution Overview: From HTTP to Internal Commands
The API call execution flow is as follows:

```text
HTTP Request
 → ApiServlet.doGet/doPost
 → ApiServer.handleRequest()
 → ApiDispatcher.dispatch()
 → BaseCmd / BaseAsyncCmd.execute()
 → Manager 层业务逻辑
 → ResponseObject
 → JSON Serializer
 → HTTP Response
```

CloudStack's API is not RESTful, but rather **command-centric**:  
`?command=createVirtualMachine&serviceofferingid=...`

Internal execution characteristics:

- Command mapping uses **reflection + annotation scanning**
- Parameter binding uses **annotations + type resolver**
- Scheduled calls use **Command Pattern**
- Many APIs are asynchronous, managed through **AsyncJobManager**
- JSON output uses **Gson** serialization

# 2. ApiServlet: The entry point for all API calls
ApiServlet located in：

```text
server/src/com/cloud/api/ApiServlet.java
```

Responsibilities:

- Parse GET/POST requests
- Extract all parameters
- Call the ApiServer
- Unified exception encapsulation

Pseudocode:

```java
Map<String, String[]> params = request.getParameterMap();
String response = apiServer.handleRequest(params, responseType);
```

It doesn't perform any business logic; it almost entirely proxies the API server.  
# 3. ApiServer: The core scheduler of the CloudStack API
ApiServer (`ApiServerImpl`) is the brain of the API framework.

## 3.1 ApiServer Core Responsibilities  
The ApiServer handles the following:

1. Parameter preprocessing
2. Signature verification
3. Obtaining the Command class
4. Instantiating the Command class
5. Parameter binding (reflection)
6. Permission verification
7. Calling the management service (Manager)
8. Constructing a ResponseObject
9. JSON serialization

Core methods:

```java
String handleRequest(Map params, boolean isAsync)
```

## 3.2 How does the APIServer locate a specific API Command?

The Command registration logic scans during system startup:

- `org.apache.cloudstack.api.command.user.*`
- `org.apache.cloudstack.api.command.admin.*`

Any Class with：

```java
@APICommand(name = "startVirtualMachine")
```

will add into a Map：

```java
Map<String, Class<? extends BaseCmd>> s_cmds;
```

Therefore, API ≈ Java class name dynamic binding system

# 4. ApiDispatcher: Command Dispatcher

The role of Dispatcher:

- Locate the command class based on the API name (string)
- Create an object using reflection
- Call execute()

Pseudocode:
```java
Class cmdClass = s_cmds.get(commandName);
BaseCmd cmd = cmdClass.newInstance();
cmd.execute();
```

# 5. Parameter Annotations Mechanism 

Each API parameter is resolved through:

```java
@Parameter(name="id", type=CommandType.UUID, required=true)
```
API Parameter Parsing Process:

1. The APIServer finds the parameter matching the annotation in the request;
2. Performs type conversion based on `CommandType`;
3. If it is a UUID, it queries the database mapping for the internal ID (Long);
4. Sets the field using reflection, for example:

```java
field.set(cmdInstance, convertedValue);
```

## 5.1 Parameter type support
CloudStack supported types：

- BOOLEAN  
- INTEGER  
- LONG  
- UUID → Long  
- LIST → List<String>  
- MAP → `LinkedHashMap<String, Object>`  

## 5.2 Multi-parameter logic  
Example：

```
ids=1,2,3
```

It will be parsed as List。

# 6. Permission Verification: Account / Domain / Role

CloudStack's permission system is based on a three-tier structure:

| Tier | Meaning |
|------|------|
| Account | Independent User Level |
| Domain | Management Subdomain Isolation |
| Role | API Permission Table |

Permission checks consist of two parts:

## 6.1 APICommand annotation permissions
By：
```
@APICommand(authorized = {RoleType.Admin})
```
Restricts the caller's role.

## 6.2 Resource access permissions
Example：
```
{id: VM_UUID}
```

ApiServer will：

1. Convert UUID to internal ID
2. Check resource owner
3. Use AccessControlService to verify user permissions to the VM

Core method:

```java
_accountMgr.checkAccess(caller, AccessType.UseEntry, true, vmObj);
```
This is the core of the CloudStack security model.

# 7. Signature Mechanism (API Key + Secret Key)

CloudStack supports "signature authentication" for use with third-party systems or remote calls.

Signature Calculation Method:

```text
Sort all params alphabetically (lowercase)
Concat with "&"
HMAC-SHA1(secretKey, encodedParams)
Base64 encoding
```

Server-side process：

```java
String requestSignature = params.get("signature");
String serverSignature = sign(requestParams);
compare
```

Access will be denied if there is a discrepancy.。

# 8. Asynchronous API Execution Flow（AsyncJobManager）  
Many APIs return a job ID immediately, which is then executed asynchronously by the backend.

Typical asynchronous APIs:

- createVM
- startVM
- rebootRouter
- migrateVolume

Workflow:

```java
BaseAsyncCmd.execute()
 → AsyncJobManager.submitAsyncJob()
 → Worker threads execute the actual logic
 → jobstatus=1 Represents completion
```

The background worker thread reads the database and updates the async_job result.

```java
job_result, job_status, job_instance_id
```
The UI uses:
```java
queryAsyncJobResult
```
to poll for task progress.

# 9. API Return Value (ResponseObject)

All response objects inherit from:

```java
BaseResponse
```
CloudStack uses Gson for serialization.

Response generation method:

```java
UserVmResponse resp = new UserVmResponse();
resp.setId(vm.getUuid());
resp.setName(vm.getDisplayName());
```

Final output: JSON。

# 10. API Exception Model
CloudStack uses a unified exception mechanism:：

```java
throw new ServerApiException(ApiErrorCode.PARAM_ERROR, "...") 
```

After ApiServer capture the exceptions, it is encapsulated as：
```json
{
  "errorresponse": {
    "errortext": "...",
    "errorcode": 431
  }
}
```

# 11. Summary

Key points of the API execution mechanism:

- A dynamic framework entirely based on **reflection + annotations**
- The Dispatcher binds API names to Java classes
- A highly flexible parameter parsing system
- A strict and multi-tiered API permission system
- An asynchronous framework ensures that heavy operations do not block
- Uniformly formatted JSON output
