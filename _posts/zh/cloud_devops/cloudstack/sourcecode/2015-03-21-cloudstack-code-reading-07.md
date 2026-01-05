---
layout: post
lang: zh
translations:
  en: /en/cloudstack-code-reading-07/
  zh: /zh/cloudstack-code-reading-07/
permalink: /zh/cloudstack-code-reading-07/
slug: "cloudstack-code-reading-07"
title: "CloudStack 代码阅读（七）—— 网络体系（NetworkGuru、NetworkElement、VR 服务链）"
date: "2015-03-21 13:34:12"
categories: ["CloudStack"]
tags: ["network", "networkguru", "networkelement", "vr", "source-analysis"]
draft: false
---
CloudStack 的网络模块是整个系统中最复杂的子系统之一。与一般 IaaS 架构不同，CloudStack 采用 **NetworkGuru → NetworkElement → VirtualRouter** 的三层结构，并通过 NetworkOrchestrator 串联网络生命周期，从 NIC 分配、VLAN 构建、流量隔离到虚拟路由器服务链（DHCP/DNS/LB/ACL/SourceNat）。

- NetworkOffering  
- NetworkGuru（网络架构师）  
- NetworkElement（网络功能组件）  
- NetworkOrchestrator（网络编排者）  
- NIC 生命周期  
- VR 服务链（DHCP/DNS/LB/ACL/SNAT）  
- 广播域、隔离方式、流量类型  

# 1. 网络模块源码结构总览

CloudStack 网络层主要包含以下路径：

```
server/src/com/cloud/network/
    ├── NetworkOrchestrator.java
    ├── NetworkManagerImpl.java
    ├── element/
    │     ├── VirtualRouterElement.java
    │     ├── NiciraNvpElement.java
    │     ├── OvsElement.java
    │     └── InternalLoadBalancerElement.java
    ├── guru/
    │     ├── PodBasedNetworkGuru.java
    │     ├── OvsGuestNetworkGuru.java
    │     ├── BridgeNetworkGuru.java
    │     └── ExternalGuestNetworkGuru.java
    └── dao/
network/src/org/apache/cloudstack/network/
    ├── NetworkModelImpl.java
    └── NetworkService.java
plugins/network/
    ├── virtualrouter/
    ├── nicira-nvp/
    └── midonet/
```

网络模块是一个极端插件化的体系，其中 Guru/Element 的组合决定了最终网络拓扑。

# 2. NetworkOffering：网络能力定义

NetworkOffering 决定了一个 Guest Network 拥有哪些能力，典型能力包括：

- DHCP  
- DNS  
- LB  
- SourceNat  
- StaticNat  
- Port Forwarding  
- Firewall  
- VPN  

源码路径：

```
com.cloud.offerings.NetworkOfferingVO
```

常见字段：

```java
private boolean isRedundantRouter;
private boolean isSharedSourceNat;
private boolean supportsDhcp;
private boolean supportsDns;
private TrafficType trafficType;
private GuestType guestType;
```

CloudStack 首先根据用户创建网络时选择的 NetworkOffering，在网络准备阶段决定：

- 使用哪个 NetworkGuru  
- 哪些 NetworkElement 会参与  
- 是否需要虚拟路由器（VR）  
- 该网络属于 Isolated / Shared 类型  

# 3. NetworkGuru：决定网络如何“定义”的核心

NetworkGuru 的作用是：

- 为 Guest Network 选择广播域（BroadcastDomain）  
- 分配 VLAN  
- 决定 NIC 的隔离方式  
- 决定是否需要 VR  

接口定义：

```
public interface NetworkGuru {
    Network design(NetworkOffering offering, DeploymentPlan plan, Network userSpec);
    Network implement(Network network, NetworkOffering offering, DeployDestination dest);
    NicProfile allocate(NicProfile nic, Network network);
    boolean trash(Network network);
}
```

CloudStack 4.2.2 中常见 Guru：

| Guru | 用途 |
|------|------|
| PodBasedNetworkGuru | 基于 Pod 的隔离网络 |
| BridgeNetworkGuru | Linux bridge 网络（KVM） |
| OvsGuestNetworkGuru | Open vSwitch 网络 |
| ExternalGuestNetworkGuru | 外部网络设备 |

以 **BridgeNetworkGuru** 为例（KVM 默认）：

源码片段：

```java
@Override
public Network design(NetworkOffering offering, DeploymentPlan plan, Network userSpecified, Account owner) {
    if (offering.getTrafficType() != TrafficType.Guest) return null;

    NetworkVO network = new NetworkVO();
    network.setBroadcastDomainType(BroadcastDomainType.Vlan);
    network.setNetworkOfferingId(offering.getId());
    return network;
}
```

### 3.1 Guru 的地位

Guru 决定了**网络结构本身**：

- 是 VLAN？VXLAN？GRE？  
- VLAN ID 如何选择？  
- NIC 接入哪个 bridge？  
- 是否需要 VR？

Guru 是 CloudStack 网络体系的最核心模块。

# 4. NetworkElement：负责具体网络功能的插件体系

NetworkElement 是“网络功能插件”，每个 Element 负责一部分功能，例如：

| Element | 功能 |
|---------|------|
| VirtualRouterElement | DHCP/DNS/LB/ACL/SNAT |
| NiciraNvpElement | OpenFlow/VXLAN/SDN |
| OvsElement | OVS 网络支持 |
| InternalLoadBalancerElement | LB 功能 |
| VpnElement | Site-to-Site VPN |

接口定义：

