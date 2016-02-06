Title: notes of ArchitectureOfDatabaseSystem
Tags: reading
Summary: reading notes of ArchitectureOfDatabaseSystem

> A Lightweight Thread Package is an application-level construct
that supports multiple threads within a single OS
process  -- page 150
Each DBMS thread is
programmed to manage its own state, to perform all potentially blocking
operations (e.g., I/Os) via non-blocking, asynchronous interfaces,
and to frequently yield control to a scheduling routine that dispatches
among these tasks.
Lightweight threads are an old idea that is discussed in a retrospective
sense in [49], and are widely used in event-loop programming
for user interfaces. The concept has been revisited frequently in the
recent OS literature [31, 48, 93, 94]. This architecture provides fast
task-switching and ease of porting, at the expense of replicating a good
deal of OS logic in the DBMS (task-switching, thread state management,
scheduling, etc.) [86]. --page 160

这就是在说 coroutine, 之前并不知道数据库里也有 co 的应用。
不过现在想想数据库这种 io 密集的应用，确实应该是 co 的第一个吃螃蟹的人。
co 应用必须使用 non-block io 是众所周知的，而像 innodb 这样完全使用direct io 的应用似乎正好
非常契合，因为至少在 Linux 上 aio 还是不支持buffer io 的。不过 MySQL 是用了内核线程的，大概是它比较新的缘故。  
不过有意思的是，事情的发展往往是三十年河东三十年河西的，文章中提到其实 co 的概念是非常古老的，甚至在1990年的时候，
因为没有足够好的操作系统级别的线程，大家转而使用了 co。 而在内核线程如此成熟的今天，在学习的时候，线程模型首先进入
了我们的视角，
不过现代数据库只有MSSQLServer 提供 co 的支持，而且不是默认选项, 默认的是线程池。 co 这玩意在MS那里叫 Fibers。 话说回来，响马也
做了个 fibjs，应该是向这个名字致敬的。

>From the simplest to the most complex, these are: (1) process
per DBMS worker, (2) thread per DBMS worker, and (3) process pool.
Although these models are simplified, all three are in use by commercial
DBMS systems today. -- page 152

这和以前接触到的 http 服务器的演化似乎是一样的，不过 http 服务器早就走进了 epoll 的时代，当然
也有人说 nginx 的强大中其实 epoll 只是做了一点点微小的贡献，不知道现代的数据库的模型是怎么样的了。
进程模型的好处是把很多事情扔给 os 去处理了，缺点就是内存开销大。
线程模型相对麻烦的一点就是要管理 race condition, 这点和应用开发无区别, 上古时期可能线程开发还有不好 debug 的问题。
从现代的操作系统来看，进程和线程的区别已经越来越小了。

>Client communication buffers: SQL is typically used in a “pull” model:
clients consume result tuples from a query cursor by repeatedly issuing
the SQL FETCH request, which retrieve one or more tuples per request.
Most DBMSs try to work ahead of the stream of FETCH requests to
enqueue results in advance of client requests.
In order to support this prefetching behavior, the DBMS worker
may use the client communications socket as a queue for the tuples
it produces. More complex approaches implement client-side cursor
caching and use the DBMS client to store results likely to be fetched
in the near future rather than relying on the OS communications
buffers. -- page 158
A relational query processor takes a declarative SQL statement,
validates it, optimizes it into a procedural dataflow execution plan,
and (subject to admission control) executes that dataflow program on
behalf of a client program. The client program then fetches (“pulls”) the
result tuples, typically one at a time or in small batches -- page 176

这里其实就是 client side cursor 和 server side cursor中我曾经误解过的地方，相信很多人也曾误解过。
结果集的发送其实不是个 push 的模型，而是个 pull 的模型，只有客户端在 fetch 的时候，服务器才会把数据发送过去，
而之所以在 fetch one row 的时候，后面的 row 也存储到客户端了，其实是数据库对于这种 prefetching 行为作出的优化，
先把所有数据都发送过来，存在客户端。这也导致了 fetch 大量数据时客户端内存的爆炸。这里可以联动http://kamushin.github.io/debug/sscursor_in_mysql.html

>Non-Uniform Memory Access (NUMA) systems provide a sharedmemory
programming model over a cluster of systems with independent
memories. Each system in the cluster can access its own local memory
quickly, whereas remote memory access across the high-speed cluster
interconnect is somewhat delayed. The architecture name comes from
this non-uniformity of memory access times.

NUMA架构好像在应用服务器那里还听说过，但是用在数据库这里估计比较难，内存的访问是个大问题。


