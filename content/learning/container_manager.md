Title: Docker容器管理
Tags: docker
Summary: 这段时间会尝试多种容器管理方式。

在去年10月开始使用了一阵docker后，我逐渐开始了解docker的管理工具。目前了解到的docker管理工具，从简单到复杂，分别是`docker-compose`,`swarm`,`k8s`.  
其中最简单的，我在今年的四月份开始使用了，因为我目前并没有集群管理的需求，只是想要加速开发部署节奏，构建我的微服务应用, 所以`docker-compose`满足了我的需求。
目前我把一些web应用，数据分析，数据抓取程序以及nginx，一起放在了`docker-compose`配置里，当我希望整套服务换一个物理机器的时候，只需要重新执行`docker-compose`的命令，虽然还是比较原始的
容器使用方式，但是既满足了我的需求，也做到了**按docker的方式做事**, 呃 , 我是说把nginx放在docker里这件事情。  
最近我又希望往前走一小步，使用下`swarm`，我选择了一个简单的Python构建的Web-UI, `shipyard`.  它会和主机的8080端口做映射，然后提供一个web服务。由于我的nginx已经被`docker-compose`管理了，所以我
只能暂时让nginx把`shipyard`指向`192.168.5.1`的宿主机地址。TODO



