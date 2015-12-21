try:
    db.connect()
    getfilelock()
    do_sth()
except:
    ...
finally:
    releasefilelock()
    db.close()

