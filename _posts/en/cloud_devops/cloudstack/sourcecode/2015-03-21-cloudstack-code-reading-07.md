---
layout: post
lang: en
translations:
  en: /en/cloudstack-code-reading-07/
  zh: /zh/cloudstack-code-reading-07/
permalink: /en/cloudstack-code-reading-07/
slug: "cloudstack-code-reading-07"
title: "CloudStack Code（7）—— Network architecture (NetworkGuru, NetworkElement, VR service chain)"
date: "2015-03-21 13:34:12"
categories: ["CloudStack"]
tags: ["network", "networkguru", "networkelement", "vr", "source-analysis"]
draft: false
---
The network module in CloudStack is one of the most complex subsystems in the entire system.

Unlike typical IaaS architectures, CloudStack employs a three-layer structure: **NetworkGuru → NetworkElement → VirtualRouter**, and uses NetworkOrchestrator to orchestrate the network lifecycle, from NIC allocation, VLAN construction, and traffic isolation to the virtual router service chain (DHCP/DNS/LB/ACL/SourceNAT).

- NetworkOffering
- NetworkGuru (Network Architect)
- NetworkElement (Network Functional Component)
- NetworkOrchestrator (Network Orchestrator)
- NIC Lifecycle
- VR Service Chain (DHCP/DNS/LB/ACL/SNAT)
- Broadcast Domain, Isolation Method, Traffic Type

# 1. 网络模块源码结构总览

The CloudStack network layer mainly includes the following paths:

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

The network module is an extremely pluggable system, where the combination of Guru/Element determines the final network topology.

# 2. NetworkOffering: Definition of Network Capabilities

NetworkOffering determines the capabilities of a Guest Network, typically including:

- DHCP  
- DNS  
- LB  
- SourceNat  
- StaticNat  
- Port Forwarding  
- Firewall  
- VPN  

Source code path:

```
com.cloud.offerings.NetworkOfferingVO
```

Common fields:

```java
private boolean isRedundantRouter;
private boolean isSharedSourceNat;
private boolean supportsDhcp;
private boolean supportsDns;
private TrafficType trafficType;
private GuestType guestType;
```

CloudStack first determines the following during the network preparation phase based on the NetworkOffering selected by the user when creating the network:

- Which NetworkGuru to use
- Which NetworkElements will participate
- Whether a Virtual Router (VR) is needed
- Whether the network is of Isolated/Shared type

# 3. NetworkGuru: The core that determines how a network is "defined"

The functions of NetworkGuru are:

- Selecting the broadcast domain for the Guest Network
- Assigning VLANs
- Determining the isolation method for the NIC
- Determining whether a VR (Virtual Reality) is needed

Interface Definition:

```
public interface NetworkGuru {
    Network design(NetworkOffering offering, DeploymentPlan plan, Network userSpec);
    Network implement(Network network, NetworkOffering offering, DeployDestination dest);
    NicProfile allocate(NicProfile nic, Network network);
    boolean trash(Network network);
}
```

Common Guru protocols in CloudStack 4.2.2:

| Guru | Purpose |
|------|------|
| PodBasedNetworkGuru | Pod-based isolated network |
| BridgeNetworkGuru | Linux bridge network (KVM) |
| OvsGuestNetworkGuru | Open vSwitch network |
| ExternalGuestNetworkGuru | External network device |

Taking **BridgeNetworkGuru** as an example (KVM default):

Source code:

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

### 3.1 Guru's Role

Guru determines the **network structure itself**:

- Is it VLAN? VXLAN? GRE?
- How to choose the VLAN ID?
- Which bridge does the NIC connect to?
- Is VR needed?

Guru is the core module of the CloudStack network architecture.

# 4. NetworkElement: A plugin system responsible for specific network functions

NetworkElement is a "network function plugin," with each Element responsible for a specific function, such as:

| Element | Function |
|---------|------|
| VirtualRouterElement | DHCP/DNS/LB/ACL/SNAT |
| NiciraNvpElement | OpenFlow/VXLAN/SDN |
| OvsElement | OVS Network Support |
| InternalLoadBalancerElement | LB Function |
| VpnElement | Site-to-Site VPN |

Interface Definition:

```java
public interface NetworkElement {
    boolean implement(Network network, NetworkOffering offering);
    boolean prepare(Network network, NicProfile nic);
    boolean release(Network network, NicProfile nic);
}
```

Key Logic:  
- NetworkGuru is responsible for the "architecture".
- NetworkElement is responsible for the "functionality".

For example, VirtualRouterElement implements DHCP/DNS:

