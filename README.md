## redis

```
docker run -d --name redis -v /opt/docker/data/redis:/data -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro --restart always -p 6379 redis

redis-cli -h 127.0.0.1 -p 49153
```
