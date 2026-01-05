---
title: "CloudStack DB表结构"
date: "2015-08-24 08:29:34"
slug: "post-520"
layout: "post"
categories: ["CloudStack"]
tags: ["CloudStack", "Database"]
draft: true
lang: zh
permalink: /zh/post-520/
translations:
  zh: /zh/post-520/
---
CloudStack 有3个DB，分别为：cloud、cloud_usage、cloudbridge。    
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
account_details 账户属性：以key-value格式，记录账户属性。  
account_view 账户视图：记录账户当前所有资源信息，所属domain，所有vm，template，network等资源的数量和Limit，现有正在运行的job等。  
account_vmstats_view：account 所有的vm数量。  
account_netstats_view：记录account网络流量信息。  
account_network_ref：account和network的映射关系，账户所能访问的network。  
account_vlan_map:  account和vlan的映射关系，账户所有的vlan ID。  
account_vnet_map：account和physical_network的映射关系。  
domain 域：用户域信息，默认域为ROOT。  
domain_network_ref：domain和network的映射关系，子域的访问权限。  
user 用户：记录account 下所有user 信息，邮箱、登陆密码等。  
user_details 用户属性：以key-value格式，记录user属性。  
user_view :用户视图。  
user_statistics： 用户统计信息，网络流量统计等。  
projects：项目，项目是一个特殊的account，可以多个account共享vm。  
project_view：项目视图。  
project_account：项目和account的映射关系。  
project_account_view：project和account的映射关系视图。  
project_invitations：project 验证登陆信息。  
project_invitation_view：project 验证登陆视图。  
IAM：*Identity* & *Access* Management（访问权限管理）  
iam_account_policy_map：登陆控制策略。  
iam_group：访问权限控制group，分为User,Admin,Domain Admin等，每个group权限不同。  
iam_group_account_map：iam group和 account 的映射。  
iam_group_policy_map：group iam policy的映射。  
iam_policy：iam 策略。  
iam_policy_permission：iam 策略访问许可。  

# Affinity Group：

affinity_group：关联性组。  
affinity_group_domain_map：affinity_group 和 domain的映射关系，subdomain的访问权限。   
affinity_group_vm_map：affinity_group 和 vm 的映射关系。  
affinity_group_view：affinity_group当前视图，account、domain、vm信息。  

# 管理节点：

mshost  
mshost_peer  

# 事件/警告：

alert：警告。  
event：事件（操作）。  
event_view：事件视图，事件相关属性等信息。  

# Async Job:

async_job：异步任务。  
async_job_join_map：异步任务调度、状态等信息。  
async_job_journal：  
async_job_view：异步任务视图，job的account，domain，user，vm等信息。

# DataCenter:

data_center：Zone 信息。  
data_center_details：以key-value形式记录zone 属性。  
dc_storage_network_ip_range：zone所有的storage network ip。  
data_center_view：Zone 视图。

# Pod:

host_pod_ref：Pod 信息  
pod_vlan_map：pod 和 vlan映射，

# Cluster:

cluster：cluster 信息。  
cluster_details：以key-value形式记录cluster 属性。

# Host:

host：主机信息。  
host_details：以key-value形式记录host 属性。  
host_gpu_groups：主机的gpu group（目前之用于XenServer）。  
host_tags：host 标签，每行对应一个host的一个标签，每个host可能有多行即多个标签。  
host_view：host视图，host属性和运行时状态信息。  
hypervisor_capabilities：Hypervisor属性，是否支持安全组、迁移、vm快照等。  

# 网络：

vlan: vlan信息，所属zone，物理网络等。  
network_acl：访问控制权限列表  
network_acl_details：  
network_acl_item：  
network_acl_item_details：  
network_acl_item_cidrs：  
networks：网络  
network_details：  
network_rule_config：  
physical_network：  
physical_network_isolation_methods：  
physical_network_service_providers：  
physical_network_tags：  
physical_network_traffic_types：  
nics  
nic_details  
nic_ip_alias  
nic_secondary_ips  
ntwk_offering_service_map  
ntwk_service_map  
user_ip_address  
user_ip_address_details  
user_ipv6_address  

# AutoScale:

autoscale_policies：  
autoscale_policy_condition_map：  
autoscale_vmgroup_details：  
autoscale_vmgroup_policy_map：  
autoscale_vmgroup_vm_map：  
autoscale_vmgroups：  
autoscale_vmprofile_details：  
autoscale_vmprofiles：  

# baremetal:

baremetal_dhcp_devices：  
baremetal_pxe_devices：

# Offering:

disk_offering  
disk_offering_details  
disk_offering_view  
service_offering  
service_offering_details  
service_offering_view  
network_offerings：网络服务（Public,Guset,Private 等）  
network_offering_details：

# 系统虚拟机：

console_proxy  
domain_router  
domain_router_view  
secondary_storage_vm  

# 主存储/二级存储:

storage_pool  
storage_pool_details  
storage_pool_host_ref  
storage_pool_view  
storage_pool_work  
swift

# 虚拟机：

