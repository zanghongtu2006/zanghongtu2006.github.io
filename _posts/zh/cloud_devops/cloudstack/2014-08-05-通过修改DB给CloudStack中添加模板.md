---
layout: post
lang: zh
translations:
  en: /en/e9-80-9a-e8-bf-87-e4-bf-ae-e6-94-b9db-e7-bb-99cloudstack-e4-b8-ad-e6-b7-bb-e5-8a-a0-e6-a8-a1-e6-9d-bf/
  de: /de/e9-80-9a-e8-bf-87-e4-bf-ae-e6-94-b9db-e7-bb-99cloudstack-e4-b8-ad-e6-b7-bb-e5-8a-a0-e6-a8-a1-e6-9d-bf/
title: "通过修改DB给CloudStack中添加模板"
date: "2014-08-05 16:48:44"
slug: "e9-80-9a-e8-bf-87-e4-bf-ae-e6-94-b9db-e7-bb-99cloudstack-e4-b8-ad-e6-b7-bb-e5-8a-a0-e6-a8-a1-e6-9d-bf"
categories: ["CloudStack"]
tags: ["CloudStack", "模板"]
---
CloudStack的模板上传有只能通过http server，但经常会遇到httpserver搭建异常、上传发生timeout或者上传一半的时候无法继续上传等等各种问题，而项目实施的时候，按进度又要求必须尽快使用该模板，这个时候就会有是否能够直接将模板scp到SecondaryStorage中的需求。

在SS中，模板存放在template目录中，此目录的结构为：template/tmpl/[account\_id]/[template\_id]/

account\_id为此模板所属用户的id

例如：登陆admin用户，上传一个centos.ova作为vmware模板，该模板id为202，则此模板在SS中存放路径为template/tmpl/2/202/。该目录中一共有4个文件：509f8d99-d81f-3104-95c9-9cfd23026f83.ova，CentOS\_5.6-disk1.vmdk，CentOS5.6.mf，CentOS 5.6.ovf，template.properties。

".ova"文件是上传的原始ova文件，".vmdk",".mf",".ovf"是由ova解压之后产生的模板文件。

".vmdk"是虚拟机的磁盘镜像文件

".ovf"是虚拟机在导出为ovf格式的时候所产生的描述文件，包含了虚拟机磁盘文件vmdk，资源文件iso和domain之间的正确对应

".mf"是相关文件的SHA的集合，主要作用是防止模板文件被修改

此例中，mf文件内容如下：

[root@localhost 202]# catCentOS\ 5.6.mf

SHA1(CentOS 5.6.ovf)=867999689b9a2f4591dc3c930d4033f7872264b0

SHA1(CentOS\_5.6-disk1.vmdk)=f8a0fdbbafafcc2dc1535c1bf53f500180a5cf75

以上3个文件是vmware模板相关文件，另外一个template.properties则是CloudStack在installtemplate完成之后，产生的模板描述文件，内容如下：

[root@localhost 202]# cattemplate.properties

#

#Mon Jul 29 06:42:11 UTC 2013

ova.virtualsize=10737418240 //模板的额定值

filename=509f8d99-d81f-3104-95c9-9cfd23026f83.ova //ova文件名

ova.filename=509f8d99-d81f-3104-95c9-9cfd23026f83.ova  //ova文件名

id=202  //db中vm\_template.id

public=true //db 中vm\_template.public，控制模板的访问权限

uniquename=202-2-fc9f565a-9e17-3de2-b81a-f91b2b69894f//db中vm\_template.uniquename

virtualsize=10737418240 //模板的额定值

checksum=847b01e45b6ad09519f4c3fabeb5b823//校验码，检查文件是否完整或被改变

hvm=true//db中vm\_template.hvm，是否需要主机支持hvm

ova=true //是否ova文件

description=test//db中vm\_template.display\_text

ova.size=1011362816 //ova模板文件大小

size=1011362816 //ova模板文件大小

==============================================================================

CloudStack中对模板的信息，会分别存放在5个表中：vm\_template，template\_host\_ref，template\_zone\_ref，template\_spool\_ref，template\_swift\_ref。

vm\_template主要存放模板的详细信息，包含名称，访问权限，下载地址，格式，类型等。

表结构如下：

+--------------------+---------------------+------+-----+---------+----------------+

| Field            | Type             | Null | Key | Default | Extra        |

+--------------------+---------------------+------+-----+---------+----------------+

