---
title: "Count Prime"
date: "2016-10-29 18:50:11"
slug: "count-prime"
layout: "post"
categories: ["算法和数据结构"]
tags: ["leetcode"]
---
算法1：

TLE：

[codesyntax lang="java5"]

```
public class Solution {
    public int countPrimes(int n) {
        if (n <= 2) {
            return 0;
        } 
        List<Integer> list = new ArrayList<Integer>();
        list.add(2);
        for (int j = list.get(list.size() - 1); j < n; j++) {
            int i = 0;
            for (; i < list.size(); i++) {
                if (j % list.get(i) == 0) {
                    break;
                }
            }
            if (i == list.size()) {
                list.add(j);
            }
        }
        return list.size();
    }
}
```

[/codesyntax]
