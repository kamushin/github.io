Title: No space left on device
Tags: debug
Summary: No space left on device

今天当我试着在服务器上创建新文件的时候, 服务器给出了, "No space left on device" 的提示.  
查看`df`后, 发现空间还是挺充裕的, 自然怀疑到 inode 上来. inode 存储了 Linux 系统中的文件元信息, 比如权限, 修改日期等等.inode 的最大数量在分配磁盘的时候被设置好.  

> The inode is a data structure in a Unix-style file system which describes a filesystem object such as a file or a directory. Each inode stores the attributes and disk block location(s) of the object's data.[1] Filesystem object attributes may include metadata (times of last change,[2] access, modification), as well as owner and permission data.[3]])

虽然我没有遇到过 inode 被用光的情况, 但是我依然用 `df -i` 查看了下, 果然看到 home 目录 inode 被用光了.   
接下来我通过逐步探测的方式, 找出是哪个目录占用了大量的 inode  

> `for i in /home/*; do echo $i; sudo find $i |wc -l; done`  
`for i in /home/docker/*; do echo $i;sudo find $i |wc -l; done`    

最后问题锁定在docker上. docker 的 overlays 占用大量 inode, 所以需要把 docker 放在一个 inode 最大值比较大的磁盘上.
