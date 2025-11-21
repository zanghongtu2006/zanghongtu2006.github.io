---
title: "CloudStack 解析 XenServer RRD (2)"
date: "2015-08-17 23:23:04"
slug: "cloudstack-e8-a7-a3-e6-9e-90-xenserver-rrd-2"
layout: "post"
categories: ["CloudStack"]
tags: ["CloudStack", "xenserver", "监控", "RRD"]
---
书接上文：[CloudStack 解析 XenServer RRD (1)](http://www.chinacloudly.com/cloudstack-%e8%a7%a3%e6%9e%90-xenserver-rrd-1/)
了解了XenServer RRD格式之后，现在看一下CloudStack中是怎么解析RRD的。
在之前的文章[CloudStack VM运行状态的监控-Hypervisor](http://www.chinacloudly.com/cloudstack-vm%e8%bf%90%e8%a1%8c%e7%8a%b6%e6%80%81%e7%9a%84%e7%9b%91%e6%8e%a7-hypervisor/) 中介绍过，在CitrixResourceBase.java中，GetVmStatsCommand的处理过程，是通过解析RRD来实现VM运行时状态抓取的。
首先，看一下RRD Data的获取：
[codesyntax lang="java"]

```
    protected Document getStatsRawXML(Connection conn, boolean host) {
        Date currentDate = new Date();
        String urlStr = "http://" + _host.ip + "/rrd_updates?";
        urlStr += "session_id=" + conn.getSessionReference();
        urlStr += "&host=" + (host ? "true" : "false");
        urlStr += "&cf=" + _consolidationFunction;            //cf=AVERAGE
        urlStr += "&interval=" + _pollingIntervalInSeconds;   //每条记录间隔60s
        urlStr += "&start=" + (currentDate.getTime() / 1000 - 1000 - 100);  //当前时间-1100s
        
        URL url;
        BufferedReader in = null;
        try {
            url = new URL(urlStr);
            url.openConnection();
            URLConnection uc = url.openConnection();
            in = new BufferedReader(new InputStreamReader(uc.getInputStream()));
            InputSource statsSource = new InputSource(in);
            return DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(statsSource);
        ......
    }
```

[/codesyntax]
如上代码，先拼接一个URL，例：http://192.168.1.21/rrd\_updates?session\_id=xxx-xxx-xxx-xxx-xx&host=false&cf=AVERAGE&interval=60
然后打开URL链接，返回RRD Data，格式如上文所述 <xport><meta>...</meta><data>...</data></xport>。
接下来看一下这段逻辑的调用者 getRRDData，该方法接受2个参数，第一个为Connection，第二个flag：用1和2表示此处获取host还是vm的数据值，1为host，2为vm。
 
[codesyntax lang="java"]

```
    protected Object[] getRRDData(Connection conn, int flag) {
        ......
            doc = getStatsRawXML(conn, flag == 1 ? true : false);
        ......
        NodeList firstLevelChildren = doc.getChildNodes();
        NodeList secondLevelChildren = (firstLevelChildren.item(0)).getChildNodes();
        Node metaNode = secondLevelChildren.item(0);
        Node dataNode = secondLevelChildren.item(1);

        Integer numRows = 0;
        Integer numColumns = 0;
        Node legend = null;
        NodeList metaNodeChildren = metaNode.getChildNodes();
        for (int i = 0; i < metaNodeChildren.getLength(); i++) {
            Node n = metaNodeChildren.item(i);
            if (n.getNodeName().equals("rows")) {
                numRows = Integer.valueOf(getXMLNodeValue(n));
            } else if (n.getNodeName().equals("columns")) {
                numColumns = Integer.valueOf(getXMLNodeValue(n));
            } else if (n.getNodeName().equals("legend")) {
                legend = n;
            }
        }

        return new Object[] { numRows, numColumns, legend, dataNode };
    }
```

[/codesyntax]
该方法对获取到的RRD Data XML进行解析：先取出<meta></meta>和<data></data>两个节点赋值给metaNode 和dataNode，metaNode为头信息和字段信息，dataNode为实际运行时数据信息（见上文）。
接下来遍历metaNode，获取row和column数量、legend，然后将四个值一起返回给调用者getVmStats和getHostStats。
[codesyntax lang="java"]

```
    protected HashMap<String, VmStatsEntry> getVmStats(Connection conn, GetVmStatsCommand cmd, List<String> vmUUIDs, String hostGuid) {
        ......
        Object[] rrdData = getRRDData(conn, 2); // call rrddata with 2 for vm
        ......
        Integer numRows = (Integer)rrdData[0];
        Integer numColumns = (Integer)rrdData[1];
        Node legend = (Node)rrdData[2];
        Node dataNode = (Node)rrdData[3];

        NodeList legendChildren = legend.getChildNodes();
        for (int col = 0; col < numColumns; col++) {
            ......
            String columnMetadata = getXMLNodeValue(legendChildren.item(col));
            ......
            String[] columnMetadataList = columnMetadata.split(":");
            ......
            String type = columnMetadataList[1];
            String uuid = columnMetadataList[2];
            String param = columnMetadataList[3];

            if (type.equals("vm") && vmResponseMap.keySet().contains(uuid)) {
                VmStatsEntry vmStatsAnswer = vmResponseMap.get(uuid);
                vmStatsAnswer.setEntityType("vm");

                if (param.contains("cpu")) {
                    vmStatsAnswer.setNumCPUs(vmStatsAnswer.getNumCPUs() + 1);
                    vmStatsAnswer.setCPUUtilization(((vmStatsAnswer.getCPUUtilization() + getDataAverage(dataNode, col, numRows))));
                } else if (param.matches("vif_\\d_rx")) {
                    vmStatsAnswer.setNetworkReadKBs(vmStatsAnswer.getNetworkReadKBs() + (getDataAverage(dataNode, col, numRows) / (8 * 2)));
                } else if (param.matches("vif_\\d_tx")) {
                    vmStatsAnswer.setNetworkWriteKBs(vmStatsAnswer.getNetworkWriteKBs() + (getDataAverage(dataNode, col, numRows) / (8 * 2)));
                }
            }
        }

        for (String vmUUID : vmResponseMap.keySet()) {
            VmStatsEntry vmStatsAnswer = vmResponseMap.get(vmUUID);
            if (vmStatsAnswer.getNumCPUs() != 0) {
                vmStatsAnswer.setCPUUtilization(vmStatsAnswer.getCPUUtilization() / vmStatsAnswer.getNumCPUs());
            }
            vmStatsAnswer.setCPUUtilization(vmStatsAnswer.getCPUUtilization() * 100);
            ......
        }
        ......
        return vmResponseMap;
    }
```

[/codesyntax]
先遍历legend节点，每个legend格式类似于：AVERAGE:vm:52bf87dd-10ff-4d99-9042-66698cc5d6c6:cpu0。解析字符串可以得到type=vm,uuid=52bf87dd-10ff-4d99-9042-66698cc5d6c6,param=cpu0。
param是字段值。根据uuid和param，对dataNode进行解析，遍历dataNode，取出getDataAverage(dataNode, col, numRows) 并进行累加，获得CPU总数，CPU总使用率，网卡总读写速度。
遍历完成后，对得到的CPU使用率进行处理，计算出CPU单核的平均使用率并返回。
getHostStats总体逻辑基本类似。
如果要添加XenServer监控数据，可以自行拼接URL，在此流程中添加新值即可。
接下来看一下刚刚调用到的getDataAverage方法，此方法接受3个参数，dataNode是全部的<data></data>，col是解析legend得到的当前列数，numRows是dataNode中一共有几行。
遍历dataNode，解析指定col，将值value进行累加，并将可用行数numRowUsed累加。如果col的值为NaN，则为空，该行定义为不可用。
全部遍历完成后，取value/numRowUsed为平均值返回，如果无可用行或出现异常，则返回dummy=0；代码如下：
 
[codesyntax lang="java"]

```
    protected double getDataAverage(Node dataNode, int col, int numRows) {
        double value = 0;  
        double dummy = 0;  
        int numRowsUsed = 0; 

        for (int row = 0; row < numRows; row++) {
            Node data = dataNode.getChildNodes().item(numRows - 1 - row).getChildNodes().item(col + 1);
            Double currentDataAsDouble = Double.valueOf(getXMLNodeValue(data));
            if (!currentDataAsDouble.equals(Double.NaN)) {
                numRowsUsed += 1;
                value += currentDataAsDouble;
            }
        }

        if (numRowsUsed == 0) {
            if ((!Double.isInfinite(value)) && (!Double.isNaN(value))) {
                return value;
            } else {
                s_logger.warn("Found an invalid value (infinity/NaN) in getDataAverage(), numRows=0");
                return dummy;
            }
        } else {
            if ((!Double.isInfinite(value / numRowsUsed)) && (!Double.isNaN(value / numRowsUsed))) {
                return (value / numRowsUsed);
            } else {
                s_logger.warn("Found an invalid value (infinity/NaN) in getDataAverage(), numRows>0");
                return dummy;
            }
        }

    }
```

[/codesyntax]
