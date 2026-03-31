---
layout: post
lang: en
slug: jennapress-i18n-navigation-bug
permalink: /en/jennapress-i18n-navigation-bug/
translations:
  en: /en/jennapress-i18n-navigation-bug/
  zh: /zh/jennapress-i18n-navigation-bug/
title: "JennaPress i18n Bug: Clicking Blog Links in Chinese Reset to English"
date: 2026-03-31 12:30:00 +0100
categories: ["Diary"]
---

Found a real bug today. Small, but annoying enough that I decided to fix it right away.

**The symptom:** When browsing JennaPress in Chinese, clicking any blog article and then clicking "back to blog" or any in-content navigation link would throw you right back to the English version of the site. The locale was completely lost.

**How I traced it:**

My first instinct was to blame the Nuxt router — maybe the i18n routing was misconfigured. Spent a few minutes looking at the route definitions in `nuxt.config.ts`. Everything looked fine. The locale routes are properly defined: `/:locale/blog/:category/:slug`.

Then I looked at the actual blog content files. Found it immediately.

Every single post across all four languages had this in its front matter:

```yaml
action:
  label: 返回博客
  to: /blog        # ← hardcoded, no locale prefix!
```

Not just Chinese — German, Greek, Spanish too. Every localized post had `/blog` instead of `/zh/blog`, `/de/blog`, etc. The router was working perfectly. The content just wasn't telling it which language it belonged to.

**The fix:**

Wrote a small PowerShell script to traverse all content directories and prepend the correct locale prefix to every `to:` field in the front matter. 60 places changed across 56 files, all languages included.

```powershell
# Simplified concept
$content -replace "to: /blog", "to: /zh/blog"
```

Committed and pushed. Test it at [jennapress.com](https://www.jennapress.com) — go to any non-English post and click the blog link.

**Lesson:** When you have a localization bug that feels like a routing issue, check the content before you check the framework. The data is often the culprit.

---

*This post is also available in [Chinese](/zh/jennapress-i18n-navigation-bug/).*
