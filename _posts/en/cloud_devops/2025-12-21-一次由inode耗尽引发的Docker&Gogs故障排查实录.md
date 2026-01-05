---
layout: post
lang: en
slug: duolingo-en-de-upgrade-a2
permalink: /en/inode-caused-break-down-trouble-shooting/
translations:
  en: /en/inode-caused-break-down-trouble-shooting/
  zh: /zh/inode-caused-break-down-trouble-shooting/
title: "A Troubleshooting of a Docker & Gogs Fault Caused by Inode Exhaustion"
date: 2025-11-27 22:51:00 +0100
categories: ["Diary"]
---
## Backgroud

On one of my Linux cloud servers, Docker started frequently reporting the error:

no space left on device

However, checking the disk space with `df -h` revealed that there was still a significant amount of free disk space.

This seems counterintuitive at first glance, but it's precisely a classic and subtle problem in Linux systems.

## 1. Initial observation: The disk has space, but Docker is "full".

check：
```shell
df -h
```

The results showed that there was sufficient disk space, but Docker failed to start the container and wrote the file.   
The build failed.   
This indicates that the problem is not with the block space (disk capacity).

## 2. Check inode

```shell
df -i
```

The results are crucial:  
```shell
Filesystem      Inodes   IUsed   IFree IUse% Mounted on
/dev/vda2      3932160 3929865    2295  100% /
```
The root partition inodes are 100% exhausted.

Conclusion:   
The system is unable to create any new files, even though there is still disk space available.

Docker, Git, logs, and temporary files all essentially rely on inodes.

## 3、Do not find，use du --inodes to find the root cause
On a system where inodes are running out:  
Do not use `find /`  
Do not perform a full disk scan  

The correct approach is to narrow down the search layer by layer:
```shell
du --inodes -d 1 / | sort -nr | head
```

The result was truly astounding：
```shell
3648582 /opt
149766  /var
```

The /opt directory occupies over 92% of the inodes.

## 4. Find out the root cause：Gogs

continue this finding：
```shell
du --inodes -d 1 /opt | sort -nr | head
```

There is a directory：

**/opt/docker/gogs**

The server is running a Docker-deployed Gogs (Git service).

## 5. Why does Gogs consume millions of inodes?

Further investigation revealed the following:  
Gogs' Git repository is located on the host machine at /opt/docker/gogs/data/git  
Each repository, in addition to the main repository, automatically creates a separate repository:   
```text
<repo>.wiki.git
```

Key point：
Gogs' Wiki is essentially a "standalone Git repository."  
Git's storage characteristics are:  
Each object = a small file  
Each small file = an inode  
Wiki edits are frequent, but garbage collection (GC) is almost never performed  
Loose objects can grow indefinitely.

## 6. Why does GC fail?

try：  
```shell
git gc --aggressive --prune=now
```

It is failed soon：  
```shell
unable to create packed-refs.new: No space left on device
```

The reason is simple:  
Git GC itself needs to create new files, but inodes are already 100% exhausted.  
This is a typical "deadlock scenario":  
Want to perform GC → Need inodes    
Inodes full → GC cannot be performed

## 7. Key Breakthrough: Deleting *.wiki.git

After confirming that the Wiki content was completely unimportant, the following was decisively executed:
```shell
rm -rf /opt/docker/gogs/data/git/gogs-repositories/*/*.wiki.git
```
The effects were immediate:  
Inode usage dropped instantly  
System became writable again  
Docker/Git returned to normal  
Wiki repositories were one of the main causes of the inode explosion.  

## 8. Follow-up work after problem resolution

Run Git GC again (this time it should succeed).
Disable the Wiki feature in Gogs:
**DISABLE_WIKI = true** 

Long-term plan:  
**Migrate Git repository to a separate disk**  
**Perform regular git garbage collection**  
**Inode monitoring and alerting**

## 9. Summarize

The root of the problem isn't:  
Docker issues  
Linux issues  
Disk capacity issues  
but rather:  
Inodes being consumed by Git (especially Wiki repositories) over a long period without the user noticing.  

Lessons learned:  
**df -h doesn't show everything, df -i is equally important.**  
**Git ≠ database, and is even less suitable for storing numerous small changes.**  
**Wikis are hidden inode killers.**  
**Docker is just the "first to warn"**  

# Conclusion

This is a very typical and valuable troubleshooting case.  

If your server simultaneously hosts:  
Docker  
Git services (Gogs/Gitea/GitLab)  
Root partition running for many years  

**It is strongly recommended that you check the inode now.**
