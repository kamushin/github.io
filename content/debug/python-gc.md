Title: 从一次失效的文件锁看看 Python 的垃圾回收机制
Tags: python gc
Summary: 不同的调用方式导致了文件锁的成功与失效, 原因是触发了 Python 的垃圾回收机制. Python的垃圾回收机制还是比较原始的, 基本上就是引用计数, 标记清除和分代.没有什么黑魔法.

### 引

有同事发现 Python 在函数中进行文件锁, 退出函数后, 文件锁就失效了. 我简单想下, 应该是函数中锁文件后, 退出函数, 文件句柄变量被 GC, 导致文件锁也失效了.  
写了段代码验证这个情况.

```

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import fcntl
import time


def inline():
    fcntl.flock(open('/tmp/locktest', 'w'), fcntl.LOCK_EX | fcntl.LOCK_NB)

def twoLines():
    fd = open('/tmp/locktest', 'w')
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return fd


lockFile = inline # will print No error
# lockFile = twoLines  # will print blocking 
fd = None

fd = lockFile()
try:
    fd = lockFile()
except IOError:
    print("can't immediately write-lock the file ($!), blocking ...")
else:
    print("No error")

```

### Python 中实现的 GC

#### 引用计数

>最早期的垃圾回收实现方法，通过对数据存储的物理空间附加多一个计数器空间，当有其他数据与其相关时则加一，反之相关解除时减一，定期检查各储存对象的计数器，为零的话则认为已经被抛弃而将其所占物理空间回收。是最简单的实现，但存在无法回收循环引用的存储对象的缺陷。

```
// object.h
struct _object {
    Py_ssize_t ob_refcnt;
    struct PyTypeObject *ob_type;
} PyObject;

```
在 Python 源码中, 类的结构体都具有一个`ob_refcnt`的部分, 用来做引用计数.

引用计数的优点是高效,不需要停顿,易于实现, 缺点是无法解决循环引用, 计数次数和引用赋值成正比, 而 mark and sweep则只和对象数量成正比.



#### 标记清除

>近现代的垃圾回收实现方法，通过定期对若干根储存对象开始遍历，对整个程序所拥有的储存空间查找与之相关的存储对象和没相关的存储对象进行标记，然后将没相关的存储对象所占物理空间回收。

```
// objimpl.h
typedef union _gc_head {
    struct {
        union _gc_head *gc_next;
        union _gc_head *gc_prev;
        Py_ssize_t gc_refs;
    } gc;
    long double dummy;  /* force worst-case alignment */
} PyGC_Head;

```
在申请内存时，所有容器对象的头部又加上了`PyGC_Head`来实现"标记-清除"机制.垃圾标记时，先将集合中对象的引用计数复制一份副本(以免在操作过程中破坏真实的引用计数值), 然后操作这个副本，遍历对象集合，将被引用对象的引用计数副本值减1, 
然后根据引用计数副本值是否为0将集合内的对象分成两类，reachable和unreachable，其中unreachable是可以被回收的对象. 这是一个比较基础的标记清除的过程.

#### 分代回收

>由于“复制”算法对于存活时间长，大容量的储存对象需要耗费更多的移动时间，和存在储存对象的存活时间的差异。需要程序将所拥有的内存空间分成若干分区，并标记为年轻代空间和年老代空间。程序运行所需的存储对象会先存放在年轻代分区，年轻代分区会较为频密进行较为激进垃圾回收行为，每次回收完成幸存的存储对象内的寿命计数器加一。当年轻代分区存储对象的寿命计数器达到一定阈值或存储对象的占用空间超过一定阈值时，则被移动到年老代空间，年老代空间会较少运行垃圾回收行为。一般情况下，还有永久代的空间，用于涉及程序整个运行生命周期的对象存储，例如运行代码、数据常量等，该空间通常不进行垃圾回收的操作。
通过分代，存活在局限域，小容量，寿命短的存储对象会被快速回收；存活在全局域，大容量，寿命长的存储对象就较少被回收行为处理干扰。

```
// gcmodule.c
struct gc_generation {
    PyGC_Head head;
    int threshold; /* collection threshold */
    int count; /* count of allocations or collections of younger
              generations */
};

```
Python默认定义了三代对象集合，索引数越大，对象存活时间越长。

```
#define NUM_GENERATIONS 3
#define GEN_HEAD(n) (&generations[n].head)

/* linked lists of container objects */
static struct gc_generation generations[NUM_GENERATIONS] = {
    /* PyGC_Head,               threshold,  count */
    {{{GEN_HEAD(0), GEN_HEAD(0), 0}},   700,        0},
    {{{GEN_HEAD(1), GEN_HEAD(1), 0}},   10,     0},
    {{{GEN_HEAD(2), GEN_HEAD(2), 0}},   10,     0},
};

```
新生成的对象会被加入第0代, 每新生成一个对象都会检查第0代有没有满，如果满了就开始着手进行垃圾回收.


### flock的失效

上面简单复习了下 Python 的 GC 机制. 可以知道因为没有其他对象持有文件句柄的引用, 所以在离开函数作用域后就被回收, 那么持有的文件锁也就被释放了.
