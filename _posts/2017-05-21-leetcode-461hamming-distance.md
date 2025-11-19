---
title: "Leetcode 461:hamming distance"
date: "2017-05-21 22:51:12"
slug: "leetcode-461hamming-distance"
layout: "post"
categories: ["算法和数据结构"]
tags: ["leetcode"]
---
hamming distance（汉明距离）数字二进制中按位不相等的个数。

本题中，条件规定x，y取值区间为[0,2^32）

算法1：x和y做按位与运算，得到的值右移直到0，统计1的个数。

一次按位与运算，每次循环中一次按位与运算

```
public class HammingDistance {

    private static int hammingDistance(int x, int y) {
        int val = x ^ y;
        int num = 0;
        while (val > 0) {
            if ((val & 1) == 1) {
                num ++;
            }
            val = val >> 1;
        }
        return num;
    }

    public static void main(String[] args) {
        System.out.println(hammingDistance(1, 4));
    }
}
```

算法2，最多循环32次，每次循环中3次按位与运算。

每次循环中

（1）先取val为1左移n位，n为0~31区间取值，val与当前x和y分别做按位与运算

（2）如果val值大于x和y，则说明已经没有可比较的值，跳出循环即可

（3）按位与运算结果为x和y第i位是否为1，如果x和y当前位不相等，则最终结果num+1

```
public class HammingDistance {
    private static int hammingDistance(int x, int y) {
        int num = 0;
        for (int i = 0; i < 32; i++) {
            int val = 1 << i;//1
            if (val > x && val > y) {//2
                break;
            }
            if ((x & val) != (y & val)) {//3
                num ++;
            }
        }
        return num;
    }

    public static void main(String[] args) {
        System.out.println(hammingDistance(1, 4));
    }
}
```
