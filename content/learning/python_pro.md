Title: Write Python like a Pro
Tags: Python
Summary: Something I know about how to write Python code

### Context Managers
If you have a function `do_sth()`, before invoking this method, it needs connect to Database and get filelock. And code maybe like this:  
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
What if `do_sth` be called at many palces? If filelock is now don't need, code should be rewrited at each palce when `do_sth` is called.   
After wasting a whole afternoon rewriting the code, you find it's useful to have a function to do this. Then code will be:  
``` 
  try:
    prepare()
    do_sth()
  except:
    ...
  finally:
    close()

```
Each palce `do_sth` invoked is full of `prepare/close`. And both of them has no relation with bussiness logic. It makes the code longer and longer.  
Although you don't care about the cofusion you may have when you see these code after 2 months(because the only one line of bussiness logic code is hidden in seven lines of non-business code),
you should be friendly to those who review your code. A funciton more than 500 lines is horrible. I think writing code is an action to get abstraction from complex logic, if there is no 
abstraction in code, it's not coding but translating.
What `prepare/close` doed indeed? They are preapre or release an environment to `do_sth`, that is context.  
Python use `with` statement to manage context.

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
Now the reviewer will only see
```
  with A() as a:
    a.do_sth()
```
Context manager is uesd explictly. Bussiness logic and impelement are splited.

> Explicit is better than implicit.
  Simple is better than complex.

Anthor common way is using `__del__`
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
The good part of this way is no need of wiring `with`. But it's not a explicit context manager.
To `GC` languages like Python or Java, there is no way to invoke a destructor method.
Although object has leaved the scope, if it was not cleaned by `GC`, the resource it takes will not be released.  
If the resource is database connect, close lately is acceptable, but to resource like `mutex`, we need `with` statement to release it immediately.


### Generation
A function with `yield` is a generator. Generation maintains a context to eval result when it is need.
For example:  
```
  for i in range(100000):
      do_sth()
```
It creates an array of 1-100000 before `do_sth` which will make a waste of memory. 
Another loop with `xrange`:
```
  for i in xrange(100000):
      do_sth()
```
That is what we know in C++, `do_sth` once and then `i++`, loops. 
```
  for(int i = 0; i < 100000; i++) {
      do_sth()
  }
```
So `xrange` will use less memory than `range`.

```
    def fetchmany(self, *args, **kwargs):
        '''
           A generator to fetch data.
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
`fetchmany` is a generator, and a generator is iteratable. Only 200 rows will be taken in a patch, not all of the results.  


Generator can also be used to make a co-routine.  
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
More useful cases in `Tornado`.  


### Decorator
Decorator is a useful syntax sugar to split implement detail.
For example
```
  begin = time.time()
  do_sth()
  end = time.time()
  print 'do sth used %s second' % (end-begin)

```
In above code, profile code is mixed in logic code.  
By decorator  
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
When `do_sth` be invoked, the caller don't need to know about `logtime`.
There is also a `@` used in Java. But that is a `annotation`, it's not run-time but a complie time reflect.  
That has no relation with decorator in Python.

### Unicode
Here are some code to show the relation with `unicode` and `str`

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
In Python2, `str` is byte array and `unicode` is charset code of the character.

















