Title: Python开发经验--从问题入手
Tags: Python
Summary: 从一系列实际问题出发, 谈 Python 的一些使用知识

### 上下文管理
如果你要做一件事情`do_sth()`，在这之前，需要连接数据库，需要持有文件锁。那么你很可能这么写：
```
try:
    db.connect()
    getfilelock()
    do_sth()
except:
    ...
finally:
    releasefilelock()
    db.close()
```
 
如果`do_sth`在 N 个地方出现呢？如果我策略修改了，不再需要`filelock` 了呢？是不是需要去改这 N 个地方？  
花了一下午去修改了 N 个地方，测试了几次终于没有遗漏后，你发现这个做法多么低效，于是你终于想起来用一个函数去做这件事情。  
你把代码写成了这样  
```
try:
    prepare()
    do_sth()
except:
    ...
finally:
    close()
```

`do_sth`所在的 N 个地方，都写满了 `prepare`, `close` 这一系列和业务逻辑无关的代码, 这使得我们的代码变得冗长。
即使你不在乎自己过了两个月后是否还愿意看这段代码，至少你要照顾下帮你 review 代码的人，一个函数写了500行还能 review 吗？
我认为一个程序员写代码的过程，就是从复杂的逻辑中进行抽象的过程，如果不进行抽象，那么就不是写代码，而是在做翻译。我们来看看这里有什么可以抽象的。  
`prepare`, `close` 这些是在做什么？是在预备和释放一个可以`do_sth`的环境，也就是我们常说的上下文管理。  
Python 提供了`with`语句来帮助我们管理上下文。代码变成了这样：
```
class A():
    def do_sth(self):
        pass

    def __enter__(self):
        db.connect()
        getfilelock()
        return self

    def __exit__(self, type, value, traceback):
      releasefilelock()
      db.close()

with A() as a:
    a.do_sth()
```
现在帮你 review 代码的人，只会在那 N 个`do_sth` 存在的地方，看到  
```
  with A() as a:
    a.do_sth()
```
很显示的使用了上下文进行管理，分离了业务逻辑和具体实现。
> Explicit is better than implicit.
  Simple is better than complex.

另一个常见的做法是使用`__del__`
```
class A():
    def __init__(self):
        db.connect()
        getfilelock()

    def __del__(self, type, value, traceback):
        releasefilelock()
        db.close()

a =  A()
a.do_sth()
```
这个做法的优点是不需要写`with` 语句，缺点是这不是明显的上下文管理，对于 Python/Java 这种带
`GC` 的语言来说，是不能手动调用一个对象的析构函数的，即使对象离开了作用域，它依然会因为还没有被`GC`而存活。  
所以对于锁这样的，我们需要很快去释放的资源，使用`with` 更加的可控。
可能会有人去对比 C++ 中的`RAII` 规则，Python中是做不到 `RAII` 的, 因为以上原因。


### 生成器
一个函数如果在代码段中有 `yield` 那么它就从一个函数变成了一个 `generator`。生成器的好处是保留了一个上下文在需要时去运算。  
同样从一个实际例子出发：  
```
  for i in range(100000):
    do_sth()
```
这段代码，在什么都没做之前，就产生了一个1-100000这些数字的数组，占用了内存。  
而
```
  for i in xrange(100000):
    do_sth()
```
这才是我们知道的C++中的
```
  for(int i = 0; i < 100000; i++) {
    do_sth()
  }
```
执行一次 `do_sth`，再生成一次 i 值。   
所以`xrange`会比`range`更省内存。（在 Py2 是这样。Py3中，`range` 就是 Py2 的 `xrange`。 另外据我所知，不存在 xrange 是 C 实现这么一回事)。
再来一个例子：
```
def fetchmany(self, *args, **kwargs):
    '''
       A generator to fetch data.
       prams: numRows -> the number of rows to fetch.
    '''
    cur = self._conn.cursor()  
    numRows = 200
    try:
        cur.execute(*args, **kwargs)
        self._conn.commit()
    except Exception as e:
        self.logger.error(str(e))
        self._conn.rollback()
        return
    while True:
        rows = cur.fetchmany(numRows)
        if rows:
            yield rows
        else:
            cur.close()
            return

for rows in fetchmany(sql):
  do_sth_with_rows(rows)

```
这就实现了每次取出200条，消费完再取200条。而不是一次性取到内存中。同时也封装了`commit`，`rollback`等操作。

