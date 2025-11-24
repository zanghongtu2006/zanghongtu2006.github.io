---
layout: post
lang: zh
title: "使用Kolla Ansible 安装一台All-in-one的OpenStack GPU服务器"
date: "2025-11-24 23:28:47"
slug: "openstack-kolla-ansible-installation"
translations:
  en: /en/openstack-kolla-ansible-installation/
  de: /de/openstack-kolla-ansible-installation/
categories: ["OpenStack"]
tags: ["OpenStack", "Kolla"]
---
前几天拿到了客户的一台GPU服务器，客户的要求是希望安装部署一套All-in-one 的OpenStack环境，可以供后端服务联调测试。
查看一下服务器当前状态。
# 检查机器状态
```
# ip a
```
双网卡，一个带公网IP，可以给我连接进去。
```
# nvidia-smi 
```
8个5090 显卡，这应该是本人见过第二高配的服务器了。客户确实比较富裕，上次是8个H100.
```
# uname -a
Linux serv-gpu-1 6.8.0-86-generic #87-Ubuntu SMP PREEMPT_DYNAMIC Mon Sep 22 18:03:36 UTC 2025 x86_64 x86_64 x86_64 GNU/Linux
```
*Ubuntu 24.04 LTS* ，当前OpenStack版本应该是 *rocky* ，这个版本如果装在24.04上面可能遇到各种未知问题。
# 开始安装
接下来开始安装，按照官网教程步骤执行
## 基础环境
```
安装依赖
# sudo apt install git python3-dev libffi-dev gcc libssl-dev libdbus-glib-1-dev
安装python venv
# sudo apt install python3-venv
创建python运行环境
# python3 -m venv /opt/openstack/kolla/venv
# source /opt/openstack/kolla/venv/bin/activate
# pip install -U pip
安装kolla依赖
# pip install git+https://opendev.org/openstack/kolla-ansible@master
安装kolla
# sudo mkdir -p /etc/kolla
# sudo chown $USER:$USER /etc/kolla
# cp -r /opt/openstack/kolla/venv/share/kolla-ansible/etc_examples/kolla/* /etc/kolla
# cp /opt/openstack/kolla/venv/share/kolla-ansible/ansible/inventory/all-in-one .
# kolla-ansible install-deps
创建各个服务的密码
# kolla-genpwd
```
这之前所有步骤顺利完成。  
系统比较纯净，还没有太多人使用过，所以没有特别奇怪的依赖错误。
## 编辑globals.yml
接下来编辑/etc/kolla/globals.yml  
按照教程，编辑网络信息等等。  
因为是All-in-one环境，用来做开发测试，而且网卡部署也不支持我们做HA，所以需要关掉HA，使用本机IP代替VIP
```
kolla_base_distro: "rocky"
network_interface: "eth0"
api_interface: "eth0"
neutron_external_interface: "eth1"
kolla_external_vip_address: "192.168.0.1"
neutron_plugin_agent: "openvswitch"
enable_haproxy: "no"
enable_keepalived: "no"
```
## 安装bootstrap server
```
kolla-ansible bootstrap-servers -i ./all-in-one
```
## 预检测环境
```
kolla-ansible prechecks -i ./all-in-one
```
预检测遇到问题
```
TASK [prechecks : Checking docker SDK version] ******************************************************************************************************************************************************************************************************* [ERROR]: Task failed: Module failed: non-zero return code Origin: /opt/openstack/openstack-kolla/share/kolla-ansible/ansible/roles/prechecks/tasks/package_checks.yml:2:3 1 --- 2 - name: Checking docker SDK version ^ column 3 fatal: [localhost]: FAILED! => {"changed": false, "cmd": ["/opt/openstack/openstack-kolla/bin/python3.12", "-c", "import docker; print(docker.__version__)"], "delta": "0:00:00.018758", "end": "2025-11-23 19:52:04.252347", "failed_when_result": true, "msg": "non-zero return code", "rc": 1, "start": "2025-11-23 19:52:04.233589", "stderr": "Traceback (most recent call last):\n File \"<string>\", line 1, in <module>\nModuleNotFoundError: No module named 'docker'", "stderr_lines": ["Traceback (most recent call last):", " File \"<string>\", line 1, in <module>", "ModuleNotFoundError: No module named 'docker'"], "stdout": "", "stdout_lines": []} PLAY RECAP ******************************************************************************************************************************************************************************************************************************************* localhost : ok=15 changed=0 unreachable=0 failed=1 skipped=9 rescued=0 ignored=0 
```
这个是venv里面缺少docker库 
```
# pip install "docker>=6.0.0" "setuptools" "wheel" 
```
重新执行，遇到问题：
```
TASK [prechecks : Checking dbus-python package] ****************************************************************************************************************************************************************************************************** 

[ERROR]: Task failed: Module failed: non-zero return code 

Origin: /opt/openstack/openstack-kolla/share/kolla-ansible/ansible/roles/prechecks/tasks/package_checks.yml:12:3 

 

10   failed_when: result is failed or result.stdout is version(docker_py_version_min, '<') 

11 

12 - name: Checking dbus-python package 

     ^ column 3 

 

fatal: [localhost]: FAILED! => {"changed": false, "cmd": ["/opt/openstack/openstack-kolla/bin/python3.12", "-c", "import dbus"], "delta": "0:00:00.018970", "end": "2025-11-23 19:58:13.745727", "failed_when_result": true, "msg": "non-zero return code", "rc": 1, "start": "2025-11-23 19:58:13.726757", "stderr": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nModuleNotFoundError: No module named 'dbus'", "stderr_lines": ["Traceback (most recent call last):", "  File \"<string>\", line 1, in <module>", "ModuleNotFoundError: No module named 'dbus'"], "stdout": "", "stdout_lines": []} 

 

PLAY RECAP ******************************************************************************************************************************************************************************************************************************************* 

localhost                  : ok=16   changed=0    unreachable=0    failed=1    skipped=9    rescued=0    ignored=0    
```
venv缺少dbus 
```
# sudo apt install -y libdbus-1-dev libglib2.0-dev pkg-config build-essential python3-dev 
# pip install dbus-python 
```
重新执行，终于通过了，继续安装。
## 安装
```
# kolla-ansible deploy -i ./all-in-one
```
### 问题1
遇到容器启动失败的问题
```
RUNNING HANDLER [common : Initializing toolbox container using normal user] ************************************************************************************************************************************************************************** 

[ERROR]: Task failed: Module failed: non-zero return code 

Origin: /opt/openstack/openstack-kolla/share/kolla-ansible/ansible/roles/common/handlers/main.yml:19:3 

 

17     - Initializing toolbox container using normal user 

18 

19 - name: Initializing toolbox container using normal user 

     ^ column 3 

 

fatal: [localhost]: FAILED! => {"changed": false, "cmd": ["docker", "exec", "-t", "kolla_toolbox", "ansible", "--version"], "delta": "0:00:00.036173", "end": "2025-11-23 20:16:58.130188", "msg": "non-zero return code", "rc": 1, "start": "2025-11-23 20:16:58.094015", "stderr": "Error response from daemon: container 1104e750dffdb69e3923d8f0c1a03283c45a190ff37e6a70a3bc44d36d7e55b6 is not running", "stderr_lines": ["Error response from daemon: container 1104e750dffdb69e3923d8f0c1a03283c45a190ff37e6a70a3bc44d36d7e55b6 is not running"], "stdout": "", "stdout_lines": []} 

 

PLAY RECAP ******************************************************************************************************************************************************************************************************************************************* 

localhost                  : ok=15   changed=10   unreachable=0    failed=1    skipped=3    rescued=0    ignored=0    

 

Kolla Ansible playbook(s) /opt/openstack/openstack-kolla/share/kolla-ansible/ansible/site.yml exited 2 
```
说明容器 *kolla_toolbox* 启动失败，查看容器log
```
# docker logs kolla_toolbox | head -50 

+ sudo -E kolla_set_configs 

sudo: PAM account management error: Authentication service cannot retrieve authentication info 

sudo: a password is required 

+ sudo -E kolla_set_configs 

sudo: PAM account management error: Authentication service cannot retrieve authentication info 

sudo: a password is required 

+ sudo -E kolla_set_configs 

sudo: PAM account management error: Authentication service cannot retrieve authentication info 

sudo: a password is required 

+ sudo -E kolla_set_configs 

sudo: PAM account management error: Authentication service cannot retrieve authentication info 

sudo: a password is required 

+ sudo -E kolla_set_configs 

sudo: PAM account management error: Authentication service cannot retrieve authentication info 

sudo: a password is required 

+ sudo -E kolla_set_configs 

sudo: PAM account management error: Authentication service cannot retrieve authentication info 

sudo: a password is required 

+ sudo -E kolla_set_configs 

sudo: PAM account management error: Authentication service cannot retrieve authentication info 

sudo: a password is required 

+ sudo -E kolla_set_configs 

sudo: PAM account management error: Authentication service cannot retrieve authentication info 

sudo: a password is required 

+ sudo -E kolla_set_configs 

sudo: PAM account management error: Authentication service cannot retrieve authentication info 

sudo: a password is required 

+ sudo -E kolla_set_configs 

sudo: PAM account management error: Authentication service cannot retrieve authentication info 

sudo: a password is required 
```
这个报错是容器获取不到权限，无法继续，这是一个社区曾经报错的问题，实际上只要暴力修改sudo文件就好了。  
只做一个docker image， 把sudo文件替换掉。  
创建2个文件，sudo和Dockerfile，内容如下：
```
# Dockerfile 
FROM quay.io/openstack.kolla/kolla-toolbox:master-rocky-10

ADD sudo /etc/pam.d/sudo

# sudo 
#%PAM-1.0
auth       sufficient      pam_permit.so
account    sufficient      pam_permit.so
password   sufficient      pam_permit.so
session    required      pam_permit.so
```
执行命令
```
docker build -t kolla-ansible:pamfixed .
```
然后修改globals.yml
在第一行加入内容
```
kolla_toolbox_image_full: "kolla/ubuntu-source-kolla-toolbox:pamfixed"
```
重新部署，启动成功。  
后续安装过程中，报各个容器出现同样的错误，对于同样错误的容器，执行相同的处理方案，替换docker image的sudo文件。  
最终得到所有需要修改的容器如下：
```
kolla_toolbox_image_full: "kolla/ubuntu-source-kolla-toolbox:pamfixed"
haproxy_image_full: "kolla/ubuntu-source-kolla-haproxy:pamfixed"
openvswitch_vswitchd_image_full: "openvswitch-vswitchd:pamfixed"
nova_libvirt_image_full: "nova-libvirt:pamfixed"
nova_api_image_full: "nova-api:pamfixed"
nova_compute_image_full: "nova-compute:pamfixed"
neutron_l3_agent_image_full: "neutron-l3-agent:pamfixed"
neutron_openvswitch_agent_image_full: "neutron-openvswitch-agent:pamfixed"
neutron_metadata_agent_image_full: "neutron-metadata-agent:pamfixed"
neutron_dhcp_agent_image_full: "neutron-dhcp-agent:pamfixed"
```
### 问题2
安装过程中，启动keystone的时候，会遇到无法创建mariadb的问题。  
这个问题是第一次遇到，mariadb无法启动，因为会有端口冲突。  
无论如何修改，包括修改端口或者容器名字，都会遇到端口冲突问题，于是决定自己部署一套mariadb，修改globals.yml和password.yml，把数据外置，不再依赖于默认安装的mariadb。
启动之后，修改globals.yml
```
enable_mariadb: "no"
database_address: "192.168.0.1"
database_port: "3306"
database_user: "root"
database_password: "password"
```
修改password.yml
```
database_password: "password"
```
修改完成后重启部署，最终成功，容器启动完成。

# Tips
## 1 
如果还有一些服务启动失败，需要查看容器log。  
很多时候重复部署失败的过程中，数据库可能会记录一些半成品服务信息，尤其是uuid，很可能会因此导致部署失败。
在初始化部署尚未完成的时候，清理数据库可能是一个非常快速成熟的方案。
## 2
在部署OpenStack Kolla Ansible的时候，可能会遇到各种系统冲突和镜像冲突。  
社区对其测试并非非常严格的产品化，需要考虑到运维功底很多。
大多数解决方案可能是来自于过往对系统的了解程度。  
因为我很久没有接触OpenStack的最新源码，有很多脚本可能并不熟悉，本次实践以独立安装完成一个测试环境为主，所以很多暴力操作不能作为生产环境实践。
