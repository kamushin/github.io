Title:  对 Paxos 的一些理解
Tags: Paxos
Summary: 0. prepare 阶段是干嘛的 1. 为什么比2pc 好 2. 什么时候持久化

今天 OB 的同事花了一个多小时讲了 paxos 的原理, 我相信场上听懂50%的人不超过50%. 至少我自己对 basic-paxos 还存在这几点疑问.

###  prepare 阶段是干嘛的

multi paxos 是不需要 prepare 的, 而 basic paxos 需要, 为什么多个leader 的时候需要做 prepare 呢?  
prepare 阶段是用来决定当前要进行 accept 的 proposal id 的.  拥有 prepare 阶段后的 accept 阶段可以保证很大概率下多数人可以接受它的请求. 
如果失去了 prepare 阶段, 并且有多个 leader 在同时提交, 很可能出现**大家都在做持久化,但是都是一群乌合之众,没有一个人是 majority**.
虽然有了 prepare 阶段后, 依然可能出现全是乌合之众的情况, 但是大大降低了.

从 paxos 的推演的角度, 我们来思考这个问题, paxos 需要满足以下三个原始条件

1. 决议（value）只有在被proposers提出后才能被批准（未经批准的决议称为“提案（proposal）”）；
2. 在一次Paxos算法的执行实例中，只批准（chosen）一个value；
3. learners只能获得被批准（chosen）的value。

 我们怎么保证只批准一个 value 呢? 那就是看哪个 value 是多数派,多数派的那个有效.
 为了形成多数派, 必然要有一方比另一方至少多1个, 而怎么保证这1个肯定出现,而不是摇摆不定呢?
 所以我们有了约束`p1:一个 acceptor 必须 accept 遇到的第一个提案`  
 继续考虑, 条件2其实只说了批准 value, 没说不能 accept 多个决议.
 所以我们有了约束`p2:一个 value 被 批准后, 之后批准的提案必须具有这个 value`
 p2进一步加强可以得到`p2a: 一个 value 被批准后, acceptor 只能接受具备这个 value 的提案`
 但是`p2a`不具备可操作性, 与p1矛盾了. 所以我们用 p2b 代替 `p2b: 一个 value 被批准后, proposal 只能提出具备这个 value 的提案`

 到这里,我突然想通了 prepare 阶段是干嘛的, prepare 阶段就是检查当前有没有已经 accept的提案的,如果已经有了 accept 的提案, 
 那么就不能提出了(如果 value 不同. 如果强行提出呢? 只不过是浪费带宽罢了

 但是故事还没完, p2b 的意思是, proposal 每提出决议,就要访问全部其他节点, 看有没有 value 被批准. 这可太麻烦了. 退化为2pc 了喂!
 所以有了非常拗口的`p2c: 如果一个编号为n的提案具有value v，那么存在一个多数派，要么他们中所有人都没有接受（accept）编号小于n 
 的任何提案，要么他们已经接受（accept）的所有编号小于n的提案中编号最大的那个提案具有value v。`

 从这里, 我们得到一个神奇的结论, paxos 是 2pc 的单调递增优化!




###  为什么比2pc 好

如果我们简单的把2pc 的 commit 条件设置为多数同意就 commit. 是不是就变得和 paxos 一样了呢?  
2pc 的 commit 条件设置为多数同意, 这就是 zookeeper 的 zab 算法. 它比 paxos 弱的一点是, 当一个 acceptor 在 prepare 阶段接受了一个提议后,
除非 rollback, 不然不能接受新的更大的提议, 也就是有个锁在上面. 而 paxos 协议是可以打破这把锁的. 打破锁的行为, 可以提高吞吐量和容错率. ( 这点不知道线上验证如何.


### 什么时候持久化

在 prepare 和 accept 后都需要持久化, 不过 accept 才是数据持久化.


### 待续

今天暂时想通了这么多, 明天继续和同事切磋去.