生成器也可以用来构造对称式协程
```
import random

def get_data():
    """Return 3 random integers between 0 and 9"""
    return random.sample(range(10), 3)

def consume():
    """Displays a running average across lists of integers sent to it"""
    running_sum = 0
    data_items_seen = 0

    while True:
        data = yield
        data_items_seen += len(data)
        running_sum += sum(data)
        print('The running average is {}'.format(running_sum / float(data_items_seen)))

def produce(consumer):
    """Produces a set of values and forwards them to the pre-defined consumer
    function"""
    while True:
        data = get_data()
        print('Produced {}'.format(data))
        consumer.send(data)
        yield

if __name__ == '__main__':
    consumer = consume()
    consumer.send(None)
    producer = produce(consumer)

    for _ in range(10):
        print('Producing...')
        next(producer)
```
在这个例子中， 不需要队列，就做到了一个一对一的生产与消费。当然这个1对1的并没有什么实际意义。对于协程和生成器的作用，如果感兴趣，可以看看`Tornado`的实现。

### Exception

这块Python和其他语言没什么不同的，拿出来讲是因为看到很多代码里充满了魔数。  
比如 `return 'unknown'`. 既然是`unknown`就应该抛出异常。而不是用一堆的常量字符串在各个函数直接传来传去。  
类似的例子还有`return 'ok'`, `return 'mysql'`, `return 2`.   
另外尽可能抛出和接收特定的异常。


### Functional Programming

Python 其实是不怎么 FP 的，不过一些基本的 FP 支持还是有的。  
比如高阶函数，`map reduce filter`。  
用`map reduce filter` 可以更好的做抽象。  
`reduce(lambda x, y: x + y, query_res)`  
很简单就能看出，虽然我不知道具体 `x`,`y` 是什么，但是我知道，这是把 `query_res` 中的每个值加到一起。  
不用去管`x`, `y`的类型，只需要他们支持`+`操作。这种编程思维可以再次把业务逻辑和实现分开。


### Decorator
装饰器算是 Python 的一大亮点。看下面这个例子：
```
  begin = time.time()
  do_sth()
  end = time.time()
  print 'do sth used %s second' % (end-begin)

```
业务逻辑里混杂着统计时间的逻辑。添加要加三行，什么时候不要了，又要删三行。
如果用上装饰器
```
def logtime(func):
    @wraps(func)
    def wrapper(*args, **kwds):
        start_time = time.time()
        ret = func(*args, **kwds)
        use_time = time.time() - start_time
        if use_time > 1.0:
            logging.info("%s use %s s", func.__name__, use_time)
        return ret
    return wrapper

@logtime
def do_sth():
  ...



do_sth()
```
代码被调用的时候，不需要知道做了时间的统计，也不需要把统计代码混杂在业务逻辑中。   
考虑下面的代码，用 Java 应该怎么实现？
```
def make_spin(spin_style=Default, words=""):
    spinner = Spinner(spin_style)
    queue = Queue()

    def add_queue(func):
        @wraps(func)
        def wrapper():
            func()
            queue.put_nowait(1)
        return wrapper

    def decorator(func):
        @wraps(func)
        def wrapper():
            process = Process(target=add_queue(func))
            process.start()
            while queue.empty():
                print(text_type("\r{0}    {1}").format(spinner.next(), words),
                      end="")
                sys.stdout.flush()
                time.sleep(0.1)
            print('')
        return wrapper
    return decorator

```

Java中同样也有`@`字符的运用，不同的是，Java中那个叫`annotation`, 也就是注解。 
注解是编译期的，它是用来做反射的，也就是提供给外部一些关于我本身信息的。和 Python 的用法没有关系。  


### Unicode
下面直接用一些例子来显示 Python2中的 Unicode 和 Str 的关系。

```
>>> a = '我'
>>> a
'\xe6\x88\x91'
>>> type(a)
<type 'str'>

>>> b = '我'.decode('utf-8')
>>> b
u'\u6211'
>>> type(b)
<type 'unicode'>

>>> b.encode('utf-8')
'\xe6\x88\x91'
>>> b.encode('gbk')
'\xce\xd2'


```
很明显可以看出，Python2中，str 类型其实是 byte 字节流。而 Unicode 类型则是表示了 Unicode 字符号。

















