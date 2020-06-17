---
title: Vmware安装Gentoo
date: 2020-6-7 18:38:45
categories: 
    - 教程
tags: 
    - Gentoo
    - Linux
---
# Vmware安装Gentoo

## Gentoo概述

> Gentoo包管理系统的设计是模块化、可移植、易维护、灵活以及针对用户机器优化的。软件包从源代码构建，这延续了ports的传统。但是为了方便，也提供一些大型软件包在多种架构的预编译二进制文件，用户亦可自建或使用第三方二进制包镜像来直接安装二进制包。Gentoo Linux意味着选择，允许用户自由的选择是Gentoo最大的特色。

## 一些需要用的网站

1. [Gentoo Document](https://wiki.gentoo.org/wiki/Handbook:AMD64/Installation/About/zh-cn)

2. [Gentoo Downloads](https://www.gentoo.org/downloads/)

3. Gentoo 相关镜像站
   - [中科大镜像](http://mirrors.ustc.edu.cn/gentoo/)
   - [清华大学镜像](https://mirror.tuna.tsinghua.edu.cn/gentoo/)
   - [阿里云镜像（可用做备用）](https://developer.aliyun.com/mirror/gentoo?spm=a2c6h.13651102.0.0.3e221b11svZPaH)

## 准备工作

温馨提示，在一切就绪前，为了你的身心健康，请先进行以下准备

1. 一个性能不错的电脑
2. 一个能思考的人
3. 若干已离线的电影、书籍、音乐等
4. 强大的心理（以下步骤可能使人产生轻生情绪，请务必确保心情通畅＞︿＜）

如果你已经都准备好了，那么，跟我来吧！

## 磁盘分配

***FBI警告：此项目适用于最小化安装CD，即没有GNU界面的安装，如果是LiveDVD镜像请忽略本条方法，直接使用镜像自带的磁盘分配工具即可***

文档介绍了两种方案，分别是parted和fdisk，以下内容以fdisk展开，对parted感兴趣的可以去[文档](https://wiki.gentoo.org/wiki/Handbook:AMD64/Installation/Disks/zh-cn)查看

### 确定分区方案

为求简便，使用默认的分区方案，见下表

| 分区      | 文件系统                           | 大小   | 描述      |
| --------- | ---------------------------------- | ------ | --------- |
| /dev/sda1 | bootloader                         | 2M     | BIOS boot |
| /dev/sda2 | ext2( fat32 if UEFI is being used) | 128M   | Boot      |
| /dev/sda3 | swap                               | 512M + | Swap      |
| /dev/sda4 | ext4                               | rest   | Root      |

###  创建分区

fdisk是一个流行的和强大的分区工具

```shell
# 进入fdisk终端
fdisk /dev/sda
```

按下p可以看到分区情况，如果不为空，按下d可以删除指定分区

```shell
# 查看所有分区
Command (m for help):p
Disk /dev/sda: 240 heads, 63 sectors, 2184 cylinders
Units = cylinders of 15120 * 512 bytes
  
   Device Boot    Start       End    Blocks   Id  System
/dev/sda1   *         1        14    105808+  83  Linux
/dev/sda2            15        49    264600   82  Linux swap

# 删除分区
Command (m for help):d
Partition number (1-4): 1
```

按下n可以创建分区，各个分区键位信息如下：

- BIOS		n		--- >	p	--- > 1		--- > Enter		--- > +2m
- Boot		n		--- >	p	--- > 2		--- > Enter		--- > +128m		--- > a		--- > 2
- SWAP	  n		--- >	p	--- > 3		--- > Enter		--- > +512m
- Root	    n		--- >	p	--- > 4		--- > Enter		--- > Enter

改变分区文件类型，键位如下：

- Boot		t		--- >	1	--- > 4
- SWAP	  t		--- >	3	--- > 82
- Root		t		--- >	4	--- > 83

按下p显示如下分区：

```shell
Command (m for help):p
Disk /dev/sda: 30.0 GB, 30005821440 bytes
240 heads, 63 sectors/track, 3876 cylinders
Units = cylinders of 15120 * 512 = 7741440 bytes
  
   Device Boot    Start       End    Blocks   Id  System
/dev/sda1             1         3      5198+  ef  EFI (FAT-12/16/32)
/dev/sda2   *         3        14    105808+  83  Linux
/dev/sda3            15        81    506520   82  Linux swap
/dev/sda4            82      3876  28690200   83  Linux
```

最后，**按下w保存退出**

### 创建文件系统

输入以下命令

```shell
mkfs.ext2 /dev/sda2
mkfs.ext4 /dev/sda4
mkswap /dev/sda3
swapon /dev/sda3
```

### 挂载root分区

```shell
mount /dev/sda4 /mnt/gentoo
```



---



## 安装stage3

进入目录

```shell
cd /mnt/gentoo
```

### 下载stage3压缩包

方法很多，可以直接使用wget命令下载或者使用links浏览器下载，不过多进行介绍

***PS.1：如果要使用systemd管理系统，请下载带有systemd文字的stage，否则下载默认的stage即可***

使用以下命令解压压缩包

```shell
tar xpvf {你下载的stage压缩包} --xattrs-include='*.*' --numeric-owner
```

### 进行编译配置

修改必要的配置

```shell
nano -w /mnt/gentoo/etc/portage/make.conf
```

添加以下内容：

```shell
# 修改国内源
GENTOO_MIRRORS="https://mirrors.ustc.edu.cn/gentoo/"
# 编译核心数
MAKEOPTS="-j2"
```

### 修改portage配置

创建配置文件

```shell
mkdir /mnt/gentoo/etc/portage/repos.conf
nano -w /mnt/gentoo/etc/portage/repos.conf/gentoo.conf
```

写入以下内容

```ini
[gentoo]
location = /usr/portage
sync-type = rsync
#sync-uri = rsync://mirrors.tuna.tsinghua.edu.cn/gentoo-portage/
sync-uri = rsync://rsync.mirrors.ustc.edu.cn/gentoo-portage/
auto-sync = yes
```

### 复制dns

```shell
cp -d /etc/resolv.conf /mnt/gentoo/etc/
```

### 挂载文件系统

```shell
mount --types proc /proc /mnt/gentoo/proc
mount --rbind /sys /mnt/gentoo/sys
mount --make-rslave /mnt/gentoo/sys
mount --rbind /dev /mnt/gentoo/dev
mount --make-rslave /mnt/gentoo/dev
```

### 进入新环境

```shell
# 将根位置/更改为/mnt/gentoo
chroot /mnt/gentoo /bin/bash
# 重新载入配置
source /etc/profile

# 挂载boot分区
mount /dev/sda2 /boot
```

### 配置portage

从Gentoo的一个镜像中获取最新的快照并将其安装到系统上：

```shell
emerge-webrsync

# 跟新最近更新的软件包（安装时谨慎选择，时间非常长，我这破电脑搞了5个多小时还没好）
emerge --sync
```

阅读新闻

```shell
eselect news read
```

列出配置文件，下方仅为示范

```shell
root #eselect profile list
Available profile symlink targets:
  [1]   default/linux/amd64/17.1 *
  [2]   default/linux/amd64/17.1/desktop
  [3]   default/linux/amd64/17.1/desktop/gnome
  [4]   default/linux/amd64/17.1/desktop/kde
```

选择配置文件

```shell
# profile前的数字
eselect profile set {number}
```

更新@world**（时间杀手）**

```shell
emerge -avuDN @world
```

### 修改时区（可选）

```shell
echo "Asia/Shanghai" > /etc/timezone

# 重新配置
emerge --config sys-libs/timezone-data
```

### 修改地区（可选）

```shell
nano -w /etc/locale.gen

# 添加以下内容
en_US ISO-8859-1
en_US.UTF-8 UTF-8
zh_CN GBK 
zh_CN.UTF-8 UTF-8

# 生成指定地区
locale-gen

eselect locale list
eselect locale {number}

# 重新加载环境
env-update && source /etc/profile
```



---



## 内核配置

### 下载内核

```shell
emerge --ask sys-kernel/gentoo-sources
```

手动编译是个巨坑[哭脸]，还是老老实实的自动编译吧＞︿＜

### 自动配置

```
# 下载工具
emerge --ask sys-kernel/genkernel
nano -w /etc/fstab

# 写入boot分区信息
/dev/sda2	/boot	ext2	defaults	0 2

# 编译内核
genkernel all
```



---



## 系统配置

### 指明分区

**此步骤必须要有**，写入的内容根据你的分区信息来写，只要是需要独立挂载的分区，都要写进去！

```shell
nano -w /etc/fsatb

# 写入以下内容
/dev/sda3   none   swap    sw           0 0
/dev/sda4   /      ext4    noatime      0 1
  
/dev/cdrom  /mnt/cdrom  auto   noauto,user   0 0
```



---



## 引导

### 下载grub

```shell
emerge --ask --verbose sys-boot/grub:2
```

### 安装

这里的安装是以BIOS启动的，如果要以UEFI方式引导，可以其看官方文档

```
grub-install /dev/sda
grub-mkconfig -o /boot/grub/grub.cfg
```

## 重启

一切就绪，把安装镜像卸下，重启试试吧（￣︶￣）↗　

```shell
reboot
```