```java
@Override
public boolean implement(Network network, NetworkOffering offering) {
    deployVirtualRouter(network);
    return true;
}
```

# 5. NetworkOrchestrator: The network lifecycle scheduler

Network operations all go through:

```
NetworkOrchestrator
```

Key Process:

```
allocateNetwork()
implementNetwork()
allocateNIC()
prepareNTWK()
releaseNTWK()
```

Key source code:

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

### The significance of NetworkOrchestrator:

- Select the appropriate network from multiple Guru/Element options
- Execute the network build process sequentially
- Manage the NIC lifecycle
- Load components such as VR, LB, and ACL

# 6. NIC Lifecycle (Assignment, Implementation, Cleanup)

A NIC is a binding object between a Network and a Virtual Machine (VM), defined in:

```
com.cloud.vm.NicVO
```

NIC allocation process:

```
allocate(network)
 → assign IP
 → create NicVO
 → allocateNicProfile
```

### NIC Creation Process:

```java
NicVO nic = new NicVO(networkId, vmId, broadcastUri, isolationUri);
nic.setReservationId(UUID.randomUUID().toString());
_nicDao.persist(nic);
```

### NIC Boot Preparation:
Before VM Boot:

```
NetworkOrchestrator.prepareNic()
 → Guru.allocate()
 → Element.prepare()
```

# 7.  Broadcast Domain and Isolation Method

BroadcastDomainType represents the underlying network structure:

- VLAN: `vlan://123`
- VXLAN: `vxlan://5001`
- GRE: `gre://100`
- Native: Bare network
- LinkLocal: VR private network

Defined in:

```
BroadcastDomainType.java
```

Sample:

```java
if (uri.getScheme().equals("vlan")) return BroadcastDomainType.Vlan;
```

Isolation methods define how VMs/NICs are isolated in a link:

- VLAN
- VXLAN
- GRE
- STT
- L3 Isolation (NICIRA)

Guru selects the isolation method based on the offering.

# 8. Virtual Router (VR) Role in Network Architecture: Core of the Service Chain

VR is the most important component in the CloudStack Guest Network, providing:

- DHCP
- DNS
- Load Balancing
- Source NAT
- Port Forwarding
- VPN
- ACL / Firewall

VR's Role in Network Orchestration:

```
NetworkGuru determines whether VR is needed
 → NetworkOrchestrator calls VirtualRouterElement
    → RouterManager.deployRouter()
```

souce code:

```
plugins/network/virtualrouter/
```

VR Deployment Process:

```java
public DomainRouterVO deployRouter(Network guestNetwork) {
    DomainRouterVO router = new DomainRouterVO(...);
    routerDao.persist(router);
    startRouter(router);
    return router;
}
```

# 9. VR Service Chain Source Code Analysis: DHCP / DNS / LB / SNAT

VR internal scripts are located at:

```
/opt/cloud/bin/

```
VR service startup and shutdown are accomplished via ConfigDrive or scripts.  
VirtualRouterElement:

```java
@Override
public boolean implement(Network network, NetworkOffering offering) {
    Commands cmds = new Commands(new SetDhcpCofigCommand(...));
    sendCommandsToVR(router, cmds);
    return true;
}
```

LB:

```java
ApplyLoadBalancerRulesCommand cmd = new ApplyLoadBalancerRulesCommand(rules);
_commands.addCommand(cmd);
```

SNAT:

```java
SetSourceNatCommand cmd = new SetSourceNatCommand(ip, true);
```

VR uses AgentCommand to actually configure iptables/dnsmasq/haproxy.

# 10. The Relationship Between Network Preparation and VM Startup

The following must be completed before VM startup:

```
NetworkGuru.allocateNIC
 → NetworkElement.prepare
    → VR ready
 → create NicProfile
 → attach NIC to VM
```

VMStart timing line:

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

# 11. Common Network Failure Points (Source Code Level)

## 11.1 VLAN Assignment Failure

Guru throws:

```
Unable to find free VLAN
```

See Details:

```
VlanDaoImpl.acquireVlan()
```

## 11.2 VR failed to start

Log keywords:

```
RouterManagerImpl.startRouter
```

## 11.3 NIC creation failed.

NetworkOrchestrator:

```
Unable to allocate nic profile
```

This usually indicates that the IP pool is full.

# 12. Summary

The network module is the most powerful part of CloudStack.

Its design philosophy is as follows:

- **Guru** determines the network topology
- **Element** determines functionality
- **NetworkOrchestrator** determines the lifecycle
- **VR** determines the service chain
