---
title: "CloudStack Host 状态机 (1)"
date: "2015-08-23 16:41:40"
slug: "cloudstack-host-e7-8a-b6-e6-80-81-e6-9c-ba-1"
layout: "post"
categories: ["CloudStack"]
tags: ["CloudStack", "host", "状态机"]
---
Cloudstack 对Host定义了一组状态机，对于Host所有状态的操作，定义了当前状态、事件、下一步状态。
Host 状态定义在 Status.java 中：
[codesyntax lang="java"]

```
public enum Status {
    Creating(true, false, false),
    Connecting(true, false, false),
    Up(true, false, false),
    Down(true, true, true),
    Disconnected(true, true, true),
    Alert(true, true, true),
    Removed(true, false, true),
    Error(true, false, true),
    Rebalancing(true, false, true);

    private final boolean updateManagementServer;
    private final boolean checkManagementServer;
    private final boolean lostConnection;

    private Status(boolean updateConnection, boolean checkManagementServer, boolean lostConnection) {
        this.updateManagementServer = updateConnection;
        this.checkManagementServer = checkManagementServer;
        this.lostConnection = lostConnection;
    }
    ......
}
```

[/codesyntax]
Java 中，枚举类型也是class，但是因为是固定的值，所以并没有public 的构造方法，只有一个 private 方法。
在Status 中，状态之后的3个 boolean 类型参数，分别是 updateManagementServer， checkManagementServer， lostConnection。
对应的含义分别为：是否需要更新management server信息，是否需要检查management server连接，是否由因为丢失connection引起。
相对应的操作为：如果updateManagementServer 为true，则更新host状态的同时，查询当前host的msid，更新host表中msid为最新状态。
如果checkManagementServer为true， 则更新host状态的同时，更新host 表中last\_ping 信息为最近一次ping值。
如果lostConnection为ture，则更新host 信息的同时，更新host表中msid为null。
以上枚举状态分别为：

```
Creating：创建，新加主机起始状态
Connecting：连接中，Agent连接成功，或Rebalance刚刚完成
Up：正常状态
Down：主机断开（多发于host或management-server关机，断网）
Disconnected：连接断开（多发于host或management-server断开，关机，
Alert：告警，状态异常（多发生于和Priamry Storage断开连接的时候）
Removed：移除，删除主机
Error：错误，一般是代码级别判断错误（Internal Error）
Rebalancing：Rebalance过程中
```

[![公众号二维码](/assets/images/2015/12/公众号二维码-150x150.jpg)](/assets/images/2015/12/公众号二维码.jpg)[![微博二维码](/assets/images/2014/07/微博二维码.png)](/assets/images/2014/07/微博二维码.png)
