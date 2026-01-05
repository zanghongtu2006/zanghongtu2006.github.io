---
layout: post
lang: zh
translations:
  en: /en/cloudstack-code-reading-02/
  zh: /zh/cloudstack-code-reading-02/
permalink: /zh/cloudstack-code-reading-02/
slug: "cloudstack-code-reading-02"
title: "CloudStack 代码阅读（二）—— API 框架执行机制（ApiServer、Dispatcher、Signature、Async）"
date: "2015-03-16 19:00:36"
categories: ["CloudStack"]
tags: ["api-framework", "apiserver", "dispatcher", "signature", "asyncjob"]
draft: false
---

本章深入分析 CloudStack API 的 **执行链路、反射机制、参数解析、权限系统、错误处理、签名校验、异步任务调度**。这是理解 CloudStack 管理平面的核心。

# 1. API 执行总览：从 HTTP 到内部命令  
API 调用执行流程如下：

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

CloudStack 的 API 不是 Restful，而是 **以 Command 为中心**：  
`?command=createVirtualMachine&serviceofferingid=...`

内部执行特点：

- 命令映射使用 **反射 + 注解扫描**
- 参数绑定使用 **注解 + 类型解析器**
- 调度调用使用 **Command Pattern**
- 大量 API 是异步的，通过 **AsyncJobManager** 管理
- 输出 JSON 使用 **Gson** 序列化

# 2. ApiServlet：所有 API 调用的入口  
ApiServlet 位于：

```text
server/src/com/cloud/api/ApiServlet.java
```

职责：

- 解析 GET/POST 请求
- 提取所有参数
- 调用 ApiServer
- 统一异常封装

伪代码：

```java
Map<String, String[]> params = request.getParameterMap();
String response = apiServer.handleRequest(params, responseType);
```

它不做任何业务逻辑，几乎完全代理给 ApiServer。

# 3. ApiServer：CloudStack API 的核心调度器  
ApiServer（`ApiServerImpl`）是 API 框架的大脑。

## 3.1 ApiServer 核心职责  
ApiServer 承担：

1. 参数预处理  
2. 签名校验  
3. 获取 Command 类  
4. 实例化 Command  
5. 参数绑定（反射）  
6. 权限校验  
7. 调用管理服务（Manager）  
8. 构造 ResponseObject  
9. JSON 序列化  

核心方法：

```java
String handleRequest(Map params, boolean isAsync)
```

## 3.2 ApiServer 如何找到某个 API Command？  
Command 注册逻辑在系统启动时扫描：

- `org.apache.cloudstack.api.command.user.*`
- `org.apache.cloudstack.api.command.admin.*`

凡是带有：

```java
@APICommand(name = "startVirtualMachine")
```

都会加入一个 Map：

```java
Map<String, Class<? extends BaseCmd>> s_cmds;
```

因此，API ≈ Java 类名的动态绑定系统。

# 4. ApiDispatcher：命令分发器  
Dispatcher 的作用：

- 根据 API 名（字符串）找到命令类
- 通过反射创建对象
- 调用 execute()

伪代码：

```java
Class cmdClass = s_cmds.get(commandName);
BaseCmd cmd = cmdClass.newInstance();
cmd.execute();
```

# 5. 参数解析机制（Parameter Annotations）  
每个 API 参数通过：

```java
@Parameter(name="id", type=CommandType.UUID, required=true)
```

声明。

API 参数解析流程：

1. ApiServer 从请求中找到与注解匹配的参数；
2. 根据 `CommandType` 做类型转换；
3. 如果是 UUID，则查询 DB 映射内部 ID（Long）；
4. 反射设置字段，例如：

```java
field.set(cmdInstance, convertedValue);
```

## 5.1 参数类型支持  
CloudStack 支持的类型：

- BOOLEAN  
- INTEGER  
- LONG  
- UUID → Long  
- LIST → List<String>  
- MAP → `LinkedHashMap<String, Object>`  

## 5.2 多参数逻辑  
例如：

```
ids=1,2,3
```

会解析为 List。

# 6. 权限校验：Account / Domain / Role  
CloudStack 的权限体系基于三层结构：

| 层级 | 含义 |
|------|------|
| Account | 独立用户级别 |
| Domain | 管理子域的隔离 |
| Role | API 权限表 |

权限检查分两部分：

## 6.1 APICommand 注解权限  
通过：

```
@APICommand(authorized = {RoleType.Admin})
```

限制调用者角色。

## 6.2 资源访问权限  
例如调用：

```
{id: VM_UUID}
```

ApiServer 会：

1. 将 UUID 转为内部 ID  
2. 检查资源 owner  
3. 使用 AccessControlService 验证用户对 VM 是否有权限  

核心方法：

```java
_accountMgr.checkAccess(caller, AccessType.UseEntry, true, vmObj);
```

这是 CloudStack 安全模型的核心。

# 7. 签名机制（API Key + Secret Key）  
CloudStack 支持“签名认证”，用于第三方系统或远程调用。

签名计算方式：

```text
Sort all params alphabetically (lowercase)
Concat with "&"
HMAC-SHA1(secretKey, encodedParams)
Base64 encoding
```

服务端流程：

```java
String requestSignature = params.get("signature");
String serverSignature = sign(requestParams);
compare
```

如果不一致则拒绝访问。

# 8. 异步 API 执行流程（AsyncJobManager）  
许多 API 会立即返回 jobid，由后端异步执行。

典型异步 API：

- createVM
- startVM
- rebootRouter
- migrateVolume

流程：

```java
BaseAsyncCmd.execute()
 → AsyncJobManager.submitAsyncJob()
 → 工作线程执行实际逻辑
 → jobstatus=1 代表完成
```

后台 worker 线程读取数据库，更新 async_job 结果：

```java
job_result, job_status, job_instance_id
```

UI 则通过：

```java
queryAsyncJobResult
```

轮询任务进度。

# 9. API 返回值（ResponseObject）  
所有响应对象继承：

```java
BaseResponse
```

CloudStack 使用 Gson 进行序列化。

Response 的生成方式：

```java
UserVmResponse resp = new UserVmResponse();
resp.setId(vm.getUuid());
resp.setName(vm.getDisplayName());
```

最终输出 JSON。

# 10. API 异常模型  
CloudStack 使用统一异常：

```java
throw new ServerApiException(ApiErrorCode.PARAM_ERROR, "...") 
```

ApiServer 捕获后封装为：

```json
{
  "errorresponse": {
    "errortext": "...",
    "errorcode": 431
  }
}
```

# 11. 小结  
API 执行机制的核心要点：

- 完全基于 **反射 + 注解** 的动态框架  
- Dispatcher 将 API 名与 Java 类绑定  
- 参数解析体系非常灵活  
- API 权限体系严格且多层级  
- 异步框架让重操作不会阻塞  
- JSON 输出统一格式化  
