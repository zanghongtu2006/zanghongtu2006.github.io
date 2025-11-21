---
title: "CloudStack全局配置参数"
date: "2014-12-15 14:36:36"
slug: "cloudstack-e5-85-a8-e5-b1-80-e9-85-8d-e7-bd-ae-e5-8f-82-e6-95-b0"
layout: "post"
categories: ["CloudStack"]
tags: []
---
`account.cleanup.interval`
清除用户账户所需要等待的时间（秒）；类型：整数；默认86400
agent.lb.enabled    false    If agent load balancing enabled in cluster setup
agent.load.threshold    0.7    Percentage (as a value between 0 and 1) of connected agents after which agent load balancing will start happening
`alert.email.addresses`
Alert发送到邮箱地址，以逗号分隔；类型：邮箱；默认：NULL
`alert.email.sender`
发送Alert的邮箱地址；类型：邮箱；默认：NULL
`alert.purge.delay`
Alert清理时间（秒），清理掉超过该时间的Alert；类型：整数；默认：0（不清理Alert）
`alert.purge.interval`
Alert清理线程间隔时间（秒）；类型：整数；默认：86400
`alert.smtp.connectiontimeout`
Alert发送邮件smtp socket连接超时时间（毫秒）；类型：整数；默认：30000（-1则不设定超时）
`alert.smtp.host`
Alert发送邮件SMTP主机地址；类型：主机名；默认：NULL
`alert.smtp.password`
Alert发送邮件SMTP密码，仅在alert.smpt.useAuth为true的时候需要；类型：字符串；默认：NULL
`alert.smtp.port`
Alert发送邮件SMTP服务端口；类型：端口；默认：465
`alert.smtp.timeout`
Alert发送邮件smtp socket I/O超时时间（毫秒）；类型：整数；默认：30000（-1则不超时）
`alert.smtp.useAuth`
Alert发送邮件SMTP服务是否加密；类型：true/false；默认：NULL
`alert.smtp.username`
Alert发送邮件SMTP账户，仅在alert.smtp.useAuth为true的时候有效；类型：字符串；默认：NULL
alert.wait    NULL    Seconds to wait before alerting on a disconnected agent
`allow.public.user.templates`
允许用户创建public属性的模板；类型：true/false；默认：true
`allow.subdomain.network.access`
允许sub domain使用parent domain的专有网络；类型：true/false；默认：true
`allow.user.create.projects`
允许用户创建project；类型：true/false；默认：true
api.throttling.cachesize    50000    Account based API count cache size
api.throttling.enabled    false    Enable/Disable Api rate limit
api.throttling.interval    1    Time interval (in seconds) to reset API count
api.throttling.max    25    Max allowed number of APIs within fixed interval
apply.allocation.algorithm.to.pods    false    If true, deployment planner applies the allocation heuristics at pods first in the given datacenter during VM resource allocation
`backup.snapshot.wait`
备份快照超时时间（秒）；类型：整数；默认：21600
baremetal.ipmi.fail.retry    default    ipmi interface will be temporary out of order after power opertions(e.g. cycle, on), it leads following commands fail immediately. The value specifies retry times before accounting it as real failure
baremetal.ipmi.lan.interface    default    option specified in -I option of impitool. candidates are: open/bmc/lipmi/lan/lanplus/free/imb, see ipmitool man page for details. default valule "default" means using default option of ipmitool
blacklisted.routes    NULL    Routes that are blacklisted, can not be used for Static Routes creation for the VPC Private Gateway
`capacity.check.period`
检查配额时间间隔（毫秒）；类型：整数；默认：300000
`capacity.skipcounting.hours`
VM Stop和释放CPU内存资源之间的时间间隔（秒）；类型：整数；默认：3600
`check.pod.cidrs`
检查POD是否使用相同CIDR，true的话，不同的POD必须属于不同的CIDR；类型：true/false；默认：true
`cloud.dns.name`
为GSLB（全局负载均衡）服务提供的DNS名；类型：字符串；默认：NULL
`cluster.cpu.allocated.capacity.disablethreshold`
Cluster中CPU分配率上限，CPU分配量/CPU可用量不能超过该值；类型：小数（0~1）；默认：0.85
`cluster.cpu.allocated.capacity.notificationthreshold`
Cluster中，CPU分配率报警值，CPU分配量/CPU可用量超过该值则发送Alert；类型：小数（0~1）；默认：0.75
`cluster.localStorage.capacity.notificationthreshold`
Cluster中，localStorage分配率报警值，localStorage分配量/localStorage可用量超过该值则发送Alert；类型：小数（0~1）；默认：0.75
`cluster.memory.allocated.capacity.disablethreshold`
Cluster中memory分配率上限，memory分配量/memory可用量不能超过该值；类型：小数（0~1）；默认：0.85
`cluster.memory.allocated.capacity.notificationthreshold`
Cluster中，memory分配率报警值，memory分配量/memory可用量超过该值则发送Alert；类型：小数（0~1）；默认：0.75
cluster.message.timeout.seconds    300    Time (in seconds) to wait before a inter-management server message post times out.
`cluster.storage.allocated.capacity.notificationthreshold`
Cluster中，storage分配率报警值，storage分配量/storage可用量超过该值则发送Alert；类型：小数（0~1）；默认：0.75
`cluster.storage.capacity.notificationthreshold`
Cluster中，storage使用率报警值，storage使用量/storage总量超过该值则发送Alert；类型：小数（0~1）；默认：0.75
`concurrent.snapshots.threshold.perhost`
每台主机并发执行的Snapshot线程数；类型：整数；默认：NULL（不限制）
`consoleproxy.capacity.standby`
Console proxy最小备用Session数，用来保证系统是否能及时提供服务；类型：整数；默认：10
`consoleproxy.capacityscan.interval`
Console proxy定期检查时间间隔（秒），系统定期检查是否需要更多的Console proxy来保证最小备用量；类型：整数；默认：30000
`consoleproxy.cmd.port`
Console proxy和management Server通信端口；类型：端口；默认：8001
`consoleproxy.disable.rpfilter`
禁用Console proxy VM public IP的rp\_filter；类型：true/false；默认：true
`consoleproxy.launch.max`
一个zone可以拥有的最大Console proxy实例数；类型：整数；默认：10
`consoleproxy.loadscan.interval`
Console proxy负载检查时间间隔（毫秒）；类型：整数；默认10000
consoleproxy.management.state    Auto    console proxy service management state
consoleproxy.management.state.last    Auto    last console proxy service management state
consoleproxy.restart    true    Console proxy restart flag, defaulted to true
`consoleproxy.service.offering`
Console proxy计算服务类型；类型：计算服务UUID；默认：NULL（使用系统默认类型）
`consoleproxy.session.max`
每个Console proxy拥有的最大Session数；类型：整数；默认：50
`consoleproxy.session.timeout`
Console proxy Session超时时间（毫秒）；类型：整数；默认：30000
`consoleproxy.url.domain`
Console proxy URL domain；类型：domain name；默认：realhostip.com（必须可以访问到此域名）
`control.cidr`
用于control network通信，默认为link-local，每个POD必须唯一；类型：CIDR；默认：169.254.0.0/16
`control.gateway`
control network 网关；类型：IP；默认：169.254.0.1
`copy.volume.wait`
磁盘copy超时时间；类型：整数；默认：10800
`cpu.overprovisioning.factor`
CPU超配倍数，CPU可用量=CPU总量\*超配倍数；类型：整数；默认：1（不超配）
`create.private.template.from.snapshot.wait`
从快照创建模板超时时间（秒）；类型：整数；默认：10800
`create.private.template.from.volume.wait`
从卷创建模板超时时间（秒）；类型：整数；默认：10800
`create.volume.from.snapshot.wait`
从快照创建卷超时时间（秒）；类型：整数；默认：10800
`custom.diskoffering.size.max`
允许用户创建磁盘最大值（GB）；类型：整数；默认：1024
`custom.diskoffering.size.min`
允许用户创建磁盘最小值（GB）；类型：整数；默认：1
`default.page.size`
list API默认一页大小；类型：整数；默认：500
detail.batch.query.size    2000    Default entity detail batch query size for listing
`developer`
开发者模式；类型：true/false；默认：true
direct.agent.load.size    16    The number of direct agents to load each time
direct.agent.pool.size    500    Default size for DirectAgentPool
direct.agent.scan.interval    90    Time interval (in seconds) to run the direct agent scan task.
direct.attach.network.externalIpAllocator.enabled    false    Direct-attach VMs using external DHCP server
direct.attach.network.externalIpAllocator.url    NULL    Direct-attach VMs using external DHCP server (API url)
direct.network.no.default.route    false    Direct Network Dhcp Server should not send a default route
`direct.network.stats.interval`
在Traffic Monitor采集数据间隔时间；类型：整数；默认：86400
`disable.extraction`
禁用模板/ISO下载；类型：true/false；默认：false
eip.use.multiple.netscalers    false    Should be set to true, if there will be multiple NetScaler devices providing EIP service in a zone
enable.baremetal.securitygroup.agent.echo    false    After starting provision process, periodcially echo security agent installed in the template. Treat provisioning as success only if echo successfully
enable.dynamic.scale.vm    false    Enables/Diables dynamically scaling a vm
`enable.ec2.api`
启用EC2 API；类型：true/false；默认：false
`enable.ha.storage.migration`
启用HA过程中，对主存储动态迁移；类型：true/false；默认：true
`enable.s3.api`
启用S3 API；类型：true/false；默认：false
`enable.usage.server`
启用Usage Server；类型：true/false；默认：true
`encode.api.response`
对API请求进行URL转码；类型：true/false；默认：false
endpointe.url    http://localhost:8080/client/api    Endpointe Url
event.purge.delay    15    Events older than specified number days will be purged. Set this value to 0 to never delete events
`event.purge.interval`
Event清理线程允许时间间隔（秒）；类型：整数；默认：86400
`execute.in.sequence.hypervisor.commands`
hyperviser执行command（StartCommand, StopCommand, CopyCommand）是否序列化，true则顺序执行，false则同时执行；类型：true/false；默认：true
`execute.in.sequence.network.element.commands`
执行网络节点command（DhcpEntryCommand, SavePasswordCommand, UserDataCommand, VmDataCommand）是否序列化，true则顺序执行，false则同时执行；类型：true/false；默认：true
`expunge.delay`
清理VM等待时间（秒），默认=expunge.interval；类型：整数；默认86400
`expunge.interval`
清理VM线程允许时间间隔（秒）；类型：整数；默认：86400
`expunge.workers`
清理VM线程数；类型：整数；默认：1
external.baremetal.resource.classname    NULL    class name for handling external baremetal resource
external.baremetal.system.url    NULL    url of external baremetal system that CloudStack will talk to
external.firewall.default.capacity    50    default number of networks permitted per external load firewall device
external.lb.default.capacity    50    default number of networks permitted per external load balancer device
external.network.stats.interval    300    Interval (in seconds) to report external network statistics.
extract.url.cleanup.interval    7200    The interval (in seconds) to wait before cleaning up the extract URL's
extract.url.expiration.interval    14400    The life of an extract URL after which it is deleted
guest.domain.suffix    cloud.internal    Default domain name for vms inside virtualized networks fronted by router
guest.vlan.bits    12    The number of bits to reserve for the VLAN identifier in the guest subnet.
`ha.tag`
HA tag，含有该tag的HOST，只能用于HA；类型：字符串；默认：NULL
`ha.workers`
HA线程数；类型：整数；默认：5
healthcheck.update.interval    600    Time Interval to fetch the LB health check states (in sec)
`host`
management Server IP（用于管理网段）；类型：IP；默认：初始化DB的时候自动获取
`host.capacityType.to.order.clusters`
主机资源类型，用于deployment planner分配VM资源时为Cluster排序；类型：CPU/RAM；默认：CPU
`host.reservation.release.period`
主机预留资源检查时间间隔（毫秒）；类型：整数；默认：300000
`host.retry`
在某Host上创建卷的重试此时；类型：整数；默认：2
`host.stats.interval`
Host stats获取时间间隔（毫秒）；类型：整数；默认：60000
`hypervisor.list`
该版本支持的Hyperviser List；类型：KVM,XenServer,VMware,BareMetal,Ovm,LXC；默认：KVM,XenServer,VMware,BareMetal,Ovm,LXC
`incorrect.login.attempts.allowed`
登陆错误尝试次数，超过则user会被禁用；类型：整数；默认：5
`instance.name`
创建VM的名字后缀；类型：字符串；默认：VM
`integration.api.port`
API端口；类型：端口；默认：8096
internallbvm.service.offering    NULL    Uuid of the service offering used by internal lb vm; if NULL - default system internal lb offering will be used
interval.baremetal.securitygroup.agent.echo    10    Interval to echo baremetal security group agent, in seconds
investigate.retry.interval    60    Time (in seconds) between VM pings when agent is disconnected
job.cancel.threshold.minutes    60    Time (in minutes) for async-jobs to be forcely cancelled if it has been in process for long
job.expire.minutes    1440    Time (in minutes) for async-jobs to be kept in system
json.content.type    text/javascript    Http response content type for .js files (default is text/javascript)
`kvm.snapshot.enabled`
是否启用KVM 的VM快照功能；类型：true/false；默认：false
`kvm.ssh.to.agent`
是否允许Management Server以SSH方式登录KVM agent；类型：true/false；默认：true
linkLocalIp.nums    10    The number of link local ip that needed by domR(in power of 2)
`management.network.cidr`
管理网段CIDR；类型：CIDR；默认：自动获取当前host ip的cidr
`max.account.cpus`
一个用户所能分配的最大CPU数量；类型：整数；默认：40
`max.account.memory`
一个用户所能分配的最大内存大小（MB）；类型：整数；默认：40960
`max.account.networks`
一个用户最多能创建的网络数量；类型：整数；默认：20
`max.account.primary.storage`
一个用户所能分配的最大存储大小（GB）；类型：整数；默认：200
`max.account.public.ips`
用户最多拥有的public IP数量；类型：整数；默认：20
`max.account.secondary.storage`
一个用户所能分配的最大二级存储大小（GB）；类型：整数；默认：400
`max.account.snapshots`
用户最多创建的Snapshot数量；类型：整数；默认：20
`max.account.templates`
用户最多创建的模板数量；类型：整数；默认：20
`max.account.user.vms`
用户最多创建的VM数量；类型：整数；默认：20
`max.account.volumes`
用户最多创建的卷数量；类型：整数；默认：20
`max.account.vpcs`
用户最多分配的VCPU数量；类型：整数；默认：20
`max.project.cpus`
一个项目能分配的最大CPU数量；类型：整数；默认：40
`max.project.memory`
一个项目能分配的最大内存大小（MB）；类型：整数；默认：40960
`max.project.networks`
一个项目能创建的最大Network数；类型：整数；默认：20
`max.project.primary.storage`
一个项目能分配的最大存储大小（GB）；类型：整数；默认：200
`max.project.public.ips`
一个项目能拥有的最大public ip数量；类型：整数；默认：20
`max.project.secondary.storage`
一个项目能分配的最大二级存储大小（GB）；类型：整数；默认：400
`max.project.snapshots`
一个project能创建的最大快照数；类型：整数；默认：20
`max.project.templates`
一个project能创建的最大模板数；类型：整数；默认：20
`max.project.user.vms`
一个project能创建的最大VM数；类型：整数；默认：20
`max.project.volumes`
一个project能创建的最大卷数量；类型：整数；默认：20
`max.project.vpcs`
一个project可以创建的最大VPC数；类型：整数；默认：20
`max.template.iso.size`
最大模板/ISOsize（GB）；类型：整数；默认：50
`mem.overprovisioning.factor`
内存超配倍数，内存可用量=内存总量\*超配倍数；类型：整数；默认：1（不超配）
`midonet.apiserver.address`
指定Midonet API Server（如果使用Midonet）；类型：URL；默认：http://localhost:8081
`midonet.providerrouter.id`
使用Midonet的情况下，指定Modonet provider router的uuid；类型：UUID；默认：d7c5e6a3-e2f4-426b-b728-b7ce6a0448e5（未测试，此值来自DB）
`migrate.retry.interval`
migrate重试时间间隔（秒）；类型：整数；默认：120
`migratewait`
migrate超时时间（秒）；类型：整数；默认：3600
`mount.parent`
二级存储在Management Server上的挂载点；类型：Linux 路径；默认：/mnt
network.dhcp.nondefaultnetwork.setgateway.guestos    Windows    The guest OS's name start with this fields would result in DHCP server response gateway information even when the network it's on is not default network. Names are separated by comma.
`network.disable.rpfilter`
Domain Router VM public网络禁用rp\_filter；类型：true/false；默认：true
network.dns.basiczone.updates    all    This parameter can take 2 values: all (default) and pod. It defines if DHCP/DNS requests have to be send to all dhcp servers in cloudstack, or only to the one in the same pod
network.gc.interval    600    Seconds to wait before checking for networks to shutdown
network.gc.wait    600    Time (in seconds) to wait before shutting down a network that's not in used
network.guest.cidr.limit    22    size limit for guest cidr; can't be less than this value
network.ipv6.search.retry.max    10000    The maximum number of retrying times to search for an available IPv6 address in the table
network.loadbalancer.basiczone.elb.enabled    false    Whether the load balancing service is enabled for basic zones
network.loadbalancer.basiczone.elb.gc.interval.minutes    30    Garbage collection interval to destroy unused ELB vms in minutes. Minimum of 5
network.loadbalancer.basiczone.elb.network    guest    Whether the elastic load balancing service public ips are taken from the public or guest network
network.loadbalancer.basiczone.elb.vm.cpu.mhz    128    CPU speed for the elastic load balancer vm
network.loadbalancer.basiczone.elb.vm.ram.size    128    Memory in MB for the elastic load balancer vm
network.loadbalancer.basiczone.elb.vm.vcpu.num    1    Number of VCPU  for the elastic load balancer vm
`network.loadbalancer.haproxy.max.conn`
LB（HAProxy）当前链接的最大数；类型：整数；默认4096
network.loadbalancer.haproxy.stats.auth    admin1:AdMiN123    Load Balancer(haproxy) authetication string in the format username:password
network.loadbalancer.haproxy.stats.port    8081    Load Balancer(haproxy) stats port number.
network.loadbalancer.haproxy.stats.uri    /admin?stats    Load Balancer(haproxy) uri.
network.loadbalancer.haproxy.stats.visibility    global    Load Balancer(haproxy) stats visibilty, the value can be one of the following six parameters : global,guest-network,link-local,disabled,all,default
network.lock.timeout    600    Lock wait timeout (seconds) while implementing network
network.securitygroups.defaultadding    true    If true, the user VM would be added to the default security group by default
network.securitygroups.work.cleanup.interval    120    Time interval (seconds) in which finished work is cleaned up from the work table
network.securitygroups.work.lock.timeout    300    Lock wait timeout (seconds) while updating the security group work queue
network.securitygroups.work.per.agent.queue.size    100    The number of outstanding security group work items that can be queued to a host. If exceeded, work items will get dropped to conserve memory. Security Group Sync will take care of ensuring that the host gets updated eventually
network.securitygroups.workers.pool.size    50    Number of worker threads processing the security group update work queue
network.throttling.rate    200    Default data transfer rate in megabits per second allowed in network.
ping.interval    60    Ping interval in seconds
ping.timeout    2.5    Multiplier to ping.interval before announcing an agent has timed out
`pod.privateip.capacity.notificationthreshold`
POD中私有IP分配率告警值，超过此值则发送Alert；类型：小数（0~1）；默认：0.75
`pool.storage.allocated.capacity.disablethreshold`
主存储已分配比率上限，超过此值则不能继续分配主存储；类型：小数（0~1）；默认：0.85
`pool.storage.capacity.disablethreshold`
主存储已使用比率上限，超过此值则不能继续分配主存储；类型：小数（0~1）；默认：0.85
port    8250    Port to listen on for agent connection.
`primary.storage.download.wait`
在二级存储向主存储传输模板超时时间（秒）；类型：整数；默认10800
project.email.sender    NULL    Sender of project invitation email (will be in the From header of the email)
`project.invite.required`
添加一个用户到project的时候，是否发送请求；类型：true/false；默认：false
`project.invite.timeout`
添加用户邀请超时时间；类型：整数；默认：86400
project.smtp.host    NULL    SMTP hostname used for sending out email project invitations
project.smtp.password    NULL    Password for SMTP authentication (applies only if project.smtp.useAuth is true)
project.smtp.port    465    Port the SMTP server is listening on
project.smtp.useAuth    NULL    If true, use SMTP authentication when sending emails
project.smtp.username    NULL    Username for SMTP authentication (applies only if project.smtp.useAuth is true)
`recreate.systemvm.enabled`
是否在启动系统虚拟机的时候，重建root卷；类型：true/false；默认：false
remote.access.vpn.client.iprange    10.1.2.1-10.1.2.8    The range of ips to be allocated to remote access vpn clients. The first ip in the range is used by the VPN server
remote.access.vpn.psk.length    24    The length of the ipsec preshared key (minimum 8, maximum 256)
remote.access.vpn.user.limit    8    The maximum number of VPN users that can be created per account
resourcecount.check.interval    0    Time (in seconds) to wait before retrying resource count check task. Default is 0 which is to never run the task
`restart.retry.interval`
VM重启超时时间（秒）；类型：整数；默认：600
router.check.interval    30    Interval (in seconds) to report redundant router status.
router.check.poolsize    10    Numbers of threads using to check redundant router status.
`router.cpu.mhz`
vrouter默认CPU速度（MHz）；类型：整数；默认：500
router.extra.public.nics    2    specify extra public nics used for virtual router(up to 5)
router.stats.interval    300    Interval (in seconds) to report router statistics.
`router.template.hyperv`
HyperV环境的vrouter模板名字；类型：模板名字；默认：SystemVM Template (HyperV)
`router.template.kvm`
KVM环境的vrouter模板名字；类型：模板名字；默认：SystemVM Template (KVM)
`router.template.lxc`
LXC环境的vrouter模板名字；类型：模板名字；默认：SystemVM Template (LXC)
`router.template.vmware`
Vmware环境的vrouter模板；类型：模板名字；默认：SystemVM Template (vSphere)
`router.template.xen`
XenServer环境的vrouter模板；类型：模板名字；默认：SystemVM Template (XenServer)
`s3.rrs.enabled`
启用S3 RRS；类型：true/false；默认false
s3.singleupload.max.size    5    The maximum size limit for S3 single part upload API(in GB). If it is set to 0, then it means always use multi-part upload to upload object to S3. If it is set to -1, then it means always use single-part upload to upload object to S3.
scale.retry    2    Number of times to retry scaling up the vm
`sdn.ovs.controller`
对L2-in-L3网络，启用Open vSwitch SDN controller；类型：true/false；默认：false
`sdn.ovs.controller.default.label`
对GRE endpoint使用网卡的默认Network label；类型：Network Label；默认cloud-public
`secstorage.allowed.internal.sites`
环境中，private IP相同网段上传模板/ISO需要在此设置该网段的CIDR，以逗号分隔，0.0.0.0是非法字段
secstorage.capacity.standby    10    The minimal number of command execution sessions that system is able to serve immediately(standby capacity)
secstorage.cmd.execution.time.max    30    The max command execution time in minute
secstorage.encrypt.copy    true    Use SSL method used to encrypt copy traffic between zones
`secstorage.proxy`
二级存储虚拟机代理；类型：http://username:password@proxyserver:port；默认：NULL
`secstorage.service.offering`
二级存储虚拟机计算服务类型；类型：计算服务UUID；默认NULL（使用默认服务）
secstorage.session.max    50    The max number of command execution sessions that a SSVM can handle
secstorage.ssl.cert.domain    realhostip.com    SSL certificate used to encrypt copy traffic between zones
secstorage.vm.mtu.size    1500    MTU size (in Byte) of storage network in secondary storage vms
security.singlesignon.key    s3ZbaX1\_Oc1scuMuT3MDsKYUIRtF1ob1e2AtTYFLjZp-NPQwJa4g\_PYsQwodJxV8h5qXNnkGPaSmbUsnX7z\_kQ    A Single Sign-On key used for logging into the cloud
security.singlesignon.tolerance.millis    300000    The allowable clock difference in milliseconds between when an SSO login request is made and when it is received.
site2site.vpn.customergateway.subnets.limit    10    The maximum number of subnets per customer gateway
site2site.vpn.vpngateway.connection.limit    4    The maximum number of VPN connection per VPN gateway
`snapshot.backup.rightafter`
在Snapshot完成后，立刻进行备份；类型：true/false；默认：true
`snapshot.delta.max`
两次全量快照之间，最多的增量快照数；类型：整数；默认：16
`snapshot.max.daily`
每天最多快照数；类型：整数；默认：8
`snapshot.max.hourly`
每小时最多快照数；类型：整数；默认：8
`snapshot.max.monthly`
每月最多快照数；类型：整数；默认：8
`snapshot.max.weekly`
每周最多快照数；类型：整数；默认：8
snapshot.poll.interval    300    The time interval in seconds when the management server polls for snapshots to be scheduled.
sortkey.algorithm    false    Sort algorithm for those who use sort key(template, disk offering, service offering, network offering), true means ascending sort while false means descending sort
`start.retry`
Create 和Start VM重试次数；类型：整数；默认：10
`stop.retry.interval`
两次重试Stop或Destroy VM的间隔时间（秒）；类型：整数；默认：600
storage.cache.replacement.enabled    true    enable or disable cache storage replacement algorithm.
storage.cache.replacement.interval    86400    time interval between cache replacement threads (in seconds).
storage.cache.replacement.lru.interval    30    time interval for unused data on cache storage (in days).
`storage.cleanup.enabled`
启用清理存储线程；类型：true/false；默认：true
`storage.cleanup.interval`
清理存储线程运行时间间隔（秒）；类型：整数；默认：86400
`storage.max.volume.size`
volume最大size（GB）；类型：整数；默认：2000
`storage.max.volume.upload.size`
上传Volume最大size（GB）；类型：整数；默认：500
`storage.overprovisioning.factor`
主存储超配倍数，主存储可用量=主存储总量\*超配倍数；类型：整数；默认：2
storage.pool.max.waitseconds    3600    Timeout (in seconds) to synchronize storage pool operations.
storage.stats.interval    60000    The interval (in milliseconds) when storage stats (per host) are retrieved from agents.
storage.template.cleanup.enabled    true    Enable/disable template cleanup activity, only take effect when overall storage cleanup is enabled
`sync.interval`
集群状态sync时间间隔（秒）；类型：整数；默认：60
system.vm.auto.reserve.capacity    true    Indicates whether or not to automatically reserver system VM standby capacity.
system.vm.default.hypervisor    NULL    Hypervisor type used to create system vm
`system.vm.random.password`
系统虚拟机第一次启动时自动修改随机密码；类型：true/false；默认：false
`system.vm.use.local.storage`
系统虚拟机使用本地存储；类型：true/false；默认：false
task.cleanup.retry.interval    600    Time (in seconds) to wait before retrying cleanup of tasks if the cleanup failed previously.  0 means to never retry.
timeout.baremetal.securitygroup.agent.echo    3600    Timeout to echo baremetal security group agent, in seconds, the provisioning process will be treated as a failure
total.retries    4    The number of times each command sent to a host should be retried in case of failure.
traffic.sentinel.exclude.zones        Traffic going into specified list of zones is not metered
traffic.sentinel.include.zones    EXTERNAL    Traffic going into specified list of zones is metered. For metering all traffic leave this parameter empty
ucs.sync.blade.interval    3600    the interval cloudstack sync with UCS manager for available blades in case user remove blades from chassis without notifying CloudStack
update.wait    600    Time to wait (in seconds) before alerting on a updating agent
usage.aggregation.timezone    GMT    The timezone to use for usage stats aggregation
usage.execution.timezone    NULL    The timezone to use for usage job execution time
usage.sanity.check.interval    NULL    Interval (in days) to check sanity of usage data
usage.stats.job.aggregation.range    1440    The range of time for aggregating the user statistics specified in minutes (e.g. 1440 for daily, 60 for hourly.
usage.stats.job.exec.time    00:15    The time at which the usage statistics aggregation job will run as an HH24:MM time, e.g. 00:30 to run at 12:30am.
use.external.dns    false    Bypass internal dns, use external dns1 and dns2
use.system.guest.vlans    true    If true, when account has dedicated guest vlan range(s), once the vlans dedicated to the account have been consumed vlans will be allocated from the system pool
use.system.public.ips    true    If true, when account has dedicated public ip range(s), once the ips dedicated to the account have been consumed ips will be acquired from the system pool
`vm.allocation.algorithm`
vm分配算法；类型：'random', 'firstfit', 'userdispersing', 'userconcentratedpod\_random', 'userconcentratedpod\_firstfit' ；默认：random
`vm.deployment.planner`
vm部署策略；类型：'FirstFitPlanner', 'UserDispersingPlanner', 'UserConcentratedPodPlanner'；默认：FirstFitPlaller
vm.destroy.forcestop    false    On destroy, force-stop takes this value
`vm.disk.stats.interval`
vm磁盘状态获取的时间间隔；类型：整数；默认：0（不获取状态）
`vm.disk.throttling.bytes_read_rate`
vm磁盘读速度限制（bytes/second）；类型：整数；默认：0（不限制）
`vm.disk.throttling.bytes_write_rate`
vm磁盘写速度限制（bytes/second）；类型：整数；默认：0（不限制）
`vm.disk.throttling.iops_read_rate`
vm磁盘每秒读请求次数限制；类型：整数；默认：0（不限制）
`vm.disk.throttling.iops_write_rate`
vm磁盘每秒写请求次数限制；类型：整数；默认：0（不限制）
vm.instancename.flag    false    If set to true, will set guest VM's name as it appears on the hypervisor, to its hostname
vm.network.throttling.rate    200    Default data transfer rate in megabits per second allowed in User vm's default network.
vm.op.cancel.interval    3600    Time (in seconds) to wait before cancelling a operation
vm.op.cleanup.interval    86400    Interval to run the thread that cleans up the vm operations (in seconds)
vm.op.cleanup.wait    3600    Time (in seconds) to wait before cleanuping up any vm work items
vm.op.lock.state.retry    5    Times to retry locking the state of a VM for operations
vm.op.wait.interval    120    Time (in seconds) to wait before checking if a previous operation has succeeded
`vm.stats.interval`
vm当前状态获取时间间隔（毫秒）；类型：整数；默认：60000
vm.tranisition.wait.interval    3600    Time (in seconds) to wait before taking over a VM in transition state
vm.user.dispersion.weight    1    Weight for user dispersion heuristic (as a value between 0 and 1) applied to resource allocation during vm deployment. Weight for capacity heuristic will be (1 - weight of user dispersion)
`vmsnapshot.create.wait`
Vmware虚拟机快照创建超时时间（秒）；类型：整数；默认：1800
`vmsnapshot.max`
一台Vmware虚拟机拥有的最大快照数量（虚拟机快照）；类型：整数；默认：10
vmware.additional.vnc.portrange.size    1000    Start port number of additional VNC port range
vmware.additional.vnc.portrange.start    50000    Start port number of additional VNC port range
`vmware.create.full.clone`
Vmware虚拟机创建模式（full clone），如果true，则创建vm的时候，磁盘完整复制，如果false则以delta格式创建；类型：true/false；默认：true
vmware.hung.wokervm.timeout    7200    Worker VM timeout in seconds
vmware.management.portgroup    Management Network    Specify the management network name(for ESXi hosts)
`vmware.nested.virtualization`
启用Vmware嵌套虚拟化；类型：true/false；默认：false
vmware.ports.per.dvportgroup    256    Default number of ports per Vmware dvPortGroup in VMware environment
vmware.recycle.hung.wokervm    false    Specify whether or not to recycle hung worker VMs
vmware.reserve.cpu    false    Specify whether or not to reserve CPU based on CPU overprovisioning factor
vmware.reserve.mem    false    Specify whether or not to reserve memory based on memory overprovisioning factor
`vmware.root.disk.controller`
Vmware环境中VM Root卷类型；类型：scsi, ide；默认：ide
vmware.service.console    Service Console    Specify the service console network name(for ESX hosts)
`vmware.systemvm.nic.device.type`
Vmware环境中，system vm网卡类型；类型：E1000, PCNet32, Vmxnet2, Vmxnet3；默认：E1000
`vmware.use.dvswitch`
Vmware环境中，启动或禁用 Nexus/Vmware dvSwitch；类型：true/false；默认：false
`vmware.use.nexus.vswitch`
Vmware环境中，启动或禁用 Cisco Nexus 1000v vSwitch；类型：true/false；默认：false
vpc.cleanup.interval    3600    The interval (in seconds) between cleanup for Inactive VPCs
vpc.max.networks    3    Maximum number of networks per vpc
`wait`
control commands返回超时时间（秒）；类型：整数；默认：1800
workers    5    Number of worker threads.
`xapiwait`
Xenserver API返回超时时间（秒）；类型：整数；默认：600
xen.bond.storage.nics    NULL    Attempt to bond the two networks if found
`xen.heartbeat.interval`
XenServer自检间隔时间（秒）；类型：整数；默认：60
`xen.nics.max`
XenServer VM 允许的最大网卡数；类型：整数；默认：7
`xen.pvdriver.version`
XenServer环境中，pvdriver版本；类型：xenserver56,xenserver61；默认：xenserver61
xen.setup.multipath    false    Setup the host to do multipath
zone.directnetwork.publicip.capacity.notificationthreshold    0.75    Percentage (as a value between 0 and 1) of Direct Network Public Ip Utilization above which alerts will be sent about low number of direct network public ips.
zone.secstorage.capacity.notificationthreshold    0.75    Percentage (as a value between 0 and 1) of secondary storage utilization above which alerts will be sent about low storage available.
zone.virtualnetwork.publicip.capacity.notificationthreshold    0.75    Percentage (as a value between 0 and 1) of public IP address space utilization above which alerts will be sent.
zone.vlan.capacity.notificationthreshold    0.75    Percentage (as a value between 0 and 1) of Zone Vlan utilization above which alerts will be sent about low number of Zone Vlans.
