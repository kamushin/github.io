Title: MySQL 首行查询陷阱
Tags: mysql 
Summary: 分析 MySQL 首行查询出现的条件和原理

### 起因

今天在执行一条 query 的时候,发现数据库用了6分钟才返回数据,而这条 query 仅仅是很简单的`select * from foo limit 1`.  

### 排查

foo 这个表里有近1T的数据, 但是这不应该成为返回慢的原因. 有同事发现这条语句只扫描了1行数据, 这是符合我们预期的, 但是为什么扫描一行数据花了6分钟呢?  
接下来我们发现此时数据库上io 压力非常大, 而且脏页比例很高. 问了下同事, 这个表最近在做历史数据迁移, 这时候真相就水落石出了.

### 原理

什么叫**脏页**? 在 Mysql 删除一条数据的时候, 并不是直接从数据文件中删除它, 而是先把它标记为 delete, 而后有异步的`purge`线程进行清理.而还没有被清理的数据所存在的页,
我们称之为脏页.  
在这个 case 中, 数据库先去数据文件中找1条记录,拿出来一看,发现这条记录是被标记 delete 的, 数据库又只能回去找下一条. 而当脏页比例很高且 io 压力很大的情况下,
要遍历找出第一条记录前, 很可能有大量的脏记录, 这就是为什么数据库花了6分钟才返回的原因.

### 解决
这个问题只有等数据库 purge 线程再工作一段时间,就会自动消失.
