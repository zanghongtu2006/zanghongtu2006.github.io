---
title: "CloudStack DB表结构"
date: "2015-08-24 08:29:34"
slug: "post-520"
layout: "post"
categories: ["CloudStack"]
tags: ["CloudStack", "Database"]
draft: true
---
CloudStack 有3个DB，分别为：cloud、cloud\_usage、cloudbridge。
其中 cloudstack 表为CloudStack的主数据库，存放CloudStack 运行相关所有数据，其中共有265个表。
cloudstack 中的表分为以下几类：
实体（对应CS中的物理资源和虚拟资源）此类数据永不删除db，删除时只将表中removed项设置为当前时间戳；
Details（属性），以key-value格式存储实体的属性信息；
Ref（实体和实体之间的关系），随业务逻辑添加或删除；
Op（操作记录等）完成即删除;
View（Mysql视图），暴露给统计等业务使用，存放使用量或当前运行量等信息。
下面分类来看一下cloudstack 库中的这265个表。

# 认证管理：

account 账户：记录登陆账户信息，账户所属domain，状态等信息。
account\_details 账户属性：以key-value格式，记录账户属性。
account\_view 账户视图：记录账户当前所有资源信息，所属domain，所有vm，template，network等资源的数量和Limit，现有正在运行的job等。
account\_vmstats\_view：account 所有的vm数量。
account\_netstats\_view：记录account网络流量信息。
account\_network\_ref：account和network的映射关系，账户所能访问的network。
account\_vlan\_map:  account和vlan的映射关系，账户所有的vlan ID。
account\_vnet\_map：account和physical\_network的映射关系。
domain 域：用户域信息，默认域为ROOT。
domain\_network\_ref：domain和network的映射关系，子域的访问权限。
user 用户：记录account 下所有user 信息，邮箱、登陆密码等。
user\_details 用户属性：以key-value格式，记录user属性。
user\_view :用户视图。
user\_statistics： 用户统计信息，网络流量统计等。
projects：项目，项目是一个特殊的account，可以多个account共享vm。
project\_view：项目视图。
project\_account：项目和account的映射关系。
project\_account\_view：project和account的映射关系视图。
project\_invitations：project 验证登陆信息。
project\_invitation\_view：project 验证登陆视图。
IAM：*Identity* & *Access* Management（访问权限管理）
iam\_account\_policy\_map：登陆控制策略。
iam\_group：访问权限控制group，分为User,Admin,Domain Admin等，每个group权限不同。
iam\_group\_account\_map：iam group和 account 的映射。
iam\_group\_policy\_map：group iam policy的映射。
iam\_policy：iam 策略。
iam\_policy\_permission：iam 策略访问许可。

# Affinity Group：

affinity\_group：关联性组。
affinity\_group\_domain\_map：affinity\_group 和 domain的映射关系，subdomain的访问权限。
affinity\_group\_vm\_map：affinity\_group 和 vm 的映射关系。
affinity\_group\_view：affinity\_group当前视图，account、domain、vm信息。

# 管理节点：

mshost
mshost\_peer

# 事件/警告：

alert：警告。
event：事件（操作）。
event\_view：事件视图，事件相关属性等信息。

# Async Job:

async\_job：异步任务。
async\_job\_join\_map：异步任务调度、状态等信息。
async\_job\_journal：
async\_job\_view：异步任务视图，job的account，domain，user，vm等信息。

# DataCenter:

data\_center：Zone 信息。
data\_center\_details：以key-value形式记录zone 属性。
dc\_storage\_network\_ip\_range：zone所有的storage network ip。
data\_center\_view：Zone 视图。

# Pod:

host\_pod\_ref：Pod 信息
pod\_vlan\_map：pod 和 vlan映射，

# Cluster:

cluster：cluster 信息。
cluster\_details：以key-value形式记录cluster 属性。

# Host:

