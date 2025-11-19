---
title: "msHost runId 和 Invalid cluster session detected"
date: "2015-11-11 23:54:15"
slug: "post-531"
layout: "post"
categories: ["CloudStack"]
tags: []
draft: true
---
ClusterManagerImpl.java中，初始化了3个变量：
[codesyntax lang="java"]

```
//
    // pay attention to _mshostId and _msid
    // _mshostId is the primary key of management host table
    // _msid is the unique persistent identifier that peer name is based upon
    //
    private Long _mshostId = null;
    protected long _msId = ManagementServerNode.getManagementServerId();
    protected long _runId = System.currentTimeMillis();
```

[/codesyntax]
其中，\_mshostId是db中mshost表的主键，会在后续程序中赋值。
\_runId是取系统的当前时间毫秒数。
\_msId是mac地址取整数，方法如下：
[codesyntax lang="java"]

```
public class ManagementServerNode extends AdapterBase implements SystemIntegrityChecker {
    。。。。。。
    private static final long s_nodeId = MacAddress.getMacAddress().toLong();
    。。。。。。
    public static long getManagementServerId() {
        return s_nodeId;
    }
    。。。。。。
}
```

[/codesyntax]
在启动加载该类的时候，会调用start方法，如下：
方法中会查找db中是否存在该\_msId，如果没有，则将\_msId 加入到db中，如果存在，则更新DB中的msHost信息。
[codesyntax lang="java"]

```
@Override
    @DB
    public boolean start() {
        。。。。。。
        ManagementServerHostVO mshost = Transaction.execute(new TransactionCallback<ManagementServerHostVO>() {
            @Override
            public ManagementServerHostVO doInTransaction(TransactionStatus status) {

                final Class<?> c = this.getClass();
                String version = c.getPackage().getImplementationVersion();

                ManagementServerHostVO mshost = _mshostDao.findByMsid(_msId);
                if (mshost == null) {
                    mshost = new ManagementServerHostVO();
                    mshost.setMsid(_msId);
                    mshost.setRunid(getCurrentRunId());
                    mshost.setName(NetUtils.getHostName());
                    mshost.setVersion(version);
                    mshost.setServiceIP(_clusterNodeIP);
                    mshost.setServicePort(_currentServiceAdapter.getServicePort());
                    mshost.setLastUpdateTime(DateUtil.currentGMTTime());
                    mshost.setRemoved(null);
                    mshost.setAlertCount(0);
                    mshost.setState(ManagementServerHost.State.Up);
                    _mshostDao.persist(mshost);

                    if (s_logger.isInfoEnabled()) {
                        s_logger.info("New instance of management server msid " + _msId + " is being started");
                    }
                } else {
                    if (s_logger.isInfoEnabled()) {
                        s_logger.info("Management server " + _msId + " is being started");
                    }

                    _mshostDao.update(mshost.getId(), getCurrentRunId(), NetUtils.getHostName(), version, _clusterNodeIP, _currentServiceAdapter.getServicePort(),
                    DateUtil.currentGMTTime());
                }

                return mshost;
            }
        });
        //给_mshostId赋值
        _mshostId = mshost.getId();
        。。。。。。
        _heartbeatScheduler.scheduleAtFixedRate(getHeartbeatTask(), HeartbeatInterval.value(), HeartbeatInterval.value(), TimeUnit.MILLISECONDS);
        。。。。。。
    }
```

[/codesyntax]
