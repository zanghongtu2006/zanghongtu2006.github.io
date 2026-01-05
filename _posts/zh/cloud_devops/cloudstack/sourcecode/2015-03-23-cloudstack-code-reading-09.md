---
layout: post
lang: zh
translations:
  en: /en/cloudstack-code-reading-09/
  zh: /zh/cloudstack-code-reading-09/
permalink: /zh/cloudstack-code-reading-09/
slug: "cloudstack-code-reading-09"
title: "CloudStack 代码阅读（九）—— 虚拟路由器 VR 架构与实现"
date: "2015-03-23 13:22:11"
categories: ["CloudStack"]
tags: ["vr", "virtualrouter", "network", "source-analysis"]
draft: false
---
Virtual Router（VR）是 CloudStack 网络体系的核心组件。VR 执行 DHCP、DNS、LB、ACL、Port Forwarding、VPN、Source NAT 等服务。  

# 1. VR 的定位：CloudStack 控制面设备

VR 是一个特殊的 System VM，行为接近一台虚拟化的网络设备：

- 基于 VyOS/dnsmasq/haproxy 脚本体系
- 通过 Config Commands 驱动
- 由 Management Server 调用 RouterManager 部署和管理
- 属于 Guest Network 的网络控制节点

# 2. VR 相关源码结构

```
plugins/network/virtualrouter/
    ├── VirtualRouterElement.java
    ├── VirtualRouterManagerImpl.java
    ├── VirtualRouterGuru.java
    ├── router/
    │     ├── RouterManagerImpl.java
    │     ├── CommandSetupHelper.java
    │     └── VirtualMachineManager
    └── commands/
           ├── SetNetworkACLCommand.java
           ├── SetStaticNatRulesCommand.java
           ├── SetPortForwardingRulesCommand.java
           ├── SetDhcpConfigCommand.java
           ├── SetDnsConfigCommand.java
           ├── LoadBalancerConfigCommand.java
```

VR 的功能几乎全部在这些 Commands 中体现。

# 3. VR 生命周期：从创建到运行

VR 创建流程调用链：

```
implementNetwork()
 → VirtualRouterElement.implement()
    → RouterManagerImpl.deployRouter()
        → VirtualRouterManagerImpl.start()
```

关键逻辑：

## 3.1 VirtualRouterElement.implement()

```java
@Override
public boolean implement(Network network, NetworkOffering offering) {
    DeployDestination dest = planDeployment(network);
    DomainRouterVO router = _routerMgr.deployRouter(network, dest);
    return router != null;
}
```

## 3.2 RouterManagerImpl.deployRouter()

```java
DomainRouterVO router = new DomainRouterVO(...);
router = _routerDao.persist(router);
startRouter(router);
```

# 4. VirtualRouterGuru：决定 VR 如何运行

Guru 决定 VR 的 Hypervisor 配置：

- NIC 布局  
- CPU/Memory  
- 启动参数  
- DomainRouterVO 构建

关键逻辑：

```java
@Override
public boolean finalizeVirtualMachineProfile(VirtualMachineProfile profile, DeployDestination dest) {
    profile.setConfigDriveOnSystemVm(true);
    return true;
}
```

Guru 决定 VR 是否使用多个 NIC：

```
Control NIC（CloudStack MGMT 通道）
Public NIC（Source NAT / LB）
Guest NIC（VM 所在网段）
```

# 5. VR 内部网络拓扑

```
              +----------------+
              |   VirtualRouter |
              +----------------+
                 |      |      |
   CONTROL ------+      |      +----- PUBLIC (SourceNat)
                        |
                        +----- GUEST（DHCP/DNS/LB）
```

VR 是 Guest Network 的网关。

# 6. VR 服务链（DHCP/DNS/LB/ACL/SNAT）源码级解析

CloudStack 将网络服务拆解为独立指令组：

| 功能 | Command 类型 |
|------|--------------|
| DHCP | SetDhcpConfigCommand |
| DNS | SetDnsConfigCommand |
| LB | LoadBalancerConfigCommand |
| 防火墙 | SetFirewallRulesCommand |
| NAT | SetSourceNatCommand |
| ACL | SetNetworkACLCommand |

每个 Element（例如 VirtualRouterElement）负责把这些指令分发到 VR。

例如配置 DHCP：

```java
SetDhcpConfigCommand cmd = new SetDhcpConfigCommand(dhcpEntries);
```

