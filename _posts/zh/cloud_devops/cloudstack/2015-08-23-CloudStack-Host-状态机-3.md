---
title: "CloudStack Host 状态机 (3)"
date: "2015-08-23 17:47:11"
slug: "cloudstack-host-e7-8a-b6-e6-80-81-e6-9c-ba-3"
layout: "post"
categories: ["CloudStack"]
tags: ["CloudStack", "host"]
---
书接上文：[CloudStack Host 状态机 (2)](http://www.chinacloudly.com/cloudstack-host-状态机-2)
前两篇文章中，分别介绍了Host Status的定义和Event 的定义，状态机的定义为： fromStatus -> 接收Event -> nextStatus。
host接到update命令的时候，获取当前状态(fromStatus)和事件(Event)，通过状态机(statusMachine)的定义，获取到下一个状态(nextStatus)，并更新到DB 中。
接下来看代码中状态机的定义，还是Status.java 文件：
[codesyntax lang="java"]

```
public enum Status {
    ......
    public Status getNextStatus(Event e) throws NoTransitionException {
        return s_fsm.getNextState(this, e);
    }

    public Status[] getFromStates(Event e) {
        List<Status> from = s_fsm.getFromStates(this, e);
        return from.toArray(new Status[from.size()]);
    }

    public Set<Event> getPossibleEvents() {
        return s_fsm.getPossibleEvents(this);
    }
    ......
    protected static final StateMachine2<Status, Event, Host> s_fsm = new StateMachine2<Status, Event, Host>();
    static {
        s_fsm.addTransition(null, Event.AgentConnected, Status.Connecting);
        s_fsm.addTransition(Status.Creating, Event.AgentConnected, Status.Connecting);
        s_fsm.addTransition(Status.Creating, Event.Error, Status.Error);
        s_fsm.addTransition(Status.Connecting, Event.AgentConnected, Status.Connecting);
        s_fsm.addTransition(Status.Connecting, Event.Ready, Status.Up);
        s_fsm.addTransition(Status.Connecting, Event.PingTimeout, Status.Alert);
        s_fsm.addTransition(Status.Connecting, Event.ShutdownRequested, Status.Disconnected);
        s_fsm.addTransition(Status.Connecting, Event.HostDown, Status.Alert);
        s_fsm.addTransition(Status.Connecting, Event.Ping, Status.Connecting);
        s_fsm.addTransition(Status.Connecting, Event.ManagementServerDown, Status.Disconnected);
        s_fsm.addTransition(Status.Connecting, Event.AgentDisconnected, Status.Alert);
        s_fsm.addTransition(Status.Up, Event.PingTimeout, Status.Alert);
        s_fsm.addTransition(Status.Up, Event.AgentDisconnected, Status.Alert);
        s_fsm.addTransition(Status.Up, Event.ShutdownRequested, Status.Disconnected);
        s_fsm.addTransition(Status.Up, Event.HostDown, Status.Down);
        s_fsm.addTransition(Status.Up, Event.Ping, Status.Up);
        s_fsm.addTransition(Status.Up, Event.AgentConnected, Status.Connecting);
        s_fsm.addTransition(Status.Up, Event.ManagementServerDown, Status.Disconnected);
        s_fsm.addTransition(Status.Up, Event.StartAgentRebalance, Status.Rebalancing);
        s_fsm.addTransition(Status.Up, Event.Remove, Status.Removed);
        s_fsm.addTransition(Status.Disconnected, Event.PingTimeout, Status.Alert);
        s_fsm.addTransition(Status.Disconnected, Event.AgentConnected, Status.Connecting);
        s_fsm.addTransition(Status.Disconnected, Event.Ping, Status.Up);
        s_fsm.addTransition(Status.Disconnected, Event.HostDown, Status.Down);
        s_fsm.addTransition(Status.Disconnected, Event.ManagementServerDown, Status.Disconnected);
        s_fsm.addTransition(Status.Disconnected, Event.WaitedTooLong, Status.Alert);
        s_fsm.addTransition(Status.Disconnected, Event.Remove, Status.Removed);
        s_fsm.addTransition(Status.Disconnected, Event.AgentDisconnected, Status.Disconnected);
        s_fsm.addTransition(Status.Down, Event.AgentConnected, Status.Connecting);
        s_fsm.addTransition(Status.Down, Event.Remove, Status.Removed);
        s_fsm.addTransition(Status.Down, Event.ManagementServerDown, Status.Down);
        s_fsm.addTransition(Status.Down, Event.AgentDisconnected, Status.Down);
        s_fsm.addTransition(Status.Down, Event.PingTimeout, Status.Down);
        s_fsm.addTransition(Status.Alert, Event.AgentConnected, Status.Connecting);
        s_fsm.addTransition(Status.Alert, Event.Ping, Status.Up);
        s_fsm.addTransition(Status.Alert, Event.Remove, Status.Removed);
        s_fsm.addTransition(Status.Alert, Event.ManagementServerDown, Status.Alert);
        s_fsm.addTransition(Status.Alert, Event.AgentDisconnected, Status.Alert);
        s_fsm.addTransition(Status.Alert, Event.ShutdownRequested, Status.Disconnected);
        s_fsm.addTransition(Status.Rebalancing, Event.RebalanceFailed, Status.Disconnected);
        s_fsm.addTransition(Status.Rebalancing, Event.RebalanceCompleted, Status.Connecting);
        s_fsm.addTransition(Status.Rebalancing, Event.ManagementServerDown, Status.Disconnected);
        s_fsm.addTransition(Status.Rebalancing, Event.AgentConnected, Status.Connecting);
        s_fsm.addTransition(Status.Rebalancing, Event.AgentDisconnected, Status.Rebalancing);
        s_fsm.addTransition(Status.Error, Event.AgentConnected, Status.Connecting);
    }
    ......
}
```

[/codesyntax]
本段代码中，实例化了一个StateMachine2 类，定义了Status的状态转变流程。和3个方法：getNextStatus，getFromStates，getPossibleEvents。
其中getFromStates暂时没有被调用。
getPossibleEvents：可能接收的Event，List的时候会调用到。
getNextStatus：获得下一个状态，状态改变主要通过该方法得到新的状态。
StateMachine2 类中有一个方法transitTo(V vo, E e, Object opaque, StateDao<S, E, V> dao)用于接收Event并更新状态。
主要由AgentManagerImpl类中的agentStatusTransitTo方法调用来更新host 的state状态。
调用者分为两种：1) 添加或删除主机、集群、二级存储；2) 定时任务，检查Agent连接状态和Rebalance
[![公众号二维码](/assets/images/2015/12/公众号二维码-150x150.jpg)](/assets/images/2015/12/公众号二维码.jpg)[![微博二维码](/assets/images/2014/07/微博二维码.png)](/assets/images/2014/07/微博二维码.png)