host：主机信息。
host\_details：以key-value形式记录host 属性。
host\_gpu\_groups：主机的gpu group（目前之用于XenServer）。
host\_tags：host 标签，每行对应一个host的一个标签，每个host可能有多行即多个标签。
host\_view：host视图，host属性和运行时状态信息。
hypervisor\_capabilities：Hypervisor属性，是否支持安全组、迁移、vm快照等。

# 网络：

vlan: vlan信息，所属zone，物理网络等。
network\_acl：访问控制权限列表
network\_acl\_details：
network\_acl\_item：
network\_acl\_item\_details：
network\_acl\_item\_cidrs：
networks：网络
network\_details：
network\_rule\_config：
physical\_network：
physical\_network\_isolation\_methods：
physical\_network\_service\_providers：
physical\_network\_tags：
physical\_network\_traffic\_types：
nics
nic\_details
nic\_ip\_alias
nic\_secondary\_ips
ntwk\_offering\_service\_map
ntwk\_service\_map
user\_ip\_address
user\_ip\_address\_details
user\_ipv6\_address

# AutoScale:

autoscale\_policies：
autoscale\_policy\_condition\_map：
autoscale\_vmgroup\_details：
autoscale\_vmgroup\_policy\_map：
autoscale\_vmgroup\_vm\_map：
autoscale\_vmgroups：
autoscale\_vmprofile\_details：
autoscale\_vmprofiles：

# baremetal:

baremetal\_dhcp\_devices：
baremetal\_pxe\_devices：

# Offering:

disk\_offering
disk\_offering\_details
disk\_offering\_view
service\_offering
service\_offering\_details
service\_offering\_view
network\_offerings：网络服务（Public,Guset,Private 等）
network\_offering\_details：

# 系统虚拟机：

console\_proxy
domain\_router
domain\_router\_view
secondary\_storage\_vm

# 主存储/二级存储:

storage\_pool
storage\_pool\_details
storage\_pool\_host\_ref
storage\_pool\_view
storage\_pool\_work
swift

# 虚拟机：

vm\_instance：所有vm
user\_vm：用户vm
user\_vm\_details
user\_vm\_view
user\_vm\_clone\_setting：vm是full-clone（磁盘）或者fast-clone（只做映射）
vm\_compute\_tags
vm\_disk\_statistics
vm\_network\_map
vm\_reservation：预留vm
vm\_root\_disk\_tags
vm\_work\_job
vmware\_data\_center：vmware 集群
vmware\_data\_center\_zone\_map：vmware集群和zone的对应关系
volumes：卷
volume\_details
volume\_view
volume\_store\_ref ：要下载或上传的卷在二级存储中的位置
volume\_host\_ref：卷下载过程中，操作的host和进度
volume\_reservation：预留卷

# 虚拟机资源：

resource\_count：用户资源使用量。
resource\_limit：用户自由限制（vm个数，snapshot个数等）
resource\_tags：资源
resource\_tag\_view：

# 模板/快照:

snapshots：卷快照，将磁盘状态备份到二级存储。
snapshot\_details
snapshot\_schedule：定时卷快照策略。
snapshot\_store\_ref：卷快照，磁盘映射和快照基本信息。
vm\_snapshots：vm 快照
vm\_snapshot\_details
vm\_template：vm 模板
vm\_template\_details
template\_view：vm模板视图
template\_host\_ref：模板和正在操作该模板的ssvm的映射
template\_s3\_ref：模板和存放模板的s3存储的映射
template\_spool\_ref：模板存放到Primary Stroage中建立的映射
template\_store\_ref：模板下载进度信息
template\_swift\_ref：模板和存放模板的swift的映射
template\_zone\_ref：模板和zone的映射
launch\_permission：模板和可访问该模板的用户之间的映射

# Guest OS:

guest\_os：VM 操作系统
guest\_os\_category：VM 操作系统分类
guest\_os\_hypervisor：hypervisor 支持的VM 操作系统

# 安全组/防火墙/端口映射/LB:

