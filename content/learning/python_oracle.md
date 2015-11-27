Title: Some tricks when using cx_Oracle
Tags: Python
Summary: threading safe && clob

cx_Oracle is a Python module that enables access to Oracle databases.  
However, users may have confusion due to some fetures of this module.

#### Thread safe
The default setting of cx_Oracle is not thread-safe.    
So if user have multiple threads, make sure that specifying `threaded=True` when creating the connection.   

`conn = cx_Oracle.connect(user + '/' + passwd + "@" + host + "/" + db, threaded=True)`   

Otherwise, the program will crash with error message like    

`ORA-24550: signal received: [si_signo=11] [si_errno=0] [si_code=2] [si_addr=0000000000000000]`  


#### Fetch LOB column
> Internally, Oracle uses LOB locators which are allocated based on the cursor array size. Thus, it is important that the data in the LOB object be manipulated before another internal fetch takes place. The safest way to do this is to use the cursor as an iterator. In particular, do not use the fetchall() method. The exception “LOB variable no longer valid after subsequent fetch” will be raised if an attempt to access a LOB variable after a subsequent fetch is detected.

Use curosr as an iterator rather than use `fetchall()` method.

```
self._cursor.execute(sql, *args)
def fix_lob(row):
    def convert(col):
        if isinstance(col, cx_Oracle.LOB):
            return str(col)
        else:
            return col

    return [convert(c) for c in row]

return [fix_lob(r) for r in self._cursor]
```
