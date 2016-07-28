Title: 搭建一个jupyter站点做数据分析吧
Tags: jupyter
Summary: 关于一个在nginx后的jupyter站点的小日记.

### jupyter

`jupyter` 是一个非常适合做数据分析的工作台。为了可以使得`jupyter`可以运行在服务器上访问生产环境的数据，今天我要在服务器上搭建一个`jupyter`站点。

### 容器

为了不和线上的其他应用起冲突，我决定把它装在一个docker中。
这里没有踩到什么坑。

### Nginx

为了提供可靠的域名转发服务，我会用Nginx根据域名转发到docker上绑定的Port。  
这里有个细节需要注意，因为`jupyter`用到了`websocket`技术，所以在nginx的配置上略有不同。
```
        location ~* /(api/kernels/[^/]+/(channels|iopub|shell|stdin)|terminals/websocket)/? {
            proxy_pass http://127.0.0.1:8003;

            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

        }

        # 对于满足以上格式的请求，是一个ws请求，需要加上最后3行。
        # 另外，至少需要 nginx 1.1.4
```

### 安全

我们当然不能让谁都能访问我们的工作台啦，果断加上密码 参考http://jupyter-notebook.readthedocs.io/en/latest/public_server.html


### 愉快的开始数据分析吧

装上`pandas`, `matplotlib` 愉快的开始数据分析吧。
