---
title: "CloudStack VM运行状态的监控-Management"
date: "2015-08-07 08:09:49"
slug: "cloudstack-vm-e8-bf-90-e8-a1-8c-e7-8a-b6-e6-80-81-e7-9a-84-e7-9b-91-e6-8e-a7-management"
layout: "post"
categories: ["CloudStack"]
tags: []
---
VM和Host的运行时刻状态，应该是所有虚拟化平台管理员最热切的关注点。
本文章介绍下CloudStack中，对于VM运行状态信息的获取和扩展。

# 信息获取原理

Management-Server在启动的时候，会初始化1个线程，用于定期获取定期获取运行时数据。
对于3个主流Hyperviser：KVM、XenServer、VMware，分别调用Libvirt API、 XenServer RRD API和 VMware API来获取当前运行时状态。
定期获取状态之后，会上报到该线程，和之前的上报的数据进行累加，以得到统计全量。
所以，CloudStack对于VM状态的监控，是从Management-Server启动到当前时间的历史统计数据，并非瞬时值。

# 代码解析

StatsController.java
该类继承了ComponentLifecycle，在Management-Server 启动的时候，会加载start方法，启动后台服务。
[codesyntax lang="java"]

```
@Override
public boolean start() {
    init(_configDao.getConfiguration());
    return true;
}
```

[/codesyntax]
其中 init() 方法，会读取全局配置中的设置，初始化不同的监控进程
[codesyntax lang="java"]

```
private void init(Map<String, String> configs) {
    _executor = Executors.newScheduledThreadPool(4, new NamedThreadFactory("StatsCollector"));

    ......
    hostAndVmStatsInterval = NumbersUtil.parseLong(configs.get("vm.stats.interval"), 60000L);
    ......
    if (hostAndVmStatsInterval > 0) {
        _executor.scheduleWithFixedDelay(new VmStatsCollector(), 15000L, hostAndVmStatsInterval, TimeUnit.MILLISECONDS);
    }
    ......
}
```

[/codesyntax]
代码可以看出，从全局设置中里面获取vm.stats.interval变量，默认为60s，即1分钟。如果想修改调整时间，可以在全局配置中进行修改。
VmStatsCollector是线程类，集成ManagedContextRunnable。
VmStatsCollector列出全部可用Host，然后按Host进行遍历，查询Host上所有VM当前运行状态，与历史值进行累加，代码如下：
[codesyntax lang="java"]

```
    class VmStatsCollector extends ManagedContextRunnable {
        @Override
        protected void runInContext() {
            try {
                ......
                SearchCriteria<HostVO> sc = _hostDao.createSearchCriteria();
                ......//创建查询条件
                List<HostVO> hosts = _hostDao.search(sc, null);

                for (HostVO host : hosts) {
                    List<UserVmVO> vms = _userVmDao.listRunningByHostId(host.getId());
                    ......
                    try {
                        HashMap<Long, VmStatsEntry> vmStatsById = _userVmMgr.getVirtualMachineStatistics(host.getId(), host.getName(), vmIds);
                        if (vmStatsById != null) {
                            ......
                            //新VM，加入map中
                        } else {
                            //已有历史数据VM，进行更新，CPU记录最新值，Disk和Network进行累加
                                statsInMemory.setCPUUtilization(statsForCurrentIteration.getCPUUtilization());
                                    statsInMemory.setNumCPUs(statsForCurrentIteration.getNumCPUs());
                                    statsInMemory.setNetworkReadKBs(statsInMemory.getNetworkReadKBs() + statsForCurrentIteration.getNetworkReadKBs());
                                    statsInMemory.setNetworkWriteKBs(statsInMemory.getNetworkWriteKBs() + statsForCurrentIteration.getNetworkWriteKBs());
                                    statsInMemory.setDiskWriteKBs(statsInMemory.getDiskWriteKBs() + statsForCurrentIteration.getDiskWriteKBs());
                                    statsInMemory.setDiskReadIOs(statsInMemory.getDiskReadIOs() + statsForCurrentIteration.getDiskReadIOs());
                                    statsInMemory.setDiskWriteIOs(statsInMemory.getDiskWriteIOs() + statsForCurrentIteration.getDiskWriteIOs());
                                    statsInMemory.setDiskReadKBs(statsInMemory.getDiskReadKBs() + statsForCurrentIteration.getDiskReadKBs());
                                    _VmStats.put(vmId, statsInMemory);
    ......
    }
```

[/codesyntax]

```
_userVmMgr.getVirtualMachineStatistics() 方法中，向Hyperviser发送Cmd，查询所需信息，代码如下：
[codesyntax lang="java"]
```

```
    public HashMap<Long, VmStatsEntry> getVirtualMachineStatistics(long hostId, String hostName, List<Long> vmIds) throws CloudRuntimeException {
        ......
        Answer answer = _agentMgr.easySend(hostId, new GetVmStatsCommand(vmNames, _hostDao.findById(hostId).getGuid(), hostName));
        ......
    }
```

```
[/codesyntax]
```

```
GetVmStatsCommand会发送到Hyperviser相关进程，并由Hyperviser相关进程调用API或 Cloud-Agent 服务进行处理，处理结果返回到当前线程进行处理，最终由VmStatsCollector进行合并。
在ListVm过程中，如果需要得到VM运行时状态，则调用StatsController的getVmStats来获取。

在Hyperviser的相关文件中，各有接受GetVmStatsCommand并进行处理的相关逻辑，下篇帖子会继续介绍Hyperviser中相关逻辑。
CloudStack VM运行状态的监控-Hypervisor
```
