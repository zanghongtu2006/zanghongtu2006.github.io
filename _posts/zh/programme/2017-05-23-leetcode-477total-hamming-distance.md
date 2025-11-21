---
title: "LeetCode 477:Total Hamming Distance"
date: "2017-05-23 17:28:58"
slug: "leetcode-477total-hamming-distance"
layout: "post"
categories: ["算法和数据结构"]
tags: ["leetcode"]
---
输入一个int数组，求所有数hammingDistance的和。

鉴于之前的程序，直观算法为逐对求hamming distance然后求和，时间复杂度为n^2

```
    public int hammingDistance(int x, int y) {
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
    
    public int totalHammingDistance(int[] nums) {
        int result = 0;
        for(int i = 0; i < nums.length - 1; i++) {
            for(int j = i + 1; j < nums.length; j++) {
                result += hammingDistance(nums[i], nums[j]);
            }
        }
        return result;
    }
```

大部分测试通过，一个巨大的数组出现LTE。

百度发现一个更好的思路：按位来计算，每位有m个1和n个0，则该位hammingDistance=m\*n。

实际上这个问题实质在于求所有数字每位上1的个数。

```
    public int totalHammingDistance(int[] nums) {
        int result = 0;
        
        for (int j = 0; j < 32; j++) {
            int count = 0;
            for (int i = 0; i < nums.length; i++) {
                if (nums[i] == 0) {
                    continue;
                }
                count += nums[i] & 1;
                nums[i] >>= 1;
            }
            result += (count * (nums.length-count));
        }
        return result;
    }
```
