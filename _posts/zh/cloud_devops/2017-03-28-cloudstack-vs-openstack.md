---
title: "cloudstack-vs-openstack"
date: "2017-03-28 23:41:05"
slug: "post-747"
layout: "post"
categories: ["未分类"]
tags: []
draft: true
---
原文链接：<https://yourserveradmin.com/blog-articles/blog/cloudstack-vs-openstack/>

近年来，本公司一直基于CloudStack和OpenStack进行二次开发，为公司和用户搭建私有云平台。现在我们来分享一下我们对于这两个平台在小规模私有云的对比观点。

什么是私有云？  
  
私有云是一个管理平台，用于简化用户对云基础设施的管理操作，云基础设施包含诸如虚拟机，网络和存储等，这些基础设施为各种终端用户提供服务（不仅仅是有经验的管理员）。  
  
搭建私有云的目的有两个，1、降低当前环境的主机成本，2、安装一个新的云环境（高可用，可扩展，预算可控）。私有云解决方案在以下情况下比较适合：1、环境中长期运行的虚拟机达到一定规模，2、预算不足以购买当前主流的云提供商的产品（例如Amazon，Google，Rackpace等）。  

接下来我们会尝试比较CloudStack和OpenStack的几个方面，从专业和个人观点两方面分别阐述一下哪个平台更为优秀。

希望本文能够帮助您进行正确的私有云选型。

功能需求

谈到私有云，一般会包含以下功能。如果您需要的话，例如：对象存储，集成在云平台中的编排服务 - 当然，OpenStack作为云平台看上去更加合适，因为OpenStack是上述所有服务的集合。但是在您决定使用OpenStack之前，您需要熟悉这两个平台在功能及其实现的几个关键要素。可能您并不需要集成这么多功能，如果云平台核心功能不能满足您的下列需求：

资源高可用性；

可用资源总量（用户和硬件）；

迅速部署稳定工作环境；

implementation and further support efforts & cost.  
  
核心功能  
  

云平台应该提供以下基本功能：

虚拟机（下文简称VM）管理和虚拟机高可用（下文简称HA）；

网络管理（网络即服务 network-as-a-service)和网络高可用；

镜像、磁盘和快照管理；

账户和权限；

  
If we speak about CloudStack this platform provides all mentioned features as part of the monolithic management service and they are available all the time during the management service operation.  
  
OpenStack splits this functionality between such core components as Nova, Neutron, Glance, Cinder and Keystone. Each component also divided into a few or more services which communicate with each other using message broker, configured using multiple .INI files and depend on SQL database. Thus, if one of the services fails the rest services may work incorrectly or may stop working at all.  
  
On the project navigator page you can also check the full list of OpenStack components and their status like adoption and maturity, compare them with projects age and decide if they are really ready for production assuming that you want to use the cloud solution instead of developing it yourself to make it working.  
  
Backups creation  
  
Independently from the chosen platform, it’s obvious that backup is one of the most important things. And most important is the ability to do the backups regularly based on preferable schedule.  
  
Both platforms have the functionality to backup machines using volume snapshots.  
  
In CloudStack you can manage backup policies and automate snapshots creation by schedule using built-in product feature.  
  
In OpenStack you will need to handle snapshots creation with additional scripts, create them manually or extend the deployment with some 3-rd party plugins or services. So, if you’re not a developer or an experienced system administrator most likely it will be a problem for you to do it by yourself and you will need to invest some additional costs into implementation of this feature in OpenStack.  
  
High Availability  
  
One of the mandatory requirements for a private cloud is that deployment must be highly available and fault-tolerant. First, it’s important to differentiate high availability of a cloud platform itself and high availability for virtual machines (and thus – services inside these virtual machines) and networks.  
  
Is both high availability features included by default into each of the cloud platform we’re talking about? Unfortunately, it is not so.  
  
High availability and fault tolerance of a cloud platform itself is a configurable feature. This must be handled by the experienced deployment engineers who develop the cloud architecture based on technical requirements and available resources.  
  
High availability and fault tolerance for end-users’ virtual machines and services deployed inside this cloud platform – is a platform specific feature, which can be either already included into the platform or not.  
  
HA for Virtual Machines  
  
Starting a new virtual machine its owner hopes that the system will be available full time of its life circle (except for some downtimes for planned maintenance, of course), but in the real world it’s not always possible due to many reasons.  
  
We know that in CloudStack the user can specify a virtual machine as HA-enabled. By default, all system VMs (virtual routers, VNC console and storage) are automatically configured as HA-enabled. When an HA-enabled machine fails, CloudStack detects this and restarts the virtual machine automatically within the same Availability Zone.  
  
