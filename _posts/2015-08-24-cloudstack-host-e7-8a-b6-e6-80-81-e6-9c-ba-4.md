---
title: "CloudStack Host 状态机 (4)"
date: "2015-08-24 11:15:17"
slug: "cloudstack-host-e7-8a-b6-e6-80-81-e6-9c-ba-4"
layout: "post"
categories: ["CloudStack"]
tags: ["CloudStack", "host", "状态机"]
---
书接上文：[CloudStack Host 状态机 (3)](http://www.chinacloudly.com/cloudstack-host-%e7%8a%b6%e6%80%81%e6%9c%ba-3/)
状态机初始状态为**null**或***Creating***，没有任何Event可以把状态修改回初始状态。
最终状态为***Removed***，此时该状态不接受任何Event。
异常状态为***Alert***，***Error***。
中间状态为***Up***,***Down ,Connecting, Disconnected, Rebalancing***。
**null**只能接受***AgentConnected***，***Error***只能接受***AgentConnected***。
 
[codesyntax lang="java"]

```
s_fsm.addTransition(null, Event.AgentConnected, Status.Connecting);
s_fsm.addTransition(Status.Creating, Event.AgentConnected, Status.Connecting);
```

[/codesyntax]
 
创建过程：如果初始状态为null或Creating，接到Event为AgentConnected，状态变为Connecting，初始状态为null只能接受AgentConnected
[codesyntax lang="java"]

```
s_fsm.addTransition(Status.Creating, Event.Error, Status.Error);
```

[/codesyntax]
 
创建过程：如果初始状态为Creating，接到Event为Error，状态变为Error
 
[codesyntax lang="java"]

```
s_fsm.addTransition(Status.Connecting, Event.AgentConnected, Status.Connecting);
s_fsm.addTransition(Status.Connecting, Event.Ready, Status.Up);
s_fsm.addTransition(Status.Connecting, Event.PingTimeout, Status.Alert);
s_fsm.addTransition(Status.Connecting, Event.ShutdownRequested, Status.Disconnected);
s_fsm.addTransition(Status.Connecting, Event.HostDown, Status.Alert);
s_fsm.addTransition(Status.Connecting, Event.Ping, Status.Connecting);
s_fsm.addTransition(Status.Connecting, Event.ManagementServerDown, Status.Disconnected);
s_fsm.addTransition(Status.Connecting, Event.AgentDisconnected, Status.Alert);
```

[/codesyntax]
 
连接过程：根据接到的Event来判断是否成功并把状态置为相应状态。***Connecting***不会转变为***Error******，******Rebalancing******，******Removed***。
 
[codesyntax lang="java"]

```
s_fsm.addTransition(Status.Up, Event.PingTimeout, Status.Alert);
s_fsm.addTransition(Status.Up, Event.AgentDisconnected, Status.Alert);
s_fsm.addTransition(Status.Up, Event.ShutdownRequested, Status.Disconnected);
s_fsm.addTransition(Status.Up, Event.HostDown, Status.Down);
s_fsm.addTransition(Status.Up, Event.Ping, Status.Up);
s_fsm.addTransition(Status.Up, Event.AgentConnected, Status.Connecting);
s_fsm.addTransition(Status.Up, Event.ManagementServerDown, Status.Disconnected);
s_fsm.addTransition(Status.Up, Event.StartAgentRebalance, Status.Rebalancing);
s_fsm.addTransition(Status.Up, Event.Remove, Status.Removed);
```

[/codesyntax]
 
***Up***为正常连接状态，会随着接受到各种事件，转变为其它中间状态。
 
[codesyntax lang="java"]

```
s_fsm.addTransition(Status.Disconnected, Event.PingTimeout, Status.Alert);
s_fsm.addTransition(Status.Disconnected, Event.AgentConnected, Status.Connecting);
s_fsm.addTransition(Status.Disconnected, Event.Ping, Status.Up);
s_fsm.addTransition(Status.Disconnected, Event.HostDown, Status.Down);
s_fsm.addTransition(Status.Disconnected, Event.ManagementServerDown, Status.Disconnected);
s_fsm.addTransition(Status.Disconnected, Event.WaitedTooLong, Status.Alert);
s_fsm.addTransition(Status.Disconnected, Event.Remove, Status.Removed);
s_fsm.addTransition(Status.Disconnected, Event.AgentDisconnected, Status.Disconnected);
```

[/codesyntax]
 
***Disconnected***为连接断开，Ping失败，监控线程发现断开，都可能变为该状态，该状态接受各种Event也会变为相应下一步状态。
 
[codesyntax lang="java"]

```
s_fsm.addTransition(Status.Down, Event.AgentConnected, Status.Connecting);
s_fsm.addTransition(Status.Down, Event.Remove, Status.Removed);
s_fsm.addTransition(Status.Down, Event.ManagementServerDown, Status.Down);
s_fsm.addTransition(Status.Down, Event.AgentDisconnected, Status.Down);
s_fsm.addTransition(Status.Down, Event.PingTimeout, Status.Down);
```

[/codesyntax]
 
***Down***为主机或Host关机状态，Agent连接成功，会变为Connecting进入下一步状态机。
 
[codesyntax lang="java"]

```
s_fsm.addTransition(Status.Alert, Event.AgentConnected, Status.Connecting);
s_fsm.addTransition(Status.Alert, Event.Ping, Status.Up);
s_fsm.addTransition(Status.Alert, Event.Remove, Status.Removed);
s_fsm.addTransition(Status.Alert, Event.ManagementServerDown, Status.Alert);
s_fsm.addTransition(Status.Alert, Event.AgentDisconnected, Status.Alert);
s_fsm.addTransition(Status.Alert, Event.ShutdownRequested, Status.Disconnected);
```

[/codesyntax]
 
***Alert***主机状态发生异常而进行重启（丢失主存储）或断网，都可能导致Alert状态，随后Agent连接则重新变为Connecting等状态。
 
[codesyntax lang="java"]

```
s_fsm.addTransition(Status.Rebalancing, Event.RebalanceFailed, Status.Disconnected);
s_fsm.addTransition(Status.Rebalancing, Event.RebalanceCompleted, Status.Connecting);
s_fsm.addTransition(Status.Rebalancing, Event.ManagementServerDown, Status.Disconnected);
s_fsm.addTransition(Status.Rebalancing, Event.AgentConnected, Status.Connecting);
s_fsm.addTransition(Status.Rebalancing, Event.AgentDisconnected, Status.Rebalancing);
```

[/codesyntax]
***Rebalancing***接受Rebalance调度任务之后的中间状态
[codesyntax lang="java"]

```
s_fsm.addTransition(Status.Error, Event.AgentConnected, Status.Connecting);
```

[/codesyntax]
任何状态改变流程出现InternalError都可能引发状态变为Error。
[![公众号二维码](/assets/images/2015/12/公众号二维码-150x150.jpg)](/assets/images/2015/12/公众号二维码.jpg)[![微博二维码](/assets/images/2014/07/微博二维码.png)](/assets/images/2014/07/微博二维码.png)
