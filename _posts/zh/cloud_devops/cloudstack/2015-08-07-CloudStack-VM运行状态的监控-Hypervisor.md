---
title: "CloudStack VM运行状态的监控-Hypervisor"
date: "2015-08-07 08:43:44"
slug: "cloudstack-vm-e8-bf-90-e8-a1-8c-e7-8a-b6-e6-80-81-e7-9a-84-e7-9b-91-e6-8e-a7-hypervisor"
layout: "post"
categories: ["CloudStack"]
tags: []
---
接上篇：[CloudStack VM运行状态的监控-Management](http://www.chinacloudly.com/cloudstack-vm%e8%bf%90%e8%a1%8c%e7%8a%b6%e6%80%81%e7%9a%84%e7%9b%91%e6%8e%a7-management/)
本文继续讲解Hyperviser端的处理逻辑.

# XenServer

XenServer的处理逻辑在CitrixResourceBase.java 中，该类封装了几乎全部的XenServer操作，主要调用XenServer  API 和 XenServer RRD API来完成。
[codesyntax lang="java"]

```
    @Override
    public Answer executeRequest(Command cmd) {
        Class<? extends Command> clazz = cmd.getClass();
        if (clazz == CreateCommand.class) {
        ......
        } else if (clazz == GetVmStatsCommand.class) {
            return execute((GetVmStatsCommand)cmd);
        }
        ......
    }
```

[/codesyntax]
 
该方法判断接收到的Command类型，并dispatch到相关处理方法。
[codesyntax lang="java"]

```
    protected GetVmStatsAnswer execute(GetVmStatsCommand cmd) {
        ......
            HashMap<String, VmStatsEntry> vmStatsUUIDMap = getVmStats(conn, cmd, vmUUIDs, cmd.getHostGuid());
            ......
            for (String vmUUID : vmStatsUUIDMap.keySet()) {
                vmStatsNameMap.put(vmNames.get(vmUUIDs.indexOf(vmUUID)), vmStatsUUIDMap.get(vmUUID));
            }
        ......
        return new GetVmStatsAnswer(cmd, vmStatsNameMap);
    }
```

[/codesyntax]
 
该方法调用getVmStats()方法，获取数据，并进行处理后返回。
[codesyntax lang="java"]

```
    protected HashMap<String, VmStatsEntry> getVmStats(Connection conn, GetVmStatsCommand cmd, List<String> vmUUIDs, String hostGuid) {
        HashMap<String, VmStatsEntry> vmResponseMap = new HashMap<String, VmStatsEntry>();
        ......
        Object[] rrdData = getRRDData(conn, 2); // call rrddata with 2 for vm
        ......//解析RRD Data
                if (param.contains("cpu")) {
                    vmStatsAnswer.setNumCPUs(vmStatsAnswer.getNumCPUs() + 1);
                    vmStatsAnswer.setCPUUtilization(((vmStatsAnswer.getCPUUtilization() + getDataAverage(dataNode, col, numRows))));
                } else if (param.matches("vif_\\d*_rx")) {
                    vmStatsAnswer.setNetworkReadKBs(vmStatsAnswer.getNetworkReadKBs() + (getDataAverage(dataNode, col, numRows)/1000));
                } else if (param.matches("vif_\\d*_tx")) {
                    vmStatsAnswer.setNetworkWriteKBs(vmStatsAnswer.getNetworkWriteKBs() + (getDataAverage(dataNode, col, numRows)/1000));
                } else if (param.matches("vbd_.*_read")) {
                    vmStatsAnswer.setDiskReadKBs(vmStatsAnswer.getDiskReadKBs() + (getDataAverage(dataNode, col, numRows)/1000));
                } else if (param.matches("vbd_.*_write")) {
                    vmStatsAnswer.setDiskWriteKBs(vmStatsAnswer.getDiskWriteKBs() + (getDataAverage(dataNode, col, numRows)/1000));
                }
            }
        }
        ......
        return vmResponseMap;
    }
```

[/codesyntax]
至此，全部逻辑处理完毕，XenServer 的 RRD 格式解析，日后会发文详解。
值得注意的是：getDataAverage()，看名字则可知其实逻辑是获取平均值。因为XenServer的RRD并不记录某段时间内的统计量，而是记录某一时刻的瞬时值。所以XenServer中，以此逻辑进行了处理，获取了该段时间内的全部瞬时值，然后进行处理得到近似这段时间内数据总量的统计值。

# VMware

逻辑类似于XenServer，只看getVmStats() 方法
[codesyntax lang="java"]

```
    private HashMap<String, VmStatsEntry> getVmStats(List<String> vmNames) throws Exception {
        ......
        List<PerfCounterInfo> cInfo = getServiceContext().getVimClient().getDynamicProperty(perfMgr, "perfCounter");
        ......
        int key = ((HostMO)hyperHost).getCustomFieldKey("VirtualMachine", CustomFieldConstants.CLOUD_VM_INTERNAL_NAME);
        ......
        String instanceNameCustomField = "value[" + key + "]";

        ObjectContent[] ocs =
                hyperHost.getVmPropertiesOnHyperHost(new String[] {"name", "summary.config.numCpu", "summary.quickStats.overallCpuUsage", instanceNameCustomField});
        if (ocs != null && ocs.length > 0) {
            for (ObjectContent oc : ocs) {
                List<DynamicProperty> objProps = oc.getPropSet();
                if (objProps != null) {
                    ......
                    for (DynamicProperty objProp : objProps) {
                        if (objProp.getName().equals("name")) {
                            vmNameOnVcenter = objProp.getVal().toString();
                        } else if (objProp.getName().contains(instanceNameCustomField)) {
                            if (objProp.getVal() != null)
                                vmInternalCSName = ((CustomFieldStringValue)objProp.getVal()).getValue();
                        } else if (objProp.getName().equals("summary.config.numCpu")) {
                            numberCPUs = objProp.getVal().toString();
                        } else if (objProp.getName().equals("summary.quickStats.overallCpuUsage")) {
                            maxCpuUsage = objProp.getVal().toString();
                        }
                    }
                    new VirtualMachineMO(hyperHost.getContext(), oc.getObj());
                    ......
                    ManagedObjectReference vmMor = hyperHost.findVmOnHyperHost(name).getMor();
                    ......
                    if (vmNetworkMetrics.size() != 0) {
                        ......
                        for (int i = 0; i < values.size(); ++i) {
                            List<PerfSampleInfo> infos = ((PerfEntityMetric)values.get(i)).getSampleInfo();
                            if (infos != null && infos.size() > 0) {
                                ......
                                List<PerfMetricSeries> vals = ((PerfEntityMetric)values.get(i)).getValue();
                                for (int vi = 0; ((vals != null) && (vi < vals.size())); ++vi) {
                                    if (vals.get(vi) instanceof PerfMetricIntSeries) {
                                        PerfMetricIntSeries val = (PerfMetricIntSeries)vals.get(vi);
                                        List<Long> perfValues = val.getValue();
                                        Long sumRate = 0L;
                                        for (int j = 0; j < infos.size(); j++) { // Size of the array matches the size as the PerfSampleInfo
                                            sumRate += perfValues.get(j);
                                        }
                                        Long averageRate = sumRate / infos.size();
                                        if (vals.get(vi).getId().getCounterId() == rxPerfCounterInfo.getKey()) {
                                            networkReadKBs = sampleDuration * averageRate; //get the average RX rate multiplied by sampled duration
                                        }
                                        if (vals.get(vi).getId().getCounterId() == txPerfCounterInfo.getKey()) {
                                            networkWriteKBs = sampleDuration * averageRate;//get the average TX rate multiplied by sampled duration
                                        }
                      ......
        return vmResponseMap;
    }
```

[/codesyntax]
由逻辑可见，Vmware也是获取平均值，然后乘相关时间，得到近似这段时间内数据总量的统计值。

# KVM

逻辑类似于XenServer，只看getVmStats() 方法
[codesyntax lang="java"]

```
    VmStatsEntry getVmStat(Connect conn, String vmName) throws LibvirtException {
        ......
            if (oldStats != null) {
                elapsedTime = now.getTimeInMillis() - oldStats._timestamp.getTimeInMillis();
                double utilization = (info.cpuTime - oldStats._usedTime) / ((double)elapsedTime * 1000000);

                utilization = utilization / node.cpus; //获取CPU使用值的平均值
                ......
            }
            .....。
            for (InterfaceDef vif : vifs) {
                DomainInterfaceStats ifStats = dm.interfaceStats(vif.getDevName());
                rx += ifStats.rx_bytes;
                tx += ifStats.tx_bytes;
            }

            if (oldStats != null) {
                double deltarx = rx - oldStats._rx;
                ......
                double deltatx = tx - oldStats._tx;
                ......
            }

            /* get disk stats */
            ......
            for (DiskDef disk : disks) {
                DomainBlockStats blockStats = dm.blockStats(disk.getDiskLabel());
                io_rd += blockStats.rd_req;
                io_wr += blockStats.wr_req;
                bytes_rd += blockStats.rd_bytes;
                bytes_wr += blockStats.wr_bytes;
            }

            if (oldStats != null) {
                long deltaiord = io_rd - oldStats._ioRead;
                ......
                long deltaiowr = io_wr - oldStats._ioWrote;
                ......
                double deltabytesrd = bytes_rd - oldStats._bytesRead;
                ......
                double deltabyteswr = bytes_wr - oldStats._bytesWrote;
                ......
            }
            ......
            return stats;
        ......
    }
```

[/codesyntax]
看代码逻辑，则可以得知，KVM得到的是准确的当前时间段内的磁盘和网络IO量。
