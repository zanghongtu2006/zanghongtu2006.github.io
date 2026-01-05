---
layout: post
lang: en
translations:
  en: /en/cloudstack-code-reading-09/
  zh: /zh/cloudstack-code-reading-09/
permalink: /en/cloudstack-code-reading-09/
slug: "cloudstack-code-reading-09"
title: "CloudStack Code（9）—— Virtual Router VR Architecture and Implementation"
date: "2015-03-23 13:22:11"
categories: ["CloudStack"]
tags: ["vr", "virtualrouter", "network", "source-analysis"]
draft: false
---
Virtual Router (VR) is a core component of the CloudStack network architecture. VR performs services such as DHCP, DNS, LB, ACL, Port Forwarding, VPN, and Source NAT.

# 1. VR's Role: CloudStack Control Plane Device

VR is a special System VM that behaves almost like a virtualized network device:

- Based on the VyOS/dnsmasq/haproxy scripting system
- Driven by Config Commands
- Deployed and managed by the Management Server calling RouterManager
- A network control node belonging to the Guest Network

# 2. VR-related source code structure

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

Almost all of VR's functionality is embodied in these Commands.

# 3. VR Lifecycle: From Creation to Operation

VR Creation Process Call Chain:

```
implementNetwork()
 → VirtualRouterElement.implement()
    → RouterManagerImpl.deployRouter()
        → VirtualRouterManagerImpl.start()
```

Key Logic:

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

# 4. VirtualRouterGuru: Determining How VR Runs

The Guru determines the VR Hypervisor configuration:

- NIC layout
- CPU/Memory
- Boot parameters
- DomainRouterVO build

Key logic:

```java
@Override
public boolean finalizeVirtualMachineProfile(VirtualMachineProfile profile, DeployDestination dest) {
    profile.setConfigDriveOnSystemVm(true);
    return true;
}
```

Guru decides whether VR uses multiple NICs:

```
Control NIC（CloudStack MGMT 通道）
Public NIC（Source NAT / LB）
Guest NIC（VM 所在网段）
```

# 5. VR Internal Network Topology

```
              +----------------+
              |   VirtualRouter |
              +----------------+
                 |      |      |
   CONTROL ------+      |      +----- PUBLIC (SourceNat)
                        |
                        +----- GUEST（DHCP/DNS/LB）
```

VR is the gateway for the Guest Network.

# 6. VR Service Chain (DHCP/DNS/LB/ACL/SNAT) Source Code Analysis

CloudStack breaks down network services into independent command groups:

| Function | Command Type |
|------|--------------|
| DHCP | SetDhcpConfigCommand |
| DNS | SetDnsConfigCommand |
| LB | LoadBalancerConfigCommand |
| Firewall | SetFirewallRulesCommand |
| NAT | SetSourceNatCommand |
| ACL | SetNetworkACLCommand |

Each Element (e.g., VirtualRouterElement) is responsible for distributing these commands to the VR.

For example, configuring DHCP:
```java
SetDhcpConfigCommand cmd = new SetDhcpConfigCommand(dhcpEntries);
```

RouterManagerImpl:

```java
Commands cmds = new Commands(cmd);
_answer = _agentMgr.send(vmHostId, cmds);
```

VR performs configuration via an internal script `/opt/cloud/bin/*`.

# 7. VR Configuration Command Generation Process

Taking DHCP as an example:

```
NetworkOrchestrator.prepare()
 → VirtualRouterElement.prepare()
   → RouterManagerImpl.applyDhcpEntries()
       → CommandSetupHelper.createDhcpConfig()
           → new SetDhcpConfigCommand()
```

DNS configuration links:

```java
SetDnsConfigCommand dnsCmd = new SetDnsConfigCommand(addresses);
```

LB configuration links:

```java
ApplyLoadBalancerRulesCommand cmd = new ApplyLoadBalancerRulesCommand(rules);
```

# 8. VR's System VM Architecture

VR is essentially a special System VM running on a hypervisor.

Its image system:

```
/usr/share/cloudstack-common/vms/systemvm.iso
```

Internal Components:

- dnsmasq: DHCP/DNS
- haproxy: Load Balancing
- iptables: SNAT/Firewall
- ipset: ACL
- racoon: VPN (older version)
- Command Interpreter: `/opt/cloud/bin/*`

VR communicates with CloudStack via SSH; the Agent is responsible for executing commands.

# 9. VR Startup Process

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

StartCommand is crucial for launching VR.

# 10. StartCommand: VR Startup Core Command

StartCommand includes:
```java
public class StartCommand extends Command {
    HashMap<String, String> bootArgs;
    List<DiskTO> disks;
    NicTO[] nics;
}
```

Upon receiving the StartCommand by the Agent:

- KVM → Generate XML → Call libvirt → Start
- Xen → Call xenapi.createVM/start
- VMware → Call vCenter API

After VR starts, the Management Server continues to push network service configuration commands.
# 11. VR Configuration Command Pipeline

All VR configuration commands follow a consistent pattern:
```
routerMgr.configureXxx()
 → CommandSetupHelper.createXxxCommand()
 → new Commands(cmd)
 → _agentMgr.send(routerHostId, cmds)
 → VR execution script update configuration
```

Example:

```java
CommandSetupHelper.createFirewallRules()  
SetFirewallRulesCommand cmd = new SetFirewallRulesCommand(rules);
```

VR Internal script:

```
/opt/cloud/bin/configure_firewall.sh
```

# 12. VR Multi-Service Combination Scheduling (NetworkElement Order)

The VR Element will: in implementNetwork()

```
VirtualRouterElement.isEnabledFor()
 → element.implement(network)
 → element.prepare(network, nic)
```

Orderly execution of services:

1. DHCP  
2. DNS  
3. LB  
4. Firewall  
5. VPN  
6. ACL  
7. NAT  

# 13. VR Health Check and Restart

VR Check Cycle:

```
router_health_check_timer
```

RouterManagerImpl:

```java
if (!router.isRunning()) {
    restartRouter(router.getId());
}
```

RestartRouter:

```
stopRouter()
startRouter()
```

# 14. Common VR Troubleshooting Points and Debugging Methods (Source Code Level)

## 14.1 VR Startup Failure

Log:

```
management-server.log
agent.log
```

Typical errors:

```
StartCommand failed: cannot create domain
```

Causes:

- Corrupted Template
- Host Libvirt Issue
- Incomplete Router Image

## 14.2 DHCP is not working.

View VR in-game logs:
```
/var/log/messages
dnsmasq.conf
```

## 14.3 LB is not working

View Logs:

```
/etc/haproxy/haproxy.cfg
```

# 15. Summary

VR is the core of the CloudStack network architecture:

- Manages services such as DHCP/DNS/LB/SNAT/ACL/VPN
- Accepts multiple command configurations
- Driven by a combination of RouterManager/Guru/Element/Orchestrator
- Actual operation is performed by VR's internal scripts
