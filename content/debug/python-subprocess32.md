Title: Python subprocess 线程不安全的解决方案
Tags: python
Summary: 1.升级至 Python3.2  2.使用多进程替代多线程 3.在 Python2.7 下使用 subprocess32 包

Python subprocess 不是线程安全的. 虽然文档上没有说明subprocess 是线程安全的, 我们应该把它看做线程不安全来使用. 但是在实际使用中, 我们并不知道 subprocess 的具体哪个方法
是线程不安全的, 于是很难对它加锁, 在这里我认为 subprocess 没有设计成线程安全这件事, 是 Python2.7的一个缺陷.  
所幸依然有三个方法来解决这个问题

1. 升级至 Python3.2  
2. 使用多进程替代多线程  
3. 在 Python2.7 下使用 subprocess32 包