vm_instance：所有vm  
user_vm：用户vm  
user_vm_details  
user_vm_view  
user_vm_clone_setting：vm是full-clone（磁盘）或者fast-clone（只做映射）  
vm_compute_tags  
vm_disk_statistics  
vm_network_map  
vm_reservation：预留vm  
vm_root_disk_tags  
vm_work_job  
vmware_data_center：vmware 集群  
vmware_data_center_zone_map：vmware集群和zone的对应关系  
volumes：卷  
volume_details  
volume_view  
volume_store_ref ：要下载或上传的卷在二级存储中的位置  
volume_host_ref：卷下载过程中，操作的host和进度  
volume_reservation：预留卷  

# 虚拟机资源：

resource_count：用户资源使用量。  
resource_limit：用户自由限制（vm个数，snapshot个数等）  
resource_tags：资源  
resource_tag_view：

# 模板/快照:

snapshots：卷快照，将磁盘状态备份到二级存储。  
snapshot_details  
snapshot_schedule：定时卷快照策略。  
snapshot_store_ref：卷快照，磁盘映射和快照基本信息。  
vm_snapshots：vm 快照  
vm_snapshot_details  
vm_template：vm 模板  
vm_template_details   
template_view：vm模板视图    
template_host_ref：模板和正在操作该模板的ssvm的映射  
template_s3_ref：模板和存放模板的s3存储的映射  
template_spool_ref：模板存放到Primary Stroage中建立的映射  
template_store_ref：模板下载进度信息  
template_swift_ref：模板和存放模板的swift的映射  
template_zone_ref：模板和zone的映射  
launch_permission：模板和可访问该模板的用户之间的映射

# Guest OS:

guest_os：VM 操作系统  
guest_os_category：VM 操作系统分类  
guest_os_hypervisor：hypervisor 支持的VM 操作系统

# 安全组/防火墙/端口映射/LB:

security_group：安全组  
security_group_rule：安全组规则  
security_group_view  
security_group_vm_map：安全组和vm的映射关系  
firewall_rules：防火墙规则  
firewall_rule_details  
firewall_rules_cidrs：防火墙规则的source_cidr  
load_balancing_rules：负载均衡策略  
load_balancer_cert_map  
load_balancer_vm_map  
load_balancer_healthcheck_policies  
load_balancer_healthcheck_policy_details  
load_balancer_stickiness_policies  
load_balancer_stickiness_policy_details  
global_load_balancing_rules：全局负载均衡规则  
global_load_balancer_lb_rule_map  
port_forwarding_rules：端口转发规则

# SDN：

nicira_nvp_nic_map  
nicira_nvp_router_map  
ovs_providers  
ovs_tunnel_interface  
ovs_tunnel_network  

# VPN:

remote_access_vpn  
remote_access_vpn_details  
vpn_users  
s2s_customer_gateway  
s2s_customer_gateway_details  
s2s_vpn_connection  
s2s_vpn_connection_details  
s2s_vpn_gateway  
s2s_vpn_gateway_details  

# Operation:

op_dc_ip_address_alloc  
op_dc_link_local_ip_address_alloc  
op_dc_storage_network_ip_address  
op_dc_vnet_alloc  
op_ha_work：VM HA线程，包括HA，Start，Stop，Migrate等HA相关长操作  
op_host  
op_host_capacity  
op_host_planner_reservation  
op_host_transfer  
op_host_upgrade  
op_it_work：虚拟机迁移，修改配置等长操作  
op_lock  
op_networks  
op_nwgrp_work  
op_pod_vlan_alloc  
op_router_monitoring_services  
op_user_stats_log  
op_vm_ruleset_log  
op_vpc_distributed_router_sequence_no  

# 设备：

s3  
ucs_blade  
ucs_manager  
netapp_lun  
netapp_pool  
netapp_volume  
netscaler_pod_ref  
cluster_vsm_map：cluster和 vsm 的映射关系，vsm是Nexus的虚拟机监控模块，也是一个运行的虚拟机。  
network_asa1000v_map：  
network_external_lb_device_map：  
network_external_firewall_device_map：  
external_bigswitch_vns_devices  
external_cisco_asa1000v_devices  
external_cisco_vnmc_devices  
external_firewall_devices  
external_load_balancer_devices  
external_nicira_nvp_devices  
external_opendaylight_controllers  
external_stratosphere_ssp_credentials  
external_stratosphere_ssp_tenants  
external_stratosphere_ssp_uuids  

# Other:

configuration：全局配置  
version：版本，每一次升级都有一条记录，以最后一个为当前版本  
ldap_configuration：ldap 登陆认证配置  
vgpu_types  
cmd_exec_log  
conditions  
counter  
dedicated_resources  
elastic_lb_vm_map  
image_store  
image_store_details  
image_store_view  
inline_load_balancer_nic_map  
instance_group  
instance_group_view  
instance_group_vm_map  
keystore  
legacy_zones  
monitoring_services  
object_datastore_ref  
port_profile  
portable_ip_address  
portable_ip_range  
private_ip_address  
free_ip_view  
region  
router_network_ref  
sequence  
ssh_keypairs  
sslcerts  
stack_maid  
static_routes  
sync_queue  
sync_queue_item  
upload  
usage_event  
usage_event_details  
virtual_router_providers  
virtual_supervisor_module  
vpc  
vpc_details  
vpc_gateway_details  
vpc_gateways  
vpc_offering_service_map  
vpc_offerings  
vpc_service_map  
