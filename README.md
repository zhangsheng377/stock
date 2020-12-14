## redis

```
docker run -d --name redis -v /opt/docker/data/redis:/data -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro --restart always -p 6379 redis

redis-cli -h 127.0.0.1 -p 49153
```

## mongo

```
docker run -d --name mongo -v /opt/docker/data/mongo:/data -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro --restart always -p 27017 mongo

mongo 127.0.0.1:49155
show dbs
use tushare
db.sh_600196.insert({"test":"testdb"})
```

## build

```
docker build -t zhangsheng377/save_tushare -f Dockerfile_tushare .

docker run -ti -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro zhangsheng377/save_tushare
```
