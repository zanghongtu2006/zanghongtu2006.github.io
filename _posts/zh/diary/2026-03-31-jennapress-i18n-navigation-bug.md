---
layout: post
lang: zh
slug: jennapress-i18n-navigation-bug
permalink: /zh/jennapress-i18n-navigation-bug/
translations:
  en: /en/jennapress-i18n-navigation-bug/
  zh: /zh/jennapress-i18n-navigation-bug/
title: "JennaPress i18n Bug修复：中文环境下点击博客链接跳回英文版"
date: 2026-03-31 12:30:00 +0100
categories: ["Diary"]
---

今天修了一个真实的 Bug。说小不小，说大不大，但足够烦人，于是顺手修了。

**现象：** 在 JennaPress 中文界面下，随便点进一篇博客文章，再点文章里的"返回博客"之类导航链接，直接跳回英文版了。Locale 完全丢失。

**排查过程：**

第一反应是框架路由有问题。花了点时间看 `nuxt.config.ts` 里的 i18n 路由配置，看着都没问题 — `/:locale/blog/:category/:slug` 写得清清楚楚。

然后去看博客内容本身。一下就找到了。

所有四种语言的文章，front matter 里的导航链接全部写死了：

```yaml
action:
  label: 返回博客
  to: /blog        # ← 硬编码，没有语言前缀！
```

不止中文，德语、希腊语、西班牙语全部中招。每篇本地化文章里的 `to: /blog` 都应该是 `/zh/blog`、`/de/blog` 之类的。框架没问题，是内容自己在说谎。

**修复：**

写了个 PowerShell 脚本，遍历所有语言的所有内容目录，把 front matter 里的 `to:` 字段统一加上对应语言前缀。改了 60 处，56 个文件，四种语言全包。

```powershell
# 简化概念
$content -replace "to: /blog", "to: /zh/blog"
```

提交，Push。去 [jennapress.com](https://www.jennapress.com) 试一下 — 随便进一篇非英文文章，再点博客导航，应该不会再跳走了。

**经验：** 遇到本地化 bug，感觉像路由问题，先查内容再查框架。数据往往是罪魁祸首。

---

*本文亦有 [英文版本](/en/jennapress-i18n-navigation-bug/)。*
