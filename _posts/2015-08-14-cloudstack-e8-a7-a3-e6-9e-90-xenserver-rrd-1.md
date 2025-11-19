---
title: "CloudStack 解析 XenServer RRD (1)"
date: "2015-08-14 10:18:13"
slug: "cloudstack-e8-a7-a3-e6-9e-90-xenserver-rrd-1"
layout: "post"
categories: ["CloudStack"]
tags: ["CloudStack", "xenserver", "监控", "RRD"]
---
XenServer有一个RRD的database，用于存储XenServer实时状态信息，并进行归集。
RRD（Round Robin Database）使用固定的存储空间来存储数据，总有一个指针指向最新数据，历史数据则按规则进行合并。
用在监控场景中，则保持最近N份记录为精确值，之前的记录按照间隔时间进行归并保存，并损失精度。
例：系统监控以15s间隔向RRD中写入数据，在当前15分钟内数据为准确值，15分钟~1小时内，归并后时间间隔为1分钟，则无法查询历史精确值，只能得到一段时间内的平均值。1~24小时内时间间隔为10分钟，则看到的数据为二次归并后的10分钟维度的平均值。1~30天时间间隔为天，则看到的数据为第三次归并后，时间维度为天的平均值。
因为对于监控系统来说，N时间长度之前的数据，人们并不是很关心，往往只是对当前运行状态精度要求更高，所以RRD的思想比较适合用在此处。
CloudStack中，对XenServer的Host和VM运行时状态，都是通过解析RRD来进行的。下面，就简单分析以下RRD的
在浏览器中输入http://[XenServerIP]/rrd\_updates?start=1439509848 该URL也可接受其它参数，详见下文介绍。此处URL输入后，会提示登陆，输入XenServer的用户名和密码登陆后，获取一个XML文本，则是RRD的返回值信息
[codesyntax lang="xml"]

```
<xport>
 <meta>    #头信息
   <start>1439509860</start>   #记录开始时间：指定的start之后第一个记录时间
   <step>60</step>             #时间间隔
   <end>1439511660</end>       #当前最后一个记录时间
   <rows>31</rows>             #一共列出行数
   <columns>4</columns>        #每行的列数
   <legend>                    #每列的数据名
     <entry>                   #每个entry是一列（row）
       AVERAGE:vm:52bf87dd-10ff-4d99-9042-66698cc5d6c6:cpu1
                               #entry的格式 AVERAGE：表示值是平均数
                                                 vm：类型是vm，还可能是host等
                                               UUID：VM的UUID
                                                 cpu1：表示第一个cpu
     </entry>
     <entry>
       AVERAGE:vm:52bf87dd-10ff-4d99-9042-66698cc5d6c6:cpu0
     </entry>
     <entry>
       AVERAGE:vm:52bf87dd-10ff-4d99-9042-66698cc5d6c6:memory
     </entry>
     <entry>
       AVERAGE:vm:52bf87dd-10ff-4d99-9042-66698cc5d6c6:memory_target
     </entry>
   </legend>
 </meta>
 <data>           #数据，每个row对应一列，第一个元素t是时间，剩余依次对应legend中的entry
   <row>          #列
     <t>1439511660</t>
     <v>0.0194</v>         #对应entry中的cpu1
     <v>0.0239</v>         #对应entry中的cpu0
     <v>788529152.0000</v> #对应memory
     <v>788529152.0000</v> #对应memory_target
   </row>
   <row>
     <t>1439511600</t>
     <v>0.0198</v>
     <v>0.0212</v>
     <v>788529152.0000</v>
     <v>788529152.0000</v>
   </row>
   <row>
     <t>1439511540</t>
     <v>0.0200</v>
     <v>0.0245</v>
     <v>788529152.0000</v>
     <v>788529152.0000</v>
   </row>
 ......
 </data>
</xport>
```

[/codesyntax]
补充解释：

```
AVERAGE:vm:52bf87dd-10ff-4d99-9042-66698cc5d6c6:cpu1
对于entry中的这一列，vm:[UUID]，在Xenserver中，Host也被当做一个vm来处理，所以，此处vm：UUID对应的也可能是host信息，按UUID查询可以指定是Host还是VM。

本套环境是新装环境，所以获取信息比较少，真实运行一段时间的环境，会得到相当复杂的信息，但其对应格式是一样的。

解析步骤：
1、获取<meta><legend>信息，顺序解析得到变量列表variableList。
2、获取遍历<data>，获取<row>：其中<t>为记录时间，<v>顺次对应 variableList 的value。

```
