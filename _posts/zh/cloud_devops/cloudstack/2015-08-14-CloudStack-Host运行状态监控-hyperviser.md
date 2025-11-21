---
title: "CloudStack Host运行状态监控 - Hyperviser"
date: "2015-08-14 07:57:51"
slug: "cloudstack-host-e8-bf-90-e8-a1-8c-e7-8a-b6-e6-80-81-e7-9b-91-e6-8e-a7-hyperviser"
layout: "post"
categories: ["CloudStack"]
tags: ["CloudStack", "监控", "host"]
---
书接上文：[CloudStack Host运行状态监控 – Management](http://www.chinacloudly.com/cloudstack-host%e8%bf%90%e8%a1%8c%e7%8a%b6%e6%80%81%e7%9b%91%e6%8e%a7-management/)
继续分析Hyperviser端对于Host监控的实现。Hyperviser端接受到命令GetHostStatsCommand，会有相应逻辑对其进行处理，获取Host当前状态并返回。

# XenServer

CitrixResourceBase.java
[codesyntax lang="java"]

```
    protected GetHostStatsAnswer execute(GetHostStatsCommand cmd) {
        ......
            HostStatsEntry hostStats = getHostStats(conn, cmd, cmd.getHostGuid(), cmd.getHostId());
            return new GetHostStatsAnswer(cmd, hostStats);
        ......
    }
```

[/codesyntax]
 
在该类接受到此命令时，调用getHostStats方法，对主机状态进行查询，与VM类似，也是通过解析XenServer提供的RRD Data来进行数据获取。
[codesyntax lang="java"]

```
    protected HostStatsEntry getHostStats(Connection conn, GetHostStatsCommand cmd, String hostGuid, long hostId) {
        HostStatsEntry hostStats = new HostStatsEntry(hostId, 0, 0, 0, "host", 0, 0, 0, 0);
        Object[] rrdData = getRRDData(conn, 1); // call rrd method with 1 for host
        ......//获取RRD Data值
        for (int col = 0; col < numColumns; col++) {
            ......
            String type = columnMetadataList[1];
            String param = columnMetadataList[3];
            if (type.equalsIgnoreCase("host")) {
                if (param.matches("pif_eth0_rx")) {
                    hostStats.setNetworkReadKBs(getDataAverage(dataNode, col, numRows)/1000);
                } else if (param.matches("pif_eth0_tx")) {
                    hostStats.setNetworkWriteKBs(getDataAverage(dataNode, col, numRows)/1000);
                } else if (param.contains("memory_total_kib")) {
                    hostStats.setTotalMemoryKBs(getDataAverage(dataNode, col, numRows));
                } else if (param.contains("memory_free_kib")) {
                    hostStats.setFreeMemoryKBs(getDataAverage(dataNode, col, numRows));
                } else if (param.matches("cpu_avg")) {
                    // hostStats.setNumCpus(hostStats.getNumCpus() + 1);
                    hostStats.setCpuUtilization(hostStats.getCpuUtilization() + getDataAverage(dataNode, col, numRows));
                }
                ......
            }
        }
        ......
        return hostStats;
    }
```

[/codesyntax]
由此看出，实际对于Host运行状态的获取，XenServer只提供了eth0的出入流量瞬时值（以该段时间平均值为瞬时值），内存的总量和剩余量，cpu的平均使用率这5项内容，如果需要新加选项， 比如需要获取所有网卡流量等信息，可以修改此处代码获取。

# Vmware

VmwareResource.java
[codesyntax lang="java"]

```
    protected Answer execute(GetHostStatsCommand cmd) {
        ......
        VmwareContext context = getServiceContext();
        VmwareHypervisorHost hyperHost = getHyperHost(context);
        HostStatsEntry hostStats = new HostStatsEntry(cmd.getHostId(), 0, 0, 0, "host", 0, 0, 0, 0);
        ......
            HostStatsEntry entry = getHyperHostStats(hyperHost);
            if (entry != null) {
                entry.setHostId(cmd.getHostId());
                answer = new GetHostStatsAnswer(cmd, entry);
            }
        ......
        return answer;
    }
```

[/codesyntax]
 
在getHyperHostStats方法中，调用VMware API来获取Host状态。
[codesyntax lang="java"]

```
    private static HostStatsEntry getHyperHostStats(VmwareHypervisorHost hyperHost) throws Exception {
        ComputeResourceSummary hardwareSummary = hyperHost.getHyperHostHardwareSummary();
        ......
        HostStatsEntry entry = new HostStatsEntry();
        entry.setEntityType("host");
        double cpuUtilization = ((double)(hardwareSummary.getTotalCpu() - hardwareSummary.getEffectiveCpu()) / (double)hardwareSummary.getTotalCpu() * 100);
        entry.setCpuUtilization(cpuUtilization);
        entry.setTotalMemoryKBs(hardwareSummary.getTotalMemory() / 1024);
        entry.setFreeMemoryKBs(hardwareSummary.getEffectiveMemory() * 1024);
        return entry;
    }
```

[/codesyntax]
 
由代码可以看出，VMware Host状态值获取了CPU使用率，内存总量和使用量。

```
hyperHost.getHyperHostHardwareSummary的逻辑如下：
[codesyntax lang="java"]
```

```
    public ComputeResourceSummary getHyperHostHardwareSummary() throws Exception {
        ......
        HostHardwareSummary hardwareSummary = getHostHardwareSummary();
        ComputeResourceSummary resourceSummary = new ComputeResourceSummary();
        resourceSummary.setNumCpuCores(hardwareSummary.getNumCpuCores());
        resourceSummary.setTotalMemory(hardwareSummary.getMemorySize());
        int totalCpu = hardwareSummary.getCpuMhz() * hardwareSummary.getNumCpuCores();
        resourceSummary.setTotalCpu(totalCpu);
        HostListSummaryQuickStats stats = getHostQuickStats();
        ......
        resourceSummary.setEffectiveCpu(totalCpu - stats.getOverallCpuUsage());
        resourceSummary.setEffectiveMemory(hardwareSummary.getMemorySize() / (1024 * 1024) - stats.getOverallMemoryUsage());
        ......
        return resourceSummary;
    }
```

```
[/codesyntax]
如果想要获取更多VMware Host的运行状态，可以在这两个方法中添加相应内容来获取。
```

# KVM

[codesyntax lang="java"]

```
    private Answer execute(GetHostStatsCommand cmd) {
        final Script cpuScript = new Script("/bin/bash", s_logger);
        cpuScript.add("-c");
        cpuScript.add("idle=$(top -b -n 1| awk -F, '/^[%]*[Cc]pu/{$0=$4; gsub(/[^0-9.,]+/,\"\"); print }'); echo $idle");
        final OutputInterpreter.OneLineParser parser = new OutputInterpreter.OneLineParser();
        String result = cpuScript.execute(parser);
        ......
        double cpuUtil = (100.0D - Double.parseDouble(parser.getLine()));

        long freeMem = 0;
        final Script memScript = new Script("/bin/bash", s_logger);
        memScript.add("-c");
        memScript.add("freeMem=$(free|grep cache:|awk '{print $4}');echo $freeMem");
        final OutputInterpreter.OneLineParser Memparser = new OutputInterpreter.OneLineParser();
        result = memScript.execute(Memparser);
        ......
        freeMem = Long.parseLong(Memparser.getLine());

        Script totalMem = new Script("/bin/bash", s_logger);
        totalMem.add("-c");
        totalMem.add("free|grep Mem:|awk '{print $2}'");
        final OutputInterpreter.OneLineParser totMemparser = new OutputInterpreter.OneLineParser();
        result = totalMem.execute(totMemparser);
        ......
        long totMem = Long.parseLong(totMemparser.getLine());

        Pair<Double, Double> nicStats = getNicStats(_publicBridgeName);
        HostStatsEntry hostStats = new HostStatsEntry(cmd.getHostId(), cpuUtil, nicStats.first() / 1024, nicStats.second() / 1024, "host", totMem, freeMem, 0, 0);
        return new GetHostStatsAnswer(cmd, hostStats);
    }
```

[/codesyntax]
由此看出，对于KVM的Host信息，CPU是根据top命令返回值来获取，内存使用信息则是通过free命令获取。网卡是调用getNicStats方法获取，getNicStats方法也是返回public bridge的上下行速度。
[codesyntax lang="java"]

```
    static Pair<Double, Double> getNicStats(String nicName) {
        return new Pair<Double, Double>(readDouble(nicName, "rx_bytes"), readDouble(nicName, "tx_bytes"));
    }

    static double readDouble(String nicName, String fileName) {
        final String path = "/sys/class/net/" + nicName + "/statistics/" + fileName;
        ......
            return Double.parseDouble(FileUtils.readFileToString(new File(path)));
        ......
    }
```

[/codesyntax]
网卡速度在/sys/class/net/[NICNAME]/statistics/[rx\_bytes/tx\_bytes]中读出
