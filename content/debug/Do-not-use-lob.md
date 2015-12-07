Title: Do not use LOB in Oracle(OLTP) -- record an optimization experience
Tags: Oracle, Python
Summary: LOB in Oracle and cx_Oracle 

## Front knowledge
### LOB in Oracle
LOB is used in Oracle to store text logger than 4000.    
We don't use Oracle in a OLTP system.   
Conside of RT and IO, we choose some other ways to provide log text. For example, CDN.

### LOB in cx_Oracle
As mentioned in [Some tricks when using cx_Oracle](http://kamushin.github.io/learning/python_oracle.html), we must convert LOB to string for each line we fetched.    
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
But it will bring out a significant cost of CPU time in Python, which you chould see later.

## Profile
I use `CProfile` to profile my Python code. It's very easy to use.
```
  import CProfile
  CProfile.run("unittest....")
```

This is part of my profile.
```
      ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      209391 1286.084  0.006 1286.559    0.006   DB.py:116(convert)
      4630   346.679   0.075  346.679    0.075   {method 'executemany' of 'cx_Oracle.Cursor' objects}
      4654   90.788    0.020   90.788    0.020   {method 'commit' of 'cx_Oracle.Connection' objects}
```

200k times call of `convert` cost 2000+ sec. Is't because Python `LOB=>str` is very slow.    
4k times of `commit` and `executemany` because of the lag between two servers.

