Title:Pelican上增加评论和自动删除文章的一些坑
Tags:Pelican
###增加评论功能###

这个网上有很多描述，主要是去disqus注册下，然后设置下配置文件[example](http://querbalken.net/howto-setup-comments-with-disqus-in-pelican-en.html)坑主要在于Pelican的默认主题是没有disqus的模板的，所以虽然看到了对disqus的请求，却看不到评论区。需要自己下个比较全的主题。

###自动删除文件###

在content里删除了md文件，重新`make html`后在output中依然会看到那个md文件生成的html文件。

一个方法是加入配置`DELETE_OUTPUT_DIRECTORY = True`来每次清空output，但是这带来了两个问题:

- 自动日期没了 目前无法解决
- 版本控制没了，可以通过加入`OUTPUT_RETENTION = [".hg", ".git", ".bzr"]`来解决