When we have just started working with OpenStack our main concern was availability of HA for VMs feature on this platform. What was a surprise when we found out that OpenStack doesn’t really have this feature built-in and it can be handled on hypervisor level only. Actual status of this feature in OpenStack can be checked here. One more illustrative example of this feature status is OpenStack user story. As you can see, it was proposed but has not been implemented for the past years.  
  
So, if you want to make your virtual machines highly available in OpenStack, be sure that they will be able to automatically migrate to another host in case of failure or, for example, recover with a minimal downtime after unexpected hardware failure (like power outages, hardware issues, etc.), software failure inside a virtual machine which caused system shutdown (kernel bug, OOM, etc.) or infrastructure failure (like shared storage failure) you must additionally use a hypervisor which will handle VMs high availability and hardware hosts failures.  
  
Not a secret, that KVM is the most tested and used OpenStack hypervisor (new and already existing features tested exactly using KVM first). But, if you run OpenStack deployment using KVM (which does not provide HA for VMs from scratch) as hypervisor, you also will not be able to provide HA for VMs.  
  
Sure, this does not mean that HA for VMs cannot be implemented with OpenStack and KVM. The most common way to do it is to use Heat in combination with Ceilometer and manage VMs inside Heat stacks. For example, Platform9 use exactly this way to provide this must-have feature and have a nice thirteen minute demonstration video which shows how to create highly available VMs using their OpenStack implementation.  
  
More than likely that many engineers who worked with both platforms would opt for simpler option with enabling / disabling a checkbox for virtual machines HA in CloudStack, rather than using so many things like OpenStack Heat, Ceilometer and virtualization to create a highly available virtual machine in OpenStack.  
  
L3 High Availability  
  
High availability of networking is a critical question for each deployment and both platforms provide their specific implementation of L3 HA.  
  
CloudStack provides the solution based on the above-mentioned native support of Virtual Machines HA: virtual routers presented as specific virtual machines and their availability is handled as entire VMs HA.  
  
OpenStack is designed as a modular and distributed platform, so to handle high availability of the networking services it will be required to distribute virtual routers at least between two hardware machines.  
  
Controller HA  
  
Both, CloudStack and OpenStack, have a controller for management of the system, but the implementation of this controller is a bit different.  
  
CloudStack controller is a single management server process which use database to store configuration and can run inside hardware or virtual machine. Management server connects to compute hosts directly via hypervisor or via agents depending on the hypervisor type. Both management services can be clustered using common practices like MySQL replication (to handle load on database) and TCP load balancing (to handle API and WEB requests).  
  
In OpenStack, controller is a machine which has the same hardware resources as a compute node and runs multiple services like databases, message broker, WEB-server and set of OpenStack components. Most of these services can be clustered to provide HA for the management service itself and make it fault tolerant. However, this will require adding more server instances to the system, that will lead to complication of system support in the future and will require additional efforts and peoples’ resources for managing the deployment.  
  
It’s obvious that each service could be a potential point of failure, and the more the number of services, the higher probability of failure. In CloudStack number of potential points of failure is lower comparing to OpenStack.  
  
Support of the system  
  
It’s evident that works on the private cloud do not end up with the setup and configuration. Developed environment, hypervisors, operating systems and hardware require regular maintenance and upgrades.  
  
Depending on the platform, number and variety of customizations and dependencies maintenance task can be fast and easy or become a nightmare.  
  
Both, CloudStack and OpenStack, are open source products. It means that any registered community member can contribute into these platforms. However, communities of CloudStack and OpenStack are a bit different.  
  
CloudStack community is managed by Apache Software Foundation. It has the core team responsible for the new features implementation as well as for bug fixes. That means all information and data are available at one place and it is well structured.  
  
OpenStack community is a huge network (primary between core contributors) that is completely decentralized. As a result, bug fixes and new features may be included into different distributions and with different frequency. So, before starting to work with OpenStack you should decide which distribution to use: RedHat, Ubuntu, Mirantis or any other software provided as self-hosted solution or as a service. One more aspect of OpenStack decentralization is that a lot of technical information can be found in the internal documentation of its core contributors only, which is not always open and regularly updated. Lack of actual and well-documented information sufficiently complicates the configuration process and further maintenance and usage of this platform, that obviously increases the costs of works.  
  
2.1Summary  
  
Both platforms have their own issues to be addressed, pros and cons. We continue to believe that CloudStack is more stable, easier, and cost & time effective solution for relatively small private clouds, which typically do not have large number of hardware servers and huge amount of resources to host multiple clusters, as well as don’t require many technicians to monitor and maintain the deployment health.
