Title: coroutine in Python Tornado and NodeJs
Tags: coroutine
Summary: source code read

`yield` and `generator` will be the front knowledge of this article. And you should also have some sense of `epoll/kqueue` and `callback style`.  
Let's enjoy the source code of the implement of coroutine.   
### Python Tornado
A simple async fetch function used by a coroutine in Python, exception handle removed   
```Python
def fetch(self, request):
    future = TracebackFuture() # TracebackFuture == Future
    def handle_response(response):
        future.set_result(response)
    self.fetch_impl(request, handle_response) # This is a async function
    return future

def fetch_impl(self, request, callback):
    pass
```
`future` -- an instance of `Future` -- is an object that used to collect and send result to `generator`.  

A coroutine that uses above `fetch`
```Python
@gen.coroutine
def request(self, uri):
    response = yield http.fetch(uri)
```

And we all know `@gen.coroutine` is a syntax sugar of   

```Python
request = gen.coroutine(request)
```

`coroutine` wrapper function, also exception handle removed 
```Python
def _make_coroutine_wrapper(func, replace_callback):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        future = TracebackFuture()
        try:
            result = func(*args, **kwargs) # result is a generator if the function is a generator function
        except (Return, StopIteration) as e:
            result = getattr(e, 'value', None)
        else:
            if isinstance(result, types.GeneratorType): # if the function is a generator function
                try:
                    yielded = next(result) # generator.next() will run the code above and right hand of the generator, for our example request here, http.fetch(uri) will run and return yielded(a instance of Future).
                except (StopIteration, Return) as e:
                    future.set_result(getattr(e, 'value', None))
                else:
                    Runner(gen=result, result_future=future, first_yielded=yielded) # Runner is like the co lib in Js written by TJ, Runner use a While True rather than recursive, because recursive is slower in Python.
                return future
            else: # or the function is jsut a normal function
              pass 
        future.set_result(result)
        return future
    return wrapper
```
With the above code, we can learn that you pass a function with or without `yield` statement to the wrapper, if the function has `yield` statement in it's code, it will be a generator function.    
Invoke this function will return a `types.GeneratorType`.   

With the Tornado usage we can learn that the function after `yield` can be either a `coroutine` or a normal function.     
Both of them returns a `Future`. You can write `return Future` by yourself or use `@coroutine`. But make sure your normal function is an async function.  

`Runner.run` function, exception handle removed
```Python
def __init__(self, gen, result_future, first_yielded): # init of Runner
    ... # some attrs bind
    self.future = first_yielded # removed some complex logic, just show the normal logic of running the `request` generator.
    self.io_loop.add_future(
                self.future, lambda f: self.run()) # io_loop is a epoll based loop, the second function is a callback function when future is finished.

def run(self):
"""Starts or resumes the generator, running until it reaches a
yield point that is not ready.
"""
    while True:
        if not future.done():
            return
        try:
            value = future.result()
            yielded = self.gen.send(value)
        except (StopIteration, Return) as e:
            self.finished = True
            return
        except Exception:
            self.finished = True
            return
        if not self.handle_yield(yielded):
            return

```
Runner is like the `co` lib in Js written by TJ, Runner use a While True rather than recursive, because recursive is slower in Python.  Both of them do the same thing, that is executing the generator unitl it's done.
  
First of all, Runner add the future, or we can say the async function `fetch` to `io_loop`. If `fetch` is finish, itself will invoke the callback function `handle_response` to set data to `future`. And the `io_loop` will invoke another callback function `lambda f: self.run()` to run the function `run` to get the `result` from `future` by `value = future.result()` and `send` to the generator by `yield = gen.send(value)` and start the next block of the generator function if exists until the whole function is stoped and return a `StopIteration`.

So let us figure out the effect of each object:  
- generator function: a function with yield statement
- generator: invoke a generator function will return a generator
- coroutine: a wrapper function to wrapper a generator function. It will create a runner to run the generator.
- Future: used to collect and get result, it's a result container.
- Runner: it will register the future to `io_loop` and send result back to generator, and repeats unitl generator is done.


### JavaScript
TODO
