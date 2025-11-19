---
title: "log4j使用DailyRolling"
date: "2015-07-18 09:14:00"
slug: "log4j-e4-bd-bf-e7-94-a8dailyrolling"
layout: "post"
categories: ["编程开发"]
tags: ["log4j", "DailyRollingFileAppender"]
---
使用log4j 1.2.16版本过程发现一个坑，共享此处，谨记：
[codesyntax lang="xml"]

```
<appender name="log_appender" class="org.apache.log4j.DailyRollingFileAppender">
  <param name="File" value="./log/log_test.log" />
  <param name="DatePattern" value="'.'yyyy-MM-dd-HH'.log'" />
  <layout class="org.apache.log4j.PatternLayout">
    <param name="ConversionPattern" value="%m%n" />
  </layout>
</appender>
```

[/codesyntax]
此处使用yyyy-MM-dd-HH和yyyy-MM-dd-hh差别很大。
大写HH是24小时制，小写hh是12小时制
按小时切割日志时，如果后缀为hh，则会覆盖掉之前的日志。例如logt\_test.logt.2015-07-18-13.log点会标记为logt\_test.logt.2015-07-18-01.log，覆盖掉之前的logt\_test.logt.2015-07-18-01.log。
后果就是logt\_test.logt.2015-07-18-01.log这段时间log无从查找。
