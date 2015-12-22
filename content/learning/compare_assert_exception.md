Title: Compare assert exception in should(JavaScript) and unittest(Python)
Tags: unittest
Summary: two different ways of assert exception.


### should
With `should`, exception is asserted like this:  

```javascript
it('should throw when n isnt Number', function () {
    (function () {
      main.fibonacci('abcd');
    }).should.throw('n should be a Number');
  });
```
This library adds an attribute `should` to  `Object`. The `should` attribute includes a bunch of assert functions. With this, you can do
`(5).should.above(3)`. It will be even harder in Python, because types defined in C cannot be monkeypatched.
The implement of `should.throw` is a simple `try/catch`.  

### unittest

With `assertRaises` in `unittest`, exception is asserted like this:
```Python
with self.assertRaisesRegexp(ValueError, 'literal'):
    int('XYZ')
```
It's much more simple than another way, because we don't need to pass test function as an argument to the assert function, no matter the argument called `this` lol.  
Exception is not catched by a `try/except` statement, but in `__exit__` context manager.

