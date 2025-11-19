---
title: "CloudStack Host运行状态监控 - Management"
date: "2015-08-14 07:15:44"
slug: "cloudstack-host-e8-bf-90-e8-a1-8c-e7-8a-b6-e6-80-81-e7-9b-91-e6-8e-a7-management"
layout: "post"
categories: ["CloudStack"]
tags: ["CloudStack", "监控", "host"]
---
CloudStack中，Host的实时状态监控和VM基本类似。

# 信息获取原理

Management-Server在启动的时候，会初始化1个线程，用于定期获取定期获取运行时数据。
对于3个主流Hyperviser：KVM、XenServer、VMware，分别调用Libvirt API、 XenServer RRD API和 VMware API来获取当前运行时状态。
定期获取状态之后，会上报到该线程，作为当前的使用量。
所以，CloudStack对于Host状态的监控，是当前时间瞬时数据。

# 代码解析

StatsCollector.java
[codesyntax lang="java"]

```
    public boolean start() {
        init(_configDao.getConfiguration());
        return true;
    }
```

[/codesyntax]
 
init方法中，读取全局变量的某些设置，启动监控线程。
[codesyntax lang="java"]

```
    private void init(Map<String, String> configs) {
        ......
        hostStatsInterval = NumbersUtil.parseLong(configs.get("host.stats.interval"), 60000L);
        ......
        if (hostStatsInterval > 0) {
            _executor.scheduleWithFixedDelay(new HostCollector(), 15000L, hostStatsInterval, TimeUnit.MILLISECONDS);
        }
        ......
    }
```

[/codesyntax]
此处读取全局配置中的host.stats.interval，默认值为60s执行一次。如果需要调整状态获取时间，则需要在全局配置中修改此项。

```
HostCollector是监控线程，继承ManagedContextRunnable。该线程主要负责列出所有需要查询的Host，获取host当前的状态值，写入内存中。
[codesyntax lang="java"]
```

```
    class HostCollector extends ManagedContextRunnable {
        @Override
        protected void runInContext() {
            try {
                ......
                SearchCriteria<HostVO> sc = _hostDao.createSearchCriteria();
                ......//拼接host查询条件，只查询Hyperviser
                ConcurrentHashMap<Long, HostStats> hostStats = new ConcurrentHashMap<Long, HostStats>();
                List<HostVO> hosts = _hostDao.search(sc, null);
                for (HostVO host : hosts) {
                    HostStatsEntry stats = (HostStatsEntry)_resourceMgr.getHostStatistics(host.getId());
                    if (stats != null) {
                        hostStats.put(host.getId(), stats);
                    ......
                }
                _hostStats = hostStats;
                ......
    }
```

```
[/codesyntax]
```

```
_resourceMgr.getHostStatistics 是实际调用方法，向Hyperviser发送GetHostStatsCommand命令，获取主机状态监控的数据。
由此可以看出，对于Host状态的获取，是逐台主机顺次执行，所以，如果环境中主机数量比较多的情况下，该线程单次执行的时间也会相应加长。
[codesyntax lang="java"]
```

```
    @Override
    public HostStats getHostStatistics(long hostId) {
        Answer answer = _agentMgr.easySend(hostId, new GetHostStatsCommand(_hostDao.findById(hostId).getGuid(), _hostDao.findById(hostId).getName(), hostId));
        ......
            if (answer instanceof GetHostStatsAnswer) {
                return ((GetHostStatsAnswer)answer).getHostStats();
            }
        ......
    }
```

```
[/codesyntax]
```
