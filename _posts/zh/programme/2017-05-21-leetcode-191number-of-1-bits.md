---
title: "Leetcode 191:Number of 1 Bits"
date: "2017-05-21 23:18:07"
slug: "leetcode-191number-of-1-bits"
layout: "post"
categories: ["算法和数据结构"]
tags: ["leetcode"]
---
Hamming Weight：统计数字二进制中1的个数。

普通算法思路为：

按位右移，与1做按位与运算，看结果是否为1，最终统计出个数。

```
    private static int hammingWeight(long n) {
        int num = 0;
        while ( n > 0) {
            if ((n & 1) == 1) {
                num ++;
            }
            n = n >> 1;
        }
        return num;
    }
```

但是提交之后给出了一个巨大数值 2147483648，已经超出java中int的最大值，java中没有unsigned类型，此数值则无法通过正常运算得到结果。

而且算法中逻辑会因数值增加而导致循环次数变多。

此处有另一种算法：

n = 0x110100 ；n-1 = 0x110011； n&(n - 1) = 0x110000   
n = 0x110000； n-1 = 0x101111； n&(n - 1) = 0x100000   
n = 0x100000； n-1 = 0x011111； n&(n - 1) = 0x0 

依照此思路，每次 n & (n -1）则结果中的 1 的个数少一位，看一共有多少次循环则有多少个1

```
    public int hammingWeight(int n) {
        int num = 0;
        while ( n != 0) {
            n = n & (n - 1);
            num ++;
        }
        return num;
    }
```

Java JDK中有个没看懂的算法，如下

```
    private static int hammingWeight4(int n) {
        n = n - ((n >>> 1) & 0x55555555);
        n = (n & 0x33333333) + ((n >>> 2) & 0x33333333);
        n = (n + (n >>> 4)) & 0x0f0f0f0f;
        n = n + (n >>> 8);
        n = n + (n >>> 16);
        return n & 0x3f;
    }
```

该算法只需要6次位运算，应该属于最快的解决方案，思路尚未理解。
