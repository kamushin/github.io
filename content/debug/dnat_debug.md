Title: 记一次网络问题的排查
Tags: network
Summary: 理一下排查网络问题时的思路

昨天遇到了一个端口转发导致VIP失效的问题，今天记录下当时的排查思路。  

因为要做升级，所以我删除了dokcer老容器，并启动新容器。之后访问VIP, 也就是LVS中的VIP，发现原先可以访问的站点不能访问了。  

以上是故障表现，下面是具体排查过程  

- `docker logs containerId ` 检查docker 中的应用是成功启动的，排除应用无法启动的问题
- `curl localhost:80` 因为容器是以`-p 80:80`的方式启动的，所以接下来我尝试在物理机上访问自己的80端口，发现可以成功访问应用，排除了`forward`没设置的问题
- 接下来，我祭出了瑞士军刀`nc -l 80`, 然后在外部以VIP的方式访问，发现无法访问。 这时候怀疑是 `iptables` 的问题
- 先做下备份，`service iptables save`, 然后关掉`service iptables stop`
- 再起`nc -l 80`, 发现很快nc进程就结束了，`trace nc -l 80` 找出来源包IP，发现是`LVS`的心跳包。至此VIP恢复访问
- 接下来就是要找iptables里谁在搞鬼了。`iptables -L`, 因为怀疑是docker在搞鬼，所以把展示出和docker有关的都删了，但是问题没有解决
- 上面我犯了一个错误，那就是以为`iptables -L`展示的是所有的规则，但其实只展示了`filter`, 和转发有关的nat需要`iptables -t nat -L`来展示
- 把`iptables -t nat -L`中和docker有关的删掉。问题解决。问题原因是docker删除容器后没有把转发规则删除。
- 又重现了下这个问题，应该是docker的问题，删除实例没有把转发规则和proxy干掉。

这次排查，用到了几个工具，都是之前的积累，所以排查显得顺畅多了。主要时间花在了对iptables的不熟悉。
