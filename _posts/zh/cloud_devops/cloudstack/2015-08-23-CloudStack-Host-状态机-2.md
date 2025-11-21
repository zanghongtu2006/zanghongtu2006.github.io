---
title: "CloudStack Host 状态机 (2)"
date: "2015-08-23 17:12:01"
slug: "cloudstack-host-e7-8a-b6-e6-80-81-e6-9c-ba-2"
layout: "post"
categories: ["CloudStack"]
tags: ["CloudStack", "host", "状态机"]
---
书接上文：[CloudStack Host 状态机 (1)](http://www.chinacloudly.com/cloudstack-host-%e7%8a%b6%e6%80%81%e6%9c%ba-1/)
Status.java 中，定义了触发 host 状态机改变的一系列Event，如下代码所示：
[codesyntax lang="java"]

```
public enum Event {
        AgentConnected(false, "Agent connected"),
        PingTimeout(false, "Agent is behind on ping"),
        ShutdownRequested(false, "Shutdown requested by the agent"),
        AgentDisconnected(false, "Agent disconnected"),
        HostDown(false, "Host is found to be down by the investigator"),
        Ping(false, "Ping is received from the host"),
        ManagementServerDown(false, "Management Server that the agent is connected is going down"),
        WaitedTooLong(false, "Waited too long from the agent to reconnect on its own.  Time to do HA"),
        Remove(true, "Host is removed"),
        Ready(false, "Host is ready for commands"),
        RequestAgentRebalance(false, "Request rebalance for the certain host"),
        StartAgentRebalance(false, "Start rebalance for the certain host"),
        RebalanceCompleted(false, "Host is rebalanced successfully"),
        RebalanceFailed(false, "Failed to rebalance the host"),
        Error(false, "An internal error happened");

        private final boolean isUserRequest;
        private final String comment;

        private Event(boolean isUserRequest, String comment) {
            this.isUserRequest = isUserRequest;
            this.comment = comment;
        }

        public String getDescription() {
            return comment;
        }

        public boolean isUserRequest() {
            return isUserRequest;
        }
    }
```

[/codesyntax]
同上文，代码在Status.java中，同样，Event 只有一个private的构造函数，接受2个参数：isUserRequest 和 comment。
参数含义分别为：是否来自用户请求，comment为Event 描述。由此可见，来自用户请求的Event 只有一个Remove，即：删除host；其它状态都为系统监控和调度产生的Event。
Event 类型分别为：

```
AgentConnected：agent 连接成功
PingTimeout：ping 失败
ShutdownRequested：agent 接到关闭指令
AgentDisconnected：agent 失去连接
HostDown：host关机
Ping：ping成功
ManagementServerDown：management-server 关机
WaitedTooLong：超时，需要进行HA
Remove：删除host
Ready(false, "Host is ready for commands"),
RequestAgentRebalance：接到rebalance请求
StartAgentRebalance：rebalance 开始
RebalanceCompleted：rebalance 完成
RebalanceFailed：rebalance 失败
Error：错误，一般是代码级别判断错误（Internal Error）
```

[![公众号二维码](/assets/images/2015/12/公众号二维码-150x150.jpg)](/assets/images/2015/12/公众号二维码.jpg)[![微博二维码](/assets/images/2014/07/微博二维码.png)](/assets/images/2014/07/微博二维码.png)
