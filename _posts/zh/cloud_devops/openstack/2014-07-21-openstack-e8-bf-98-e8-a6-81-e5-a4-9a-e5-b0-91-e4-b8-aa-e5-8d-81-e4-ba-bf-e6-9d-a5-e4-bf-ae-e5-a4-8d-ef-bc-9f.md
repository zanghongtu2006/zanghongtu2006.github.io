![openstack-logo512](/assets/images/2012/01/openstack-logo512.png)

**作为私有云标志性的开源平台, OpenStack似乎成了一个巨大的焦油坑, 数以十亿计的资金投入和不计其数的机构和企业深陷其中,不能自拔, OpenStack正朝着BrokenStack的深渊滑去.**

[HP已经宣布要投资十亿美元进去[1]](http://cloud.chinabyte.com/news/308/12960808.shtml)。[法国政府投了25亿进去[2]](http://news.cntv.cn/20110829/106828.shtml)。[华山资本投给了Mirantis, 一个尝试简化OpenStack使用的初创公司[3]](http://tech.qq.com/a/20130114/000071.htm)。 [IBM [4]](http://tech.163.com/13/0917/13/98VS3JPG000915BD.html), [思科[5]](http://tech.163.com/13/0917/13/98VS3JPG000915BD.html)和[甲骨文 [6]](http://net.it168.com/a2014/0325/1606/000001606371.shtml)也跟着丢了20亿美金进去以及他们的名字。

在许多年后，最著名的开源云平台Openstack看起来[始终很难在压力下提供可靠的商业服务[7]](http://www.numerama.com/magazine/28423-cloudwatt-bercy-demande-un-audit-sur-un-possible-fiasco.html)并一直处于未完成状态: 没有完整的编配，没有完整的帐务，也没有自动化灾难恢复。它的设计模仿了已经有15年历史的虚拟化产品，而这个时候，其他正规的云公司（百度，谷歌，Salesforce.com)主要都在关心大规模的电脑裸机配置自动化。

超过40亿美金的投资都没有能力生产出一个像样的 —— 能够与已经在市场上存在的大量的却不知名的开源云平台相当的产品， 而那些不知名的产品已经支持许多重要应用很多年了。

[Qemu [8]](http://wiki.qemu.org/Main_Page) —— 是IaaS 教父 —— 由 Fabrice Bellard在2003年用一年的时间在法国创建。

[NiftyName [9]](http://www.niftyname.org/) —— 一个已经被用于巴黎城市网站的开源云平台 —— 由3个人用1年的时间开发出来。 在2008年，它可以支持： 虚拟计算， 虚拟存储，虚拟网络，含有多重数据中心部署的虚拟数据中心。

[Eucalyptus [10]](http://en.wikipedia.org/wiki/Eucalyptus_%28software%29) —— 2008年产生于加利福尼亚 —— 提供了一个与亚马逊Web服务兼容的开源解决方案。

[OpenNebula [11]](http://en.wikipedia.org/wiki/OpenNebula) —— 来自于西班牙 —— 从2010年开始投入使用。

[Cloudstack [12]](http://en.wikipedia.org/wiki/Apache_CloudStack) —— 由Apache软件基金会支持 —— 从2010年起就是商务云供应商的基金会。

[Proxmox [13]](http://pve.proxmox.com/wiki/Roadmap) —— 一个来自德国的虚拟机以及虚拟私有服务器管理员 —— 自2008年起被许多只需要虚拟化的公司使用，而且它的设置非常的简单。

[SlapOS [14]](http://community.slapos.org/) —— 一个基于轻量级容器的分布式网状云编配器 —— [开始于2010年，托管了大型公司制造的数据 [15]](http://community.slapos.org/news-slapos-success) 并且顺利地结合了IaaS, PaaS, SaaS, 计算机编配，帐务及自动地灾难恢复。两百万欧元的投资足够使其达到一个成熟的状态，这都归功于它简单并稳健的设计。

[Docker [16]](http://en.wikipedia.org/wiki/Docker_%28software%29) —— 另一个与SlapOS共享了许多理论的轻量级容器配置器, [从2008年起更名为Dotcloud [17]](http://www.crunchbase.com/organization/dotcloud) —— 没有要求超过2千万美元的投资。 Docker还托管了生产应用。

整体来说，一个优秀的开发人员组是可以在一年内用几百万的投资创建一个可靠的云计算系统出来的， 并将其投入到重要应用任务的使用中。 在5年内， “BrokenStack”项目用超过2000倍的预算和大量来自多国纳税人的资金支持实现了更少的成就（除了市场营销）。

对于这个现状的原因有任何想法吗？ 如果你有任何的想法请给我留言。

我认为现在是时候改变评估开源软件的方式了：通过”亲自”学习真实案例来了解它”内部”是如何工作的来代替比较市场数据， 结构报告或者网页的美观程度。也是时候削弱官僚主义机构在开源产品上的力量并牢记[25年前OSF/1（开源软件基金会）的失败 [18]](http://en.wikipedia.org/wiki/Open_Software_Foundation)。没有这样的改变， 技术灾害和资源的浪费就会再次发生并损害低成本高质量的开源产品的好名声。

### 参考

[1] 云之上：HP Helion实践OpenStack从未停歇 – <http://cloud.chinabyte.com/news/308/12960808.shtml>
[2] 法式”云”将问世 – <http://news.cntv.cn/20110829/106828.shtml>
[3] Mirantis获戴尔风投等三家投资方1000万美元注资 – <http://tech.qq.com/a/20130114/000071.htm>
[4] IBM将投资10亿美元发展Linux等开源技术 – <http://tech.163.com/13/0917/13/98VS3JPG000915BD.html>
[5] 思科投资愈10亿美金建全球性Intercloud – <http://net.it168.com/a2014/0325/1606/000001606371.shtml>
[6] VMware/Oracle向公有云拓展生态系统 – <http://www.csdn.net/article/2013-03-14/2814499-VMware_Oracle_expand_public_cloud>
[7] Cloudwatt : Bercy demande un audit sur un possible fiasco –<http://www.numerama.com/magazine/28423-cloudwatt-bercy-demande-un-audit-sur-un-possible-fiasco.html>
[8] Qemu – <http://wiki.qemu.org/Main_Page>
[9] NiftyName- <http://www.niftyname.org/>
[10] Eucalyptus – <http://en.wikipedia.org/wiki/Eucalyptus_%28software%29>
[11] OpenNebula – <http://en.wikipedia.org/wiki/OpenNebula>
[12] CloudStack – <http://en.wikipedia.org/wiki/Apache_CloudStack>
[13] Proxmox Roadmap – <http://pve.proxmox.com/wiki/Roadmap>
[14] SlapOS – [http://community.slapos.org](http://community.slapos.org/)
[15] SlapOS implemented at SANEF Tolling UK – <http://community.slapos.org/news-slapos-success>
[16] Docker – <http://en.wikipedia.org/wiki/Docker_%28software%29>
[17] Dotcloud – <http://www.crunchbase.com/organization/dotcloud>
[18] OSF – <http://en.wikipedia.org/wiki/Open_Software_Foundation>

原文转自：http://www.ctocio.com/ccnews/16052.html
