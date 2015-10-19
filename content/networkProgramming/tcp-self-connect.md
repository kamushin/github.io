Title:TCP自连接
Tags:网络编程
Summary:TCP自连接特性

陈硕的第8节视频介绍了TCP自连接这个特性。

程序代码类似于:

    for i in range(65536):
        try:
            sock = socket.create_connection(('localhost', port))
            time.sleep(60*60)
        except:
            ...

这里主要是这样的一个逻辑:  

首先在循环中每次尝试创建连接的时候，TCP会分配一个IP给客户端，这个IP不是每次都随机的而是会自增。在最多尝试了65536或更少次后，一定会恰好和我们输入的port参数重合(如果port没有被占用)，那么就产生了一个客户端连接到自己的现象。要避免这个现象，可以在网络库中进行判断。