| id               | bigint(20) unsigned | NO  | PRI | NULL   | auto\_increment |

| unique\_name       | varchar(255)      | NO   |    | NULL    |             |

| name             | varchar(255)      | NO   |    | NULL    |             |

| uuid             | varchar(40)       | YES  | UNI | NULL   |             |

| public           | int(1) unsigned    | NO   |    | NULL    |             |访问权限

| featured          | int(1)unsigned     | NO  |     | NULL   |             |访问权限

| type             | varchar(32)       | YES  |    | NULL    |             |

| hvm              | int(1) unsigned    | NO   |    | NULL   |              |

| bits             | int(6) unsigned    | NO   |    | NULL   |             |32/64

| url              | varchar(255)      | YES  |    | NULL    |             |模板上传地址

| format           | varchar(32)        | NO  |     | NULL   |             | OVA/VHD/QCOW2/ISO

| created          | datetime          | NO   |    | NULL    |             |

| removed          | datetime          | YES  | MUL | NULL   |             |

| account\_id        | bigint(20) unsigned | NO  |     | NULL   |             |

| checksum          |varchar(255)       | YES  |    | NULL   |              |

| display\_text      | varchar(4096)      | YES  |    | NULL   |              |

| enable\_password    |int(1) unsigned     | NO  |     | 1      |             |

| enable\_sshkey     | int(1) unsigned    | NO   |    | 0      |              |

| guest\_os\_id       | bigint(20) unsigned | NO  |     | NULL   |             |操作系统类型

| bootable          | int(1)unsigned     | NO  |     | 1      |             |

| prepopulate       | int(1) unsigned    | NO   |    | 0      |             |

| cross\_zones       | int(1) unsigned    | NO   |    | 0      |             |跨资源域

| extractable       | int(1) unsigned    | NO   |    | 0      |             |可下载

| hypervisor\_type    |varchar(32)        | YES  |    | NULL   |              |

| source\_template\_id | bigint(20) unsigned | YES |     | NULL   |             |

| template\_tag      | varchar(255)       | YES |     | NULL   |             |

| sort\_key          | int(32)           | NO  |     | 0      |             |

+--------------------+---------------------+------+-----+---------+----------------+

type有4种类型，分别为USER/SYSTEM/BUILTIN/PERHOST，即用户模板，系统虚拟机模板，内建模板，PERHOST。

CloudStack默认提供的模板，除了系统虚拟机模板之外，还对每种类型的hyperviser提供一个CentOS5.3(64-bit) no GUI(XenServer)的内建模板（BUILTIN），以供测试或小型应用。

PERHOST为hyperviser中自带的vmtools.iso。

**SYSTEM，BUILTIN和PERHOST属于system用户，所以account\_id=1，这3类模板的信息，在db的vm\_template中，是在初始化db的时候就写入其中的，所以，SS中template/tmpl/1中的目录和文件可以在部署CloudStack之前提前放入其中，如果使用其他CloudStack环境中使用过的SS的来部署CloudStack的时候，SS中的template/tmpl/1目录中的所有模板，都可以保持不变，这样能够省去不少传输模板的时间**

USER为用户上传模板，上传用户为其所属用户，account\_id为用户的id。

cross\_zones为模板的跨资源域属性，上传模板的时候，如果选AllZone，则此项为1，此时模板标记为跨资源域，在多个Zone的情况下，如果删除某一Zone里的该模板，则其他资源域中相应模板也会一并删除。

例：

mysql> select \*from vm\_template where id=202 \G;

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* 1.row \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

id: 202 //template.properties中的id

unique\_name:202-2-fc9f565a-9e17-3de2-b81a-f91b2b69894f//template.properties中的unique\_name

name:test

uuid:9838688c-4845-4d2f-827a-8035aee76f8b

public: 1

featured: 1

type:USER

hvm: 1

bits:64

url:http://192.168.204.199/CentOS5.6.ova

format: OVA

created: 2013-07-2906:23:43

removed: NULL

account\_id: 2

checksum:847b01e45b6ad09519f4c3fabeb5b823

display\_text:test

enable\_password: 0

enable\_sshkey: 0

guest\_os\_id: 103

bootable: 1

prepopulate: 0

cross\_zones: 0

extractable: 1

hypervisor\_type: VMware

source\_template\_id:NULL

template\_tag:NULL

sort\_key: 0

template\_zone\_ref主要用于存放模板对应的zone的信息，表结构如下：

mysql> desc template\_zone\_ref;

