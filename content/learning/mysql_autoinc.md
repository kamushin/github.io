Title: MySQL auto_increment 的坑
Tags: MySQL 
Summary: 这破玩意去年8月就出过故障，今年又出了，贴下去年8月我总结的东西吧，没有干货，完全是mysql文档对应的一些总结


### Auto-Increment
- 内存中有一个计数器auto-increment counter来记录行值。在服务器启动后的第一个sql进来的时候，这个计数器被初始化select max(col) from t for update.如果表是空的，就用1开始，这个值也是可以设定的。
- 如果在计数器被初始化前， SHOW TABLE STATUS，那么计数器会被初始化，这个语句所在的事务持有独占锁，直到事务结束。
- 插入的时候，如果值大于当前最大值+步长，那么counter也跟着跳变。
- 如果值是NULL或者0，那么会被置为最大值+步长 
- 如果值是负或者大于整数范围，未定义行为
- Auto-Increment Locking是表锁，但是在语句结束的时候释放，而不是事务结束。
- A server restart also cancels the effect of the AUTO_INCREMENT = N table option in CREATE TABLE and ALTER TABLE statements, which you can use with InnoDB tables to set the initial counter value or alter the current counter value.
- 因为是语句锁，所以rollback后，是会产生gap的
 
### Configurable InnoDB Auto-Increment Locking
表级锁可以保证顺序性，但是并发性能差。所以加入优化，如果当前insert数量可预测，而且也没用别的语句持有Auto-Increment Locking表锁，那么这个insert不会持有表锁，而是在语句结束的时候，持mutex来修改counter。

- `innodb_autoinc_lock_mode = 0` 全部用传统的表锁
- `innodb_autoinc_lock_mode = 1` 简单插入用mutex，但是如果当前已经有语句持有表锁，那简单插入也得等着了。对于语句级别的复制是安全的。
- `innodb_autoinc_lock_mode = 2`  所有语句都用mutex。会导致交叉增加。

对于这个参数的设定，考虑到主备同步，还要和主备复制的参数一起考虑
- 对于语句级别的复制，开 `innodb_autoinc_lock_mode=2` 会导致主备不一致。
- row级别的复制，则不要紧。 
- 对于mixed来说1，2模式下，计数器简单的增加插入数量，不管有多少是特殊值。

简单插入，simple insert指的是mysql可以自己判断出插入条数的sql，其他为bulk insert。  
故障就是因为开了1，一个insert select这种bulk insert，导致持有表锁。  
以上
