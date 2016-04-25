Title: Python multiprocessing WHY and HOW
Tags: python
Summary: Some thinking and traps in refactor multithreading Python to multiprocessing.


I am working on a Python script which will migrate data from one database to another. In a simple way, I need `select` from a database and then `insert` into another.  
In the first version, I designed to use multithreading, just because I am more familiar with it than multiprocessing. But after fewer month, I found several problems in my workaround.  

- can only use one of 24 cpus in case of GIL
- can not handle singal for each thread. I want to use a simple `timeout` decarator, to set a `signal.SIGALRM` for a specified function. But for multithreading, the signal will get caught by a random thread.

So I start to refactor to multiprocessing.


### multiprocessing

> multiprocessing is a package that supports spawning processes using an API similar to the threading module. 

But it's not so elegant and sweet as it described.

#### multiprocessing.pool

```Python

from multiprocessing import Pool

def f(x):
    return x*x

if __name__ == '__main__':
    p = Pool(5)
    print(p.map(func=f, [1, 2, 3]))

```


It looks like a good solution, but we can not set a `bound function` as a target `func`. Because `bound function` can not be serialized in `pickle`. And `multithreading.pool` use pickle to serialize object and send to new processes.
`pathos.multiprocessing` is a good instead. It uses `dill` as an instead of `pickle` to give better serialization.

#### share memory

Memory in multithreading is shared naturally. In a multiprocessing environment, there are some wrappers to wrap a sharing object.

- `multiprocessing.Value` and `multiprocessing.Array` is the most simple way to share Objects between two processes. But it can only contain `ctype` Objects.
- `multiprocessing.Queue` is very useful and use an API similar to `Queue.Queue`


#### Python and GCC version

I didn't know that even the `GCC` version will affect behavior of my code. On my centos5 os, same Python version with different `GCC` version will have different behaviors.
```

Python 2.7.2 (default, Jan 10 2012, 11:17:45)
[GCC 3.4.6 20060404 (Red Hat 3.4.6-11)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from multiprocessing.queues import JoinableQueue
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/oracle/dbapython/lib/python2.7/multiprocessing/queues.py", line 48, in <module>
    from multiprocessing.synchronize import Lock, BoundedSemaphore, Semaphore, Condition
  File "/home/oracle/dbapython/lib/python2.7/multiprocessing/synchronize.py", line 59, in <module>
    " function, see issue 3770.")
ImportError: This platform lacks a functioning sem_open implementation, therefore, the required synchronization primitives needed will not function, see issue 3770.


Python 2.7.2 (default, Oct 15 2013, 13:15:26)
[GCC 4.1.2 20080704 (Red Hat 4.1.2-46)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from multiprocessing.queues import JoinableQueue
>>>
```