>The Halloween problem arises from a
particular execution strategy for statements like “give everyone whose
salary is under $20K a 10% raise.” A na¨ıve plan for this query pipelines
an index scan iterator over the Emp.salary field into an update iterator
(the left-hand side of Figure 4.3). The pipelining provides good I/O)
locality, because it modifies tuples just after they are fetched from the
B+-tree. This pipelining, however, can also result in the index scan
“rediscovering” a previously modified tuple that moved rightward in
the tree after modification, leading to multiple raises for each employee.
In our example, all low-paid employees will receive repeated raises until
they earn more than $20K. This is not the intention of the statement --page 192

这个问题就是怎么解决已经更新过的值被再次更新。因为数据是以 B+ 树存储的，
意味着数据被改变后，它存放的位置是变了的，那么依次往后找，可能又找到了它。
解决的方式有两个，要么是 mvcc 下不让一个 sql 语句看到它自己导致的改变。要么用临时表来
先找出所有要改变的行，然后一起做改变。

>All DBMSs need some way to “point” to rows in a base table, so that
index entries can reference the rows appropriately. In many DBMSs,
this is implemented by using direct row IDs (RIDs) that are the physical
disk addresses of the rows in the base tables. This has the advantage
of being fast, but has the downside of making base table row movement
very expensive since all secondary indexes that point to this row require
updating. Both finding and updating these rows can be costly. Rows
need to move when an update changes the row size and space is unavailable
on the current page for the freshly updated row. And many rows
need to move when a B+-tree is split. -- page 195 
DB2 uses a forwarding pointer
to avoid the first problem. This requires a second I/O to find a moved
page, but avoids having to update the secondary index --page 195 

用 rowid 来表示存储在数据表中的位置，带来两个问题。第一个问题，数据位置改变后
rowid 就需要改变，那么所有的二级索引都要变，因为二级索引都必须持有这个 rowid 来找到数据。
第二个问题就是在更新时因为 b+树的分裂，很多行都需要改变位置.  
在我看到这个问题的时候，我第一反应是其实没必要改变所有的二级索引，如果二级索引持有rowid 的指针而不是 rowid 的值，那么只要改变 rowid 的值就行了。
Oracle的做法是不在二级索引中加rowid，而是加主键，然后去查一个主键-rowid的 map。不过这个也会带来一个查表的开销。

>In order to reduce locking and lock conflicts some DBMSs support
MVCC or OCC, typically as an add-on to 2PL. --page 221

这里我觉得是数据库技术的精髓所在。即让多个事务同时进行的同时，让结果看上去就像他们是串行的执行一样。  
这里我只了解 innodb。 在 rr 级别下，会用 mvcc 做隔离，在 rc 级别下会用乐观锁的 double-check 方案做隔离。
而 mvcc 并不是不加锁了，mvcc 只能让读不受到写锁的影响，而写操作还是要加锁的, 这点上 pg 好像写都没锁了，有空去看看。
double-check 就是先做操作，然后检查在事务执行期间，有没有别的事务改动过值，如果有就需要回滚重做了。
rc 模式下会产生幻读的问题，主要指的是 `select for update` 这样的问题。 在第一次`select` 的时候，读了 x 条
记录，然后乐观锁检查的时候发现这x 条记录没被改动过，就提交了。这里有个问题，就是如果`select`的`where` 语句是 range 的，
那么很可能有别的事物在这之后插入了一条记录，造成前一个事务的`select` 和`update` 的记录数不相等。  
RR的要求笼统点说就是要求同一事务中两次读得到的结果要是一样的。不会因为另一个事物的提交，而产生新的结果，这里不仅包括了值一样，行数也要一样，所以要解决幻读问题。
那么对于简单的select来说，只要通过MVCC读快照的模式就可以保证两次读结果一致。通过比较版本号，永远读取版本号早于事物开始时系统版本号的快照。
但是对于update、delete来说，难道我们要去update一个快照吗？这并没有什么意义。所以我们需要对记录上X锁。然后在遇到update一个范围或者是非唯一索引、无索引的时候（也就是目标可能不止一个），需要用gap锁，把所有目标可能出现的地方都锁住，也防
止新的符合目标的记录插入。 所以说其实MVCC解决了快照读的问题，而gap lock解决的是当前读的问题。
next key lock 就是记录锁加 gap lock, 主要就是解幻读。

>Latches differ from locks in a number of ways --page 223 

latch 其实就是编程意义上的一些锁，存在于内存中，比如自旋锁，互斥锁，rcu 锁等等, 其中 rcu 锁挺有那么点 mvcc 的意思。lock 就是数据库层面上为了做隔离而实现的锁，一般会持有的时间比
latch 要长，也会存下来，而不仅仅是内存中的一个变量。

>Database logging is an extremely complex and detail-oriented topic --page 228 

