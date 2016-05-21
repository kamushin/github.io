Title: Python 调试方法
Tags: Python
Summary: 在解决一个线上程序 hang 住的过程中, 研究了几种 Python 调试方法, 总结下各自的优缺点.


### 背景
这几天一直在查一个线上程序 hang 住的问题. 这个程序总是在运行50分钟后 hang 住, 通过以下的一些调试手段,发现是打日志的时候因为 buffer 满被 block 了.
Python 日志是默认打到 stderr 的, 无论日志级别. 而我这个程序是被另一个程序调起的, 父进程没有接收子进程的 stderr, 导致了 buffer 被打满.
在调试的过程中, 用到了以下几种 Python 调试手段, 于是记录以下.



### GDB
GDB是一个广为人知的调试器, 而且线上可用, 非常赞. 但是默认配置的 GDB 并不能打印 Python 当前调用栈. 我们需要对其做些配置.   
首先进行gdb的安装, 需要gdb7以上版本  
`sudo yum install gdb python-debuginfo`   
然后下载这份 gdb 配置文件` http://svn.python.org/projects/python/trunk/Misc/gdbinit ` 到 `~/.gdbinit`  
对于一个线上已经hang住的程序来说, 可以用` gdb -p pid `的形式进行 attach, 打印出当前调用栈.  
一般来说, 必须是带`debug symbol`的Python 编译版本才能打印出足够多的信息, 但是线上的 Python 版本往往是不带`debug symbol` 的, 于是我们要修改下上述的配置文件
```
    <<<<         if $pc > PyEval_EvalFrameEx && $pc < PyEval_EvalCodeEx
    >>>>         if $pc > PyEval_EvalFrameEx && $pc < PyEval_EvalCodeEx && $fp != 0
```
对`~/.gdbinit` 进行上述修改, 即可成功打印出当前 hang住进程的调用栈.  
具体到我这次遇到的问题, 在打出调用栈后发现是卡死在 log 模块的 emit 上, 于是 strace 下看到果然是卡死在 write 的系统调用上, 顺利找到了原因.  
更多的用法可以看https://wiki.python.org/moin/DebuggingWithGdb, 不过大部分的用法依然需要`debug symbol`, 按照 wiki 来,不一定可以顺利实现.

### PDB
PDB是 Python 自带的一个调试模块. 可以以`python -m pdf xxx.py` 的形式, 以调试模式启动一个 Python 进程.
虽然似乎不能 attach 到已运行的进程上, 但是提供了一个简单快速的调试方式.

### Singal AND InteractiveConsole
上述的方式都是不需要侵入代码的, 这里再提供一种侵入代码的方式.
```
import code, traceback, signal

def debug(sig, frame):
    """Interrupt running process, and provide a python prompt for
    interactive debugging."""
    d={'_frame':frame}         # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    i = code.InteractiveConsole(d)
    message  = "Signal received : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    i.interact(message)

def listen():
    signal.signal(signal.SIGUSR1, debug)  # Register handler

```
基本原理是给`SIGUSR1`信号加上一个handler, handler 执行时会把当前的变量加载到一个交互式窗口, 然后开启交互式console, 接下来就像打开一个 REPL 一样了, 可以查看当前的变量值, 可以改变变量值, 可以调用函数看看结果是什么, 查看完后`^d`离开, 就可以让程序继续执行下去.   
在加好 handler 后, 我们可以用`os.kill(pid, signal.SIGUSR1)`的方式, 调起 handler, 进行调试.  
值得注意的是, 由于和console 的交互需要 stdout 的支持, 而父子进程默认是不共享 stdout 的,所以当要调试子进程的时候, 需要重定向子进程的 stdout 到父进程的 stdout, 这个很简单,就不贴代码了.
