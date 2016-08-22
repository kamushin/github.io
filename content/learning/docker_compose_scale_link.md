Title: docker-compose: scale and link
Tags: DevOps docker
Summary: Learned how to use docker compose to create a scalable web app with nginx.

Month ago, I built my apps with docker and used Nginx outside the docker as a reverse proxy server. Now I have something better to make a change.  
In docker's world, every component of a website should running as a container, include app, db, and Nginx as well.
A docker compose YAML I found online as follows, from [a blog](http://anandmanisankar.com/posts/docker-container-nginx-node-redis-example/):
``` yaml
nginx:
    build: ./nginx
    links:
        - node1:node1
        - node2:node2
        - node3:node3
    ports:
        - "80:80"
node1:
    build: ./node
    links:
        - redis
    ports:
        - "8080"
node2:
    build: ./node
    links:
        - redis
    ports:
        - "8080"
node3:
    build: ./node
    links:
        - redis
    ports:
        - "8080"
redis:
    image: redis
    ports:
        - "6379"
```
The author made 3 app containers, 1 redis container and 1 nginx container. I find some ugly implement here that each node is hard coded in conf file, so if nodes need to be scaled up, we should add more and more nodes in the conf file.  
`docker compose scale` is a useful command here to let us scale up our app containers elegantly. `docker compose scale node=3 nginx=1 redis=1` will automatically create 3 node containers for us.  
But there is another dark cloud on the sky. In the previous version, nginx config file is simply as follows:
``` nginx
worker_processes 4;

events { worker_connections 1024; }

http {

        upstream node-app {
              least_conn;
              server node1:8080 weight=10 max_fails=3 fail_timeout=30s;
              server node2:8080 weight=10 max_fails=3 fail_timeout=30s;
              server node3:8080 weight=10 max_fails=3 fail_timeout=30s;
        }
         
        server {
              listen 80;
         
              location / {
                proxy_pass http://node-app;
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection 'upgrade';
                proxy_set_header Host $host;
                proxy_cache_bypass $http_upgrade;
              }
        }
}

```
Can we use `node` to replace `node1`,`node2`,`node3` here?  
`node1` here is not some docker magic, it's just a hostname which docker generated in `/ets/hosts` of nginx container, since we linked `node1` to nginx.
So if we have 3 node IP which has the same hostname, we can just rewrite conf to a single server: 
```
        upstream node-app {
              least_conn;
              server node:8080 max_fails=3 fail_timeout=30s;
        }

```
Unfortunately, docker compose v1 seems not support group nodes into the same hostname.   
It will generate hosts as follows:
```

172.17.0.21 node 8a1297a5b3e4 compose_node_1
172.17.0.21 node_1 8a1297a5b3e4 compose_node_1
172.17.0.22 node_2 069dd46836aa compose_node_2

```
Only one container will get the name `node`. After searching in Github, I got some interesting facts:

The interaction of scaling with networking (as with links) is unsatisfactory at the moment - you'll basically get a bunch of entries in /etc/hosts along these lines:
```
  172.16.0.1 myapp_php_1
  172.16.0.2 myapp_php_2
  172.16.0.3 myapp_php_3
```
In a future version of Compose (enabled by changes to Engine), the name under which each container joins the network is going to change to just the service name, php. So you'll get multiple entries with the same name:
```
172.16.0.1 php
172.16.0.2 php
172.16.0.3 php
```
This isn't a real solution either, of course - we're still working towards one - but in both cases, if you have a load balancer container that needs to keep up-to-date with what's currently on the network, for the time being it'll need to periodically read /etc/hosts and parse the entries to determine the IPs of the backends.   

@aanand one of the maintainer of docker compose said above in [2015-12-7](https://github.com/docker/compose/issues/2472).  

It may already be improved in v2 with docker 1.10, but I have not get the chance to use docker 1.10.  

I think this way is better since we can easily scale up and dont need to change the config.  DevOps should evolve in this scalable way.
