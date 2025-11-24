---
layout: post
lang: zh
translations:
  en: /en/cloudstack-e4-ba-8c-e7-ba-a7-e5-ad-98-e5-82-a8-e7-bb-93-e6-9e-84/
  de: /de/cloudstack-e4-ba-8c-e7-ba-a7-e5-ad-98-e5-82-a8-e7-bb-93-e6-9e-84/
title: "CloudStack二级存储结构"
date: "2014-08-05 16:47:45"
slug: "cloudstack-e4-ba-8c-e7-ba-a7-e5-ad-98-e5-82-a8-e7-bb-93-e6-9e-84"
categories: ["CloudStack"]
tags: ["CloudStack", "二级存储", "secondary storage"]
---
CloudStack的存储分为两种，PrimaryStorage（PS）和SecondaryStorage（SS），即主存储和二级存储。

PS主要用来存放VM的磁盘镜像，SS则用来存放模板（template），快照（snapshot），卷（volume)，对于vmware，二级存储也会存放systemvm.iso。

CloudStack目前只接受NFS作为Secondary Storage。

SS是资源域（Zone）级别的存储，即一个SS可以供其所在Zone中所有的主机（host）使用。

SS在添加到资源域之前，需要手动或调用脚本将所需要的系统虚拟机模板（SystemvmTemplate)部署到指定位置。CloudStack提供了脚本实现这一功能，以下是社区文档中的脚本：

1. #/usr/share/cloudstack-common/scripts/storage/secondary/cloud-install-systmplt-m /mnt/secondary -uhttp://download.cloud.com/templates/acton/actonsystemvm-02062012.vhd.bz2-h xenserver -s<optional-management-server-secret-key>-F

但是由于在国内下载太卡，可以先把url复制到浏览器中，把相应文件下载到本地，使用如下命令安装：

1. /usr/lib64/cloud/agent/scripts/storage/secondary/cloud-install-sys-tmplt-m /mnt/secondary -f actonsystemvm-02062012.vhd.bz2 -h xenserver-F

**脚本执行成功后，会在SS中创建template目录**

以vmware为例，其结构如下：

/template/tmpl/1/8/

此目录中一共有5个文件：routing-8.ova，systemvm-disk1.vmdk，systemvm.mf，systemvm.ovf，template.properties，这就是vmware的系统虚拟机模板所需要的所有文件。

其中template.properties是模板的描述文件，CloudStack中所有的模板都会有唯一一个描述文件，与db中所存储的信息相对应

template目录结构为template/tmpl/[account\_id]/[template\_id]/

CloudStack有2个默认用户，system和admin，系统虚拟机模板和内建模板默认属于system，所以其account\_id=1，同样，使用admin用户上传的模板account\_id=2

**SS在添加到资源域之后，会再创建2个目录，snapshots，volumes**

snapshots存放的是卷快照，对卷做快照，都会存放到该目录下。snapshot目录结构为snapshots/[account\_id]/[volume\_id]/

volumes存放的是需要提供下载的卷，在CloudStack中，关闭的vm的卷可以提供下载功能，点击下载后，会将卷复制到SS中，由SSVM（二级存储虚拟机）提供下载服务。volume目录结构为volumes/[account\_id]

对于存在vmware类型hyperviser的zone，在SSVM创建在vmware主机上，并且已经创建完成之后，SS中还会创建一个名为systemvm的目录，CloudStack会将management-server中的systemvm.iso复制到该路径下，以提供给vmware的SSVM,CPVM,v-Router进行挂载。Xenserver则是将systemvm.iso部署到hyperviser中，提供挂载点。

Tips:

如果使用曾经使用过的二级存储部署CloudStack，需要删除除template目录中，系统虚拟机模板和内建模板之外的所有目录，systemvm目录如果存在则必须删除，否则可能会对新部署的环境中的系统虚拟机和v-Router产生不良影响，例如v-Router无法启动等问题。
