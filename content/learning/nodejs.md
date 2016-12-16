Title: 最近在做的事情
Tags: nodejs
Summary: 几个月没写博客了, 总结下最近做的事情

最近几个月没有写博客, 一方面是觉得之前博客总是在分享单一的知识点,没能沉淀出什么精华,在反思该如何写博客. 另一方面是玩起了`nodejs`后, 发现挺好玩的,也就一直花时间在代码上.  

一开始先是读了tj 大神的`co`库, 和 python 的实现对比后发现, 因为 node 自带事件驱动模型, 所以实现的非常简单.  之前写过两者的比较. 这个坑填了一半.得找时间填下.  

后来就开始用`co`做一个后台项目, 当然不是 web 项目, 本来也是可以用 python 做的, 但是这次想玩玩 node, 现在感觉还不错.  

先记录下一些我觉得还不错的库吧, 其他高深的暂时也没 get 到.

- dockernode-promise https://github.com/kamushin/dockerode-promise-es6 这个库是用 node 调用 docker 的..稍微有点 bug, 所以我给它提了个 pr, 所以先写在第一个. 
- tracer 这个是我在一堆 log 库里挑出感觉还不错的
- sequelize orm 库, 似乎大家都是用的这个.

- co-mocha 涉及到 co 的单测
- power-assert 一用就爱上的 assertion, 再也不用写 should 了
- growl 下面这两个主要是配合 mocha 提升测试时的体验的, 比如 watch 文件,然后把测试 report 用 message 的形式显示在桌面等等.
- intelli-espower-loader

用了一段时间 node, 感觉库比 python 丰富, 包管理也简单的多, 速度肯定是比 Python 快. 在es6语法的支持下, 语法糖也不算输 python 太多. 据说修饰器也快要有了.
