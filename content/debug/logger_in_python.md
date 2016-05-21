Title: Loggers in Python
Tags: Python
Summary: 1. Loggers will be stored in manager in Python. Handlers will cause resource leak if not removed.
2. Loggers will send to stderr by default. So make sure stderr has a receiver.


### Logger manager
Loggers will be stored in manager in Python. Handlers will cause resource leak if not removed.


``` Python
def getLogger(name=None):
    """
    Return a logger with the specified name, creating it if necessary.

    If no name is specified, return the root logger.
    """
    if name:
        return Logger.manager.getLogger(name)
    else:
        return root

class Manager(object):
    def getLogger(self, name):
        """
        Get a logger with the specified name (channel name), creating it
        if it doesn't yet exist. This name is a dot-separated hierarchical
        name, such as "a", "a.b", "a.b.c" or similar.

        If a PlaceHolder existed for the specified name [i.e. the logger
        didn't exist but a child of it did], replace it with the created
        logger and fix up the parent/child references which pointed to the
        placeholder to now point to the logger.
        """
        rv = None
        if not isinstance(name, basestring):
            raise TypeError('A logger name must be string or Unicode')
        if isinstance(name, unicode):
            name = name.encode('utf-8')
        _acquireLock()
        try:
            if name in self.loggerDict:
                rv = self.loggerDict[name]
                if isinstance(rv, PlaceHolder):
                    ph = rv
                    rv = (self.loggerClass or _loggerClass)(name)
                    rv.manager = self
                    self.loggerDict[name] = rv
                    self._fixupChildren(ph, rv)
                    self._fixupParents(rv)
            else:
                rv = (self.loggerClass or _loggerClass)(name)
                rv.manager = self
                self.loggerDict[name] = rv
                self._fixupParents(rv)
        finally:
            _releaseLock()
        return rv
```
`Loggers` in Python are stored in `Logger.manager` with a specified name. If create a logger with a task rather than a file, loggers stored in manager will increase and never be deleted.  
It becomes even worse when the logger has a handler, eg. write logs to database. It may cause a connections leak.

#### Log emit will hang if stderr is not received

Log info will send to stderr by default, make sure stderr buffer has a removed, otherwise stream write will be blocked.

