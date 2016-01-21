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
a = A()
print sys.getrefcount(a)



