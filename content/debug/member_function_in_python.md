Title: Member functions in Python
Tags: Python
Summary: Pass a self.func as an argument is passing a function and a self object.
`self.func` is a operation that bind `self` to the function.
```Python

class A(object):
    def __init__(self):
        self.b = B()
        self.b.run(self.func)

    def func(self):
        print "callback"

class B(object):
    def run(self, cb):
        self.cb = cb
        self.cb()

import sys
foo = A()
print sys.getrefcount(foo) # output: 3
```

Here are 3 objects ref to `foo`: 
- `foo` as a local variable, 
- a ref in getrefcount
- a ref in `foo.b.cb`

It's more like `self.func` is `func.self = self`, bind `self` to the function.