Can't agree more! 数据库中的日志简直复杂，不仅种类多，而且各种数据库的实现思路也不同。
不过总体来说，数据库里日志主要做三件事情，保障事务的持久化，回滚事务以保障原子性，还有就是故障恢复。
所以日志可以看做是一切状态改变的证明，所以在一个分布式数据库中最重要的就是保证日志的一致，因为日志就是状态，
没落成日志的东西，都是可以扔掉的。
基本的实现技术就是日志先行,WAL.  

- 在刷数据页前先刷日志
- 日志需要是有序的
- 事务提交前先刷日志

以上是 WAL 的三个规则。
第一条规则保证了原子性，也就是可回滚。第二第三个规则保证了故障后可恢复。
这些知识是我本来就知道的， 接下来是这篇文章告诉我的，real world.

>In order to maximize the speed of the fast path, most commercial
database systems operate in a mode that Haerder and Reuter call
“DIRECT, STEAL/NOT-FORCE” [34]: (a) data objects are updated
in place, (b) unpinned buffer pool frames can be “stolen” (and the modified
data pages written back to disk) even if they contain uncommitted
data, and (c) buffer pool pages need not be “forced” (flushed) to the
database before a commit request returns to the user -- page 229 
Another fast-path challenge in logging is to keep log records as small
as possible, in order to increase the throughput of log I/O activity.
A natural optimization is to log logical operations (e.g., “insert (Bob,
$25000) into EMP”) rather than physical operations (e.g., the afterimages
for all byte ranges modified via the tuple insertion, including
bytes on both heap file and index blocks.)  -- page 229
Rather than starting from the very first log
record, a correct result will be obtained by starting recovery at the
oldest of these two log records: (1) the log record describing the earliest
change to the oldest dirty page in the buffer pool, and (2) the log
record representing the start of the oldest transaction in the system.
The sequence number of this point is called the recovery log sequence
number (recovery LSN).) -- page 230

第一个就是说放弃一致性去保证性能。MySQL里等于把双1给去了。  
第二个就是说记录逻辑日志而不是物理日志。
逻辑日志的有点是快和小，缺点是用来做 undo/redo 会比较麻烦。所以 
MySQL 里 binlog 也就是用来复制的 log，是逻辑日志。而 redo/transaction log 是物理日志。  
第三个是在说 LSN，也就是 crash 的最优恢复点。这块我不太了解。

> Latching in B+-Trees --page 232 

这部分没怎么看懂，甚至我怀疑这里 latch 是不是写错了，应该是 lock。好吧，不过勾起了我一点回忆，就是 
以前看过的哪本书里有关于索引锁的优化的介绍。

>One manifestation of the relationship between concurrency and recovery is that writeahead
logging makes implicit assumptions about the locking protocol.
Write-ahead logging requires strict two-phase locking, and will not
operate correctly with non-strict two-phase locking --page236

真正有意思的来了，我看了很多书，原子性，隔离性都讲的很多，但是当原子性遇到隔离性呢？
如果要做到 WAL，那么在回滚事务的时候，可能存在一种情况是把已经修改的内容给修改回去。这就要求事务必须是
严格两阶段锁的。在一个非严格的状态下，一旦一个 x 锁被释放了，在同一事务内，是不可以再吃得到这个 x 锁去回滚数据的。
所以WAL的隐含前提就是，严格两阶段锁的。这段挺精彩的。

>Perhaps the most noticeable changes in this space are
due to the rapidly dropping price of RAM.

数据库技术和相关论文在现在看来已经是非常成熟了，唯一值得注意的区别就是内存白菜价了。所以带来了这么多内存数据库嘛~

>As should be clear from this paper, modern commercial database systems
are grounded both in academic research and in the experiences
of developing industrial-strength products for high-end customers. The
task of writing and maintaining a high-performance, fully functional
relational DBMS from scratch is an enormous investment in time and
energy. Many of the lessons of relational DBMSs, however, translate
over to new domains. Web services, network-attached storage, text and
e-mail repositories, notification services, and network monitors can all
benefit from DBMS research and experience. Data-intensive services
are at the core of computing today, and knowledge of database system
design is a skill that is broadly applicable, both inside and outside the
halls of the main database shops. These new directions raise a number
of research problems in database management as well, and point the
way to new interactions between the database community and other
areas of computing.

这段是结语，没啥好说的，直接贴上来。  
文章原文来自http://120.52.72.51/perspectives.mvdirona.com/c3pr90ntcsf0/content/binary/ArchitectureOfDatabaseSystem.pdf  
看完后给我感觉是第6章值得一看，前1-3章的话说实话和数据库没太大关系，是个操作系统上的涉及 cpu 和 io 的应用都会涉及。
第4章讲 query 的，这部分其实是编译原理的知识，和数据库关系不大。第5章没什么干货。
第6章是真正数据库相关的内容，概括的比较全面，比『数据库系统基础 高级篇』要实践一点，比『MySQL技术内幕innodb存储引擎 』要理论一点。