security\_group：安全组
security\_group\_rule：安全组规则
security\_group\_view
security\_group\_vm\_map：安全组和vm的映射关系
firewall\_rules：防火墙规则
firewall\_rule\_details
firewall\_rules\_cidrs：防火墙规则的source\_cidr
load\_balancing\_rules：负载均衡策略
load\_balancer\_cert\_map
load\_balancer\_vm\_map
load\_balancer\_healthcheck\_policies
load\_balancer\_healthcheck\_policy\_details
load\_balancer\_stickiness\_policies
load\_balancer\_stickiness\_policy\_details
global\_load\_balancing\_rules：全局负载均衡规则
global\_load\_balancer\_lb\_rule\_map
port\_forwarding\_rules：端口转发规则

# SDN：

nicira\_nvp\_nic\_map
nicira\_nvp\_router\_map
ovs\_providers
ovs\_tunnel\_interface
ovs\_tunnel\_network

# VPN:

remote\_access\_vpn
remote\_access\_vpn\_details
vpn\_users
s2s\_customer\_gateway
s2s\_customer\_gateway\_details
s2s\_vpn\_connection
s2s\_vpn\_connection\_details
s2s\_vpn\_gateway
s2s\_vpn\_gateway\_details

# Operation:

op\_dc\_ip\_address\_alloc
op\_dc\_link\_local\_ip\_address\_alloc
op\_dc\_storage\_network\_ip\_address
op\_dc\_vnet\_alloc
op\_ha\_work：VM HA线程，包括HA，Start，Stop，Migrate等HA相关长操作
op\_host
op\_host\_capacity
op\_host\_planner\_reservation
op\_host\_transfer
op\_host\_upgrade
op\_it\_work：虚拟机迁移，修改配置等长操作
op\_lock
op\_networks
op\_nwgrp\_work
op\_pod\_vlan\_alloc
op\_router\_monitoring\_services
op\_user\_stats\_log
op\_vm\_ruleset\_log
op\_vpc\_distributed\_router\_sequence\_no

# 设备：

s3
ucs\_blade
ucs\_manager
netapp\_lun
netapp\_pool
netapp\_volume
netscaler\_pod\_ref
cluster\_vsm\_map：cluster和 vsm 的映射关系，vsm是Nexus的虚拟机监控模块，也是一个运行的虚拟机。
network\_asa1000v\_map：
network\_external\_lb\_device\_map：
network\_external\_firewall\_device\_map：
external\_bigswitch\_vns\_devices
external\_cisco\_asa1000v\_devices
external\_cisco\_vnmc\_devices
external\_firewall\_devices
external\_load\_balancer\_devices
external\_nicira\_nvp\_devices
external\_opendaylight\_controllers
external\_stratosphere\_ssp\_credentials
external\_stratosphere\_ssp\_tenants
external\_stratosphere\_ssp\_uuids

# Other:

configuration：全局配置
version：版本，每一次升级都有一条记录，以最后一个为当前版本
ldap\_configuration：ldap 登陆认证配置
vgpu\_types
cmd\_exec\_log
conditions
counter
dedicated\_resources
elastic\_lb\_vm\_map
image\_store
image\_store\_details
image\_store\_view
inline\_load\_balancer\_nic\_map
instance\_group
instance\_group\_view
instance\_group\_vm\_map
keystore
legacy\_zones
monitoring\_services
object\_datastore\_ref
port\_profile
portable\_ip\_address
portable\_ip\_range
private\_ip\_address
free\_ip\_view
region
router\_network\_ref
sequence
ssh\_keypairs
sslcerts
stack\_maid
static\_routes
sync\_queue
sync\_queue\_item
upload
usage\_event
usage\_event\_details
virtual\_router\_providers
virtual\_supervisor\_module
vpc
vpc\_details
vpc\_gateway\_details
vpc\_gateways
vpc\_offering\_service\_map
vpc\_offerings
vpc\_service\_map