+--------------+---------------------+------+-----+---------+----------------+

| Field       | Type             | Null | Key | Default | Extra        |

+--------------+---------------------+------+-----+---------+----------------+

| id          | bigint(20) unsigned | NO  | PRI | NULL   | auto\_increment |

| zone\_id     | bigint(20) unsigned | NO   |MUL | NULL    |             |

| template\_id  | bigint(20) unsigned | NO  | MUL | NULL   |              |

| created     | datetime          | NO   |    | NULL    |             |

| last\_updated | datetime          | YES  |    | NULL   |              |

| removed     | datetime          | YES  | MUL | NULL   |             |

+--------------+---------------------+------+-----+---------+----------------+

若该模板注册到某资源域（Zone），则会在此表中写入一项

例：

mysql> select \*from template\_zone\_ref where template\_id=202 \G;

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* 1.row \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

id: 13

zone\_id: 1

template\_id:202

created: 2013-07-2906:23:43

last\_updated: 2013-07-2906:23:43

removed: NULL

template\_host\_ref主要存放模板和二级存储的对应关系，上传进度，上传地址等信息，表结构如下：

mysql> desc template\_host\_ref;

+----------------+---------------------+------+-----+---------+----------------+

| Field         | Type             | Null | Key | Default | Extra        |

+----------------+---------------------+------+-----+---------+----------------+

| id            |bigint(20) unsigned | NO   | PRI | NULL   | auto\_increment |

| host\_id       | bigint(20) unsigned | NO  | MUL | NULL   |              |

| template\_id    |bigint(20) unsigned | NO   | MUL | NULL   |             |

| created       | datetime          | NO   |    | NULL   |              |

| last\_updated   | datetime          | YES |     | NULL   |             |

| job\_id        | varchar(255)      | YES  |    | NULL    |             |上传模板任务id

| download\_pct   | int(10) unsigned   | YES  |    | NULL   |              |上传进度

| size          |bigint(20) unsigned | YES  |    | NULL    |             |模板额定大小

| physical\_size  | bigint(20) unsigned | YES |     | 0      |             |模板物理大小

| download\_state | varchar(255)       | YES |     | NULL   |             |

| error\_str     | varchar(255)       | YES |     | NULL   |             |

| local\_path     |varchar(255)       | YES  |    | NULL   |             |SSVM中的下载地址

| install\_path   | varchar(255)      | YES  |    | NULL    |             |SS中的存放路径

| url           |varchar(255)       | YES  |    | NULL   |              |上传地址

| destroyed     | tinyint(1)        | YES  |    | NULL    |             |

| is\_copy       | tinyint(1)        | NO   |    | 0      |             |

+----------------+---------------------+------+-----+---------+----------------+

模板注册到CloudStack之后，由management-server调度任务，发送到SSVM执行，将模板从给定的url下载到二级存储中。local\_path为SSVM中下载模板的实际路径，下载完成后，此项则不在起任何作用，同时会获取模板在SS中的实际路径并写入表的install\_path中。例：

mysql> select \*from template\_host\_ref where template\_id=202 \G;

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* 1.row \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

id: 12

host\_id:3

template\_id: 202

created:2013-07-29 06:23:43

last\_updated: 2013-07-29 14:39:50

job\_id:8aab877e-b6a2-4952-920e-d631102da361

download\_pct: 100

size: 10737418240

physical\_size:1011362816

download\_state:DOWNLOADED

error\_str: Install completedsuccessfully at 7/29/13 6:42 AM

local\_path:/mnt/SecStorage/d8c72098-9608-3917-90a4-ac88d47a30f4/template/tmpl/2/202/dnld912053474216253760tmp\_

install\_path:template/tmpl/2/202//509f8d99-d81f-3104-95c9-9cfd23026f83.ova

url:http://192.168.204.199/CentOS5.6.ova

destroyed: 0

is\_copy:0

template\_spool\_ref存放的是模板由二级存储传入主存储之后的对应信息，template\_swift\_ref是在启用swift之后，模板和swift的对应信息。

由此可以看出，实际模板相关的信息，分别存放在db的vm\_template，template\_host\_re，template\_zone\_ref和SS中的template.properties中。

**所以，如果上传模板失败而暂时无法解决或由于网络速度受限而需要长时间传输模板的情况下，实际可以通过手动复制模板文件到相关目录，按模板编辑template.properties文件，然后插入db的方式，来解决此问题。可以省去不少传输模板的时间。**
