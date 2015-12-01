Title: Difference between ArrayList and Arrays.asList()
Tags: Java
Summary: ArrayList is resizeable-array, while Arrays.asList() is a "view" onto the primitives array so it's fixed-size array.

`Arrays.asList` does not return an `ArrayList` instance which has an `add` method implemented correctly.   
It returns a List that is a "view" onto the array - a wrapper that makes the array look like a list  
Changes to the returned list `write through` to the array  
Since the returned instance is a fixed-size array, the `add` method always throw an UnsupporedOperationException.  
If want to use `add` method  
```
  new ArrayList(Arrays.asList(myArray)); //copies the content of the array to a new ArrayList 
```


