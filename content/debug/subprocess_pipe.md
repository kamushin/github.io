Title: Python subprocess包中的父子进程沟通
Tags: Python
Summary: Python subprocess包中父子进程如何沟通， 使用不当又会有什么后果。

### 前言

前段时间是5.27蚂蚁技术日，听了康朵分享的关于创新的一些特质，记录一下，权且是自勉。  

创新需要以下几点能力：

- **学习能力** 没有学习能力，别说创新，跟上大环境都难
- **解构能力** 没有解构能力，无法把复杂问题分解为已知问题去解决
- **系统性思维** 这点我觉得很难做到，是内功
- **交朋友能力** 主要指认识大牛
- **化繁为简** 这个和解构差不多吧
- **对美的追求** 很多烂设计，如果对美有要求，根本不会让它出现。这点我深有体会。那种接到一个需求就做，从来不考虑怎么去更完美的实现的人，肯定是给团队挖坑最多的人。

### 引言

10多天前，我写了篇文章谈如何调试一个hang住的Python程序，最后发现程序是因为打日志把buffer打满了，而产生了阻塞。
> 当你发现家里有一只蟑螂的时候，可能你家里已经有了一个蟑螂窝。

这话用了形容这几天的发现着实不假，当你发现一个legacy项目的代码中有了一个暗藏的坑后，项目中其他的代码可能也都是这个坑。 这周果然又在其他代码中发现了这个问题，并引起了一个小故障。
在故障的改进措施中，我发现大家其实对操作系统的一些基础知识已经不是那么熟悉了，所以今天再写篇文章，复盘下这个坑。


### subprocess

Python中可以使用`subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)`来开启一个子进程。
两处埋坑的代码，一摸一样的错误，都是试图在子进程返回后才去读子进程的stderr的PIPE。这就带来了一个坑，子进程在没返回前就把这个PIPE打满了，父进程不去读PIPE，而是在等子进程返回，子进程则在等父进程读PIPE消耗缓冲区，产生了死锁。
> Warning This will deadlock when using stdout=PIPE and/or stderr=PIPE and the child process generates enough output to a pipe such that it blocks waiting for the OS pipe buffer to accept more data. Use communicate() to avoid that.)

这个坑，可能太经典了吧，以至于Python官方文档都要做个爱心提示了[1]

### communicate

在上文中提到，要避免死锁，需要用`communicate()`, 那做个函数做了什么事情避免了死锁呢？  
其实它也只是做了一点微小的工作，那就是用`select`读父子进程间的管道，直到EOF，然后调用`wait()`等待子进程返回.  
今天我在看改进方案时，发现同学尝试用非阻塞读去解决上面那个问题，我觉得是牛头不对马嘴。首先要搞清楚，程序hang住不是因为buffer空着去读buffer，然后读阻塞。而是buffer写满了，造成的写阻塞。用非阻塞读去解决写阻塞的问题，我真是不知道说什么好了。
解决方法就是，在子进程返回前，要不停的去探测子进程有没有输出，即文件是否可读，保证buffer不被打满。至于怎么去读，用IO复用也好，判断可读后用阻塞读，无需判断可读性直接非阻塞读也罢, 还是另开线程直接阻塞读也是个更好的方法，都不是问题。[2] 关键就是，**要在`wait()`前读文件**.



### 参考资料

[1]  https://docs.python.org/2/library/subprocess.html#subprocess.Popen.wait  
[2]  《Unix 网络编程》