```java
public interface NetworkElement {
    boolean implement(Network network, NetworkOffering offering);
    boolean prepare(Network network, NicProfile nic);
    boolean release(Network network, NicProfile nic);
}
```

关键逻辑：

- NetworkGuru 负责“架构”  
- NetworkElement 负责“功能”  

例如 VirtualRouterElement 实现 DHCP/DNS：

```java
@Override
public boolean implement(Network network, NetworkOffering offering) {
    deployVirtualRouter(network);
    return true;
}
```

# 5. NetworkOrchestrator：网络生命周期调度者

网络操作都经过：

```
NetworkOrchestrator
```

关键流程：

```
allocateNetwork()
implementNetwork()
allocateNIC()
prepareNTWK()
releaseNTWK()
```

关键代码：

```java
public Network implementNetwork(long networkId, DeployDestination dest) {
    NetworkVO network = _networkDao.findById(networkId);

    NetworkGuru guru = _networkGurus.get(network.getGuruName());
    guru.implement(network, offering, dest);

    for (NetworkElement element : networkElements) {
        if (element.isEnabledFor(network)) {
            element.implement(network, offering);
        }
    }
    return network;
}
```

### NetworkOrchestrator 的意义：

- 从多个 Guru / Element 选择适合网络
- 按顺序执行网络构建流程
- 管理 NIC 生命周期
- 填装 VR、LB、ACL 等组件

# 6. NIC 生命周期（分配、实现、清理）

NIC 是 Network → VM 的绑定对象，定义在：

```
com.cloud.vm.NicVO
```

NIC 的分配流程：

```
allocate(network)
 → assign IP
 → create NicVO
 → allocateNicProfile
```

### NIC 创建流程：

```java
NicVO nic = new NicVO(networkId, vmId, broadcastUri, isolationUri);
nic.setReservationId(UUID.randomUUID().toString());
_nicDao.persist(nic);
```

### NIC 启动准备：

在 VM 启动前：

```
NetworkOrchestrator.prepareNic()
 → Guru.allocate()
 → Element.prepare()
```

# 7. 广播域（BroadcastDomain）与隔离方式（IsolationMethod）

BroadcastDomainType 代表网络底层结构：

- VLAN：`vlan://123`  
- VXLAN：`vxlan://5001`  
- GRE：`gre://100`  
- Native：裸网  
- LinkLocal：VR 专用网络  

定义在：

```
BroadcastDomainType.java
```

Sample:

```java
if (uri.getScheme().equals("vlan")) return BroadcastDomainType.Vlan;
```

隔离方式定义 VM/NIC 在链路中如何隔离：

- VLAN  
- VXLAN  
- GRE  
- STT  
- L3 隔离（NICIRA）

Guru 根据 offering 选择隔离方式。

# 8. Virtual Router（VR）在网络体系中的角色：服务链核心

VR 是 CloudStack Guest Network 中最重要的组件，提供：

- DHCP  
- DNS  
- LB  
- Source NAT  
- Port Forwarding  
- VPN  
- ACL / Firewall  

VR 在网络编排中的角色：

```
NetworkGuru 决定是否需要 VR
 → NetworkOrchestrator 调用 VirtualRouterElement
    → RouterManager.deployRouter()
```

源码位置：

```
plugins/network/virtualrouter/
```

VR 部署流程：

```java
public DomainRouterVO deployRouter(Network guestNetwork) {
    DomainRouterVO router = new DomainRouterVO(...);
    routerDao.persist(router);
    startRouter(router);
    return router;
}
```

# 9. VR 服务链源码解剖：DHCP / DNS / LB / SNAT

VR 内部脚本位于：

```
/opt/cloud/bin/
```

VR 服务启停通过 ConfigDrive 或脚本完成。

VirtualRouterElement:

```java
@Override
public boolean implement(Network network, NetworkOffering offering) {
    Commands cmds = new Commands(new SetDhcpCofigCommand(...));
    sendCommandsToVR(router, cmds);
    return true;
}
```

LB 功能：

```java
ApplyLoadBalancerRulesCommand cmd = new ApplyLoadBalancerRulesCommand(rules);
_commands.addCommand(cmd);
```

SNAT：

```java
SetSourceNatCommand cmd = new SetSourceNatCommand(ip, true);
```

VR 通过 AgentCommand 实际配置 iptables/dnsmasq/haproxy。

# 10. 网络准备与 VM 启动的联动关系

VM 启动前必须完成：

```
NetworkGuru.allocateNIC
 → NetworkElement.prepare
    → VR ready
 → create NicProfile
 → attach NIC to VM
```

VMStart 时序：

```
orchestrateDeployVM
 |
 +--> NetworkOrchestrator.prepare()
 |       |
 |       +--> allocateNIC()
 |       +--> implementNetwork()
 |       +--> prepareNic()
 |
 +--> VolumeManager.prepare()
 |
 +--> Guru.finalizeDeployment()
 |
 +--> agentMgr.send(StartCommand)
```

# 11. 常见网络失败点（源码级）

## 11.1 VLAN 分配失败

Guru 抛出：

```
Unable to find free VLAN
```

详见：

```
VlanDaoImpl.acquireVlan()
```

## 11.2 VR 启动失败

日志关键：

```
RouterManagerImpl.startRouter
```

## 11.3 NIC 创建失败

NetworkOrchestrator:

```
Unable to allocate nic profile
```

通常是 IP 池已满。

# 12. 小结

网络模块是 CloudStack 最强大的部分。  
其设计理念为：

- **Guru** 决定网络拓扑  
- **Element** 决定功能  
- **NetworkOrchestrator** 决定生命周期  
- **VR** 决定服务链  