RouterManagerImpl：

```java
Commands cmds = new Commands(cmd);
_answer = _agentMgr.send(vmHostId, cmds);
```

VR 在内部脚本 `/opt/cloud/bin/*` 执行配置。

# 7. VR 配置命令的生成流程

以 DHCP 为例：

```
NetworkOrchestrator.prepare()
 → VirtualRouterElement.prepare()
   → RouterManagerImpl.applyDhcpEntries()
       → CommandSetupHelper.createDhcpConfig()
           → new SetDhcpConfigCommand()
```

DNS 配置链路类似：

```java
SetDnsConfigCommand dnsCmd = new SetDnsConfigCommand(addresses);
```

LB 配置链路：

```java
ApplyLoadBalancerRulesCommand cmd = new ApplyLoadBalancerRulesCommand(rules);
```

# 8. VR 的 System VM 架构

VR 本质上是一台特殊的 System VM，运行在 Hypervisor 上。

其镜像系统：

```
/usr/share/cloudstack-common/vms/systemvm.iso
```

内部组件：

- dnsmasq：DHCP/DNS  
- haproxy：Load Balancing  
- iptables：SNAT/Firewall  
- ipset：ACL  
- racoon：VPN（旧版本）  
- 命令解释器：`/opt/cloud/bin/*`  

VR 通过 SSH 与 CloudStack 通信，Agent 负责执行命令。

# 9. VR 的启动流程

```
deployRouter()
  |
  v
persist routerVO
  |
  v
startRouter(router)
  |
  +--> VirtualMachineManager.start()
  |       |
  |       +--> orchestrateStartVM()
  |               |
  |               +--> allocate NICs
  |               +--> send(StartCommand)
  |
  v
router running
```

StartCommand 是 VR 启动的关键。

# 10. StartCommand：VR 启动核心指令

StartCommand 包含：

```java
public class StartCommand extends Command {
    HashMap<String, String> bootArgs;
    List<DiskTO> disks;
    NicTO[] nics;
}
```

StartCommand 由 Agent 收到后：

- KVM → 生成 XML → 调用 libvirt → 启动  
- Xen → 调用 xenapi.createVM/start  
- VMware → 调用 vcenter API  

VR 启动后，Management Server 继续推送网络服务配置指令。

# 11. VR 配置指令管线（Config Pipeline）

所有 VR 配置指令遵循一致模式：

```
routerMgr.configureXxx()
 → CommandSetupHelper.createXxxCommand()
 → new Commands(cmd)
 → _agentMgr.send(routerHostId, cmds)
 → VR 执行脚本更新配置
```

例如：

```java
CommandSetupHelper.createFirewallRules()  
SetFirewallRulesCommand cmd = new SetFirewallRulesCommand(rules);
```

VR 内部脚本：

```
/opt/cloud/bin/configure_firewall.sh
```

# 12. VR 的多服务组合调度（NetworkElement 顺序）

VR Element 在 implementNetwork() 中会：

```
VirtualRouterElement.isEnabledFor()
 → element.implement(network)
 → element.prepare(network, nic)
```

有序执行服务：

1. DHCP  
2. DNS  
3. LB  
4. Firewall  
5. VPN  
6. ACL  
7. NAT  

# 13. VR 健康检查与重启

VR 检查周期：

```
router_health_check_timer
```

RouterManagerImpl：

```java
if (!router.isRunning()) {
    restartRouter(router.getId());
}
```

RestartRouter：

```
stopRouter()
startRouter()
```

# 14. VR 常见故障点与调试方法（源码级）

## 14.1 VR 启动失败

日志：

```
management-server.log
agent.log
```

典型错误：

```
StartCommand failed: cannot create domain
```

原因：

- Template 损坏  
- 主机 Libvirt 问题  
- Router 镜像不完整  

## 14.2 DHCP 不生效

查看 VR 内日志：

```
/var/log/messages
dnsmasq.conf
```

## 14.3 LB 不生效

查看：

```
/etc/haproxy/haproxy.cfg
```

# 15. 总结

VR 是 CloudStack 网络体系的核心：

- 管理 DHCP/DNS/LB/SNAT/ACL/VPN 等服务  
- 接受多个 Commands 配置  
- 通过 RouterManager/Guru/Element/Orchestrator 组合驱动  
- 实际工作由 VR 内部脚本完成  
