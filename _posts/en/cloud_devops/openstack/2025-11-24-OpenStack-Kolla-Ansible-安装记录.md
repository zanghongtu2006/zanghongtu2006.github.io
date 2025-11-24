---
layout: post
lang: en
title: "Deploy an All-in-one OpenStack GPU Server By Kolla Ansible"
date: "2025-11-24 23:28:47"
slug: "openstack-kolla-ansible-installation"
translations:
  zh: /zh/openstack-kolla-ansible-installation/
  de: /de/openstack-kolla-ansible-installation/
categories: ["OpenStack"]
tags: ["OpenStack", "Kolla"]
---
A few days ago, I received a GPU server from a client. The client requested the installation and deployment of an all-in-one OpenStack environment for backend service integration testing.
Let's check the current server status first.
# Check Server Status
```
# ip a
```
It has 2 network cards, one card has an public IP, that allowed me login it.
```
# nvidia-smi 
```
8 5090 GPUs，this is probably the second-highest configuration server I've ever seen.  
Last one had 8 H100.
```
# uname -a
Linux serv-gpu-1 6.8.0-86-generic #87-Ubuntu SMP PREEMPT_DYNAMIC Mon Sep 22 18:03:36 UTC 2025 x86_64 x86_64 x86_64 GNU/Linux
```
*Ubuntu 24.04 LTS* ，OpenStack version is *rocky* currently.  
This version may encounter various unknown problems if installed on Ubuntu 24.04.

# 开始安装
Next, begin the installation process, following the steps outlined in the official website tutorial.

## 基础环境
```
Install Dependencies
# sudo apt install git python3-dev libffi-dev gcc libssl-dev libdbus-glib-1-dev
Install python venv
# sudo apt install python3-venv
Create a python runtime env
# python3 -m venv /opt/openstack/kolla/venv
# source /opt/openstack/kolla/venv/bin/activate
# pip install -U pip
Install kolla dependencies
# pip install git+https://opendev.org/openstack/kolla-ansible@master
Install kolla
# sudo mkdir -p /etc/kolla
# sudo chown $USER:$USER /etc/kolla
# cp -r /opt/openstack/kolla/venv/share/kolla-ansible/etc_examples/kolla/* /etc/kolla
# cp /opt/openstack/kolla/venv/share/kolla-ansible/ansible/inventory/all-in-one .
# kolla-ansible install-deps
Create passwords for OpenStack services
# kolla-genpwd
```
All previous steps were completed successfully.  
The system is relatively clean and hasn't been used by many people yet, so there are no particularly strange dependency errors.
## 编辑globals.yml
Then edit the file: /etc/kolla/globals.yml  
Follow the tutorial to edit network information, etc.

Because this is an all-in-one environment used for development and testing, 
and the network card does not support high availability (HA), 
we need to disable HA and use the local IP address instead of the VIP.
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
## Install bootstrap server
```
kolla-ansible bootstrap-servers -i ./all-in-one
```
## Pre-Check
```
kolla-ansible prechecks -i ./all-in-one
```
Problems encountered in pre-detection
```
TASK [prechecks : Checking docker SDK version] ******************************************************************************************************************************************************************************************************* [ERROR]: Task failed: Module failed: non-zero return code Origin: /opt/openstack/openstack-kolla/share/kolla-ansible/ansible/roles/prechecks/tasks/package_checks.yml:2:3 1 --- 2 - name: Checking docker SDK version ^ column 3 fatal: [localhost]: FAILED! => {"changed": false, "cmd": ["/opt/openstack/openstack-kolla/bin/python3.12", "-c", "import docker; print(docker.__version__)"], "delta": "0:00:00.018758", "end": "2025-11-23 19:52:04.252347", "failed_when_result": true, "msg": "non-zero return code", "rc": 1, "start": "2025-11-23 19:52:04.233589", "stderr": "Traceback (most recent call last):\n File \"<string>\", line 1, in <module>\nModuleNotFoundError: No module named 'docker'", "stderr_lines": ["Traceback (most recent call last):", " File \"<string>\", line 1, in <module>", "ModuleNotFoundError: No module named 'docker'"], "stdout": "", "stdout_lines": []} PLAY RECAP ******************************************************************************************************************************************************************************************************************************************* localhost : ok=15 changed=0 unreachable=0 failed=1 skipped=9 rescued=0 ignored=0 
```
This means docker-lib is not found in python-venv, we need to install it.
```
# pip install "docker>=6.0.0" "setuptools" "wheel" 
```
Re-execution encountered problems：
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
dbus is not found, we need to install dbus-python.
```
# sudo apt install -y libdbus-1-dev libglib2.0-dev pkg-config build-essential python3-dev 
# pip install dbus-python 
```
Recheck, and finally it works.   
Everything is down.
## Installation
```
# kolla-ansible deploy -i ./all-in-one
```
### Question 1
Docker startup failed.
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
This means docker *kolla_toolbox* start failed.  
We need to check logs 
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
This error indicates the container cannot obtain sufficient permissions to continue. 
This is a previously reported issue in the community, 
and it can actually be resolved by simply modifying the sudo file.

Create only one Docker image and replace the sudo file.

Create two files, sudo and Dockerfile, with the following content:
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
Execute
```
# docker build -t kolla-ansible:pamfixed .
```
After that, Edit globals.yml
Add this line into the head of the globals.yml
```
kolla_toolbox_image_full: "kolla/ubuntu-source-kolla-toolbox:pamfixed"
```
Re-execute and it works.    
During subsequent installation, the same error occurred in all containers. For containers with the same error, the same solution was implemented: replacing the sudo file in the Docker image.
The final list of all containers requiring modification is as follows:
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
### Question 2
During the installation process, when starting Keystone, an issue arose where MariaDB could not be created.

This was the first time I encountered this problem; MariaDB failed to start due to a port conflict.

No matter what I modified, including changing the port or container name, the port conflict issue persisted. Therefore, I decided to deploy my own MariaDB instance, modifying `globals.yml` and `password.yml` to externalize the data and no longer rely on the default MariaDB installation.

After starting MariaDB, I modified `globals.yml`...
```
enable_mariadb: "no"
database_address: "192.168.0.1"
database_port: "3306"
database_user: "root"
database_password: "password"
```
Modify password.yml
```
database_password: "password"
```
After making the modifications and restarting the deployment, it was finally successful, and the container started successfully.

# Tips
## 1 
If some services fail to start, you need to check the container logs.

Often, during repeated deployment failures, the database may record some incomplete service information, especially UUIDs, which could potentially cause deployment failures.

Clean up the database before the initial deployment is complete is often a quick and effective solution.
## 2
Deploying OpenStack Kolla Ansible can encounter various system and image conflicts.

Community testing of it is not very rigorous for production, 
requiring a high level of operational expertise.

Most solutions likely stem from prior knowledge of the system.

Because I haven't worked with the latest OpenStack source code in a long time, 
I may not be familiar with many scripts.
This practice focuses on independently installing a test environment, 
so many brute-force operations cannot be used for production environments.