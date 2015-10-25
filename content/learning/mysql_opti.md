Title: MySQL 优化学习之路
Tags: MySQL
Summary: 阅读MySQL文档, 总结优化经验
### Overview

#### DB Level
- table structure: column data type | table with few or many columns
- right indexs
- storage engine
- data format: compression or not
- locking strategy
- caching size
#### Hardware Level
- Disk seeks 10ms
- Disk reading and writing. easier to optimize than disk seeks
- CPU cycles large tables compared to the amount of memory ???
- Memory bandwith when CPU needs more data to fit in CPU cache ???

### SQL
- use explain
- indexs
- avoid full table scan
- analyze table periodically
- read-only transactions 5.6.4+ // had read an article on ATA about this
- avoid transforming query hard to read, optimizer will do this

#### SELECT
- cover index: In some cases, MySQL can read rows from the index without even consulting the data file. If all columns used from the index are numeric, only the index tree is used to resolve the query. // need numeric ? TODO
- range index
    - MySQL does not support merging ranges， use union
    - `eq_range_index_dive_limit` To permit use of index dives for comparisons of up to N equality ranges, set `eq_range_index_dive_limit` to N + 1
- index extensions: add pk after each secondary index  5.6.9
- two kinds of filesort
- group by: loose index scan vs tight index scan, depends on distribution of column(cardinality).

#### INSERT
- use INSERT statements with multiple VALUES lists to insert several rows at a time will be faster than using separate single-row INSERT statements.
- `bulk_insert_buffer_size` for large INSERT
- insert values explicitly only when the value to be inserted differs from the default.
- Bulk insert speed up (https://dev.mysql.com/doc/refman/5.6/en/optimizing-innodb-bulk-data-loading.html)

#### Update
- same with INSERT

#### DELETE
- truncate

#### Optimizing INFORMATION_SCHEMA Queries
- Try to use constant lookup values for database and table names in the WHERE clause
- Write queries that minimize the number of table files that must be opened (???)
- Use EXPLAIN to determine whether the server can use INFORMATION_SCHEMA optimizations for a query

### Index
Index can improve the speed of determining rows which match where statements. But useless indexs are waste of space and time for db to determinie whcih index to use and need more time to create indexs when insert.

#### How MySQL use index
- the most seletive indexs
- leftmost prefix of the index
- join: 
    - use same data type will be faster // varchar and char are the same if their size equal.
    - must use the same character set when compare string columns
    - comparison of dissimilar column may prevent use of indexs
- MIN() MAX() of column `key_col` will be O(1) if all `key_part_N` before `key_col` in where statement is constant.
- cover index // here not mention numeric

#### Primary Key
- use numeric pk

#### Foreign Key
- split low-frequently data into separate table

#### Column Key
- prefix index 
- fulltext for char varchar and text

#### Statistic 
- expr1 = expr2 is not true when expr1 or expr2 (or both) are NULL
    










