## redis

```
docker run -d --name redis -v /opt/docker/data/redis:/data -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro --restart always -p 6379:6379 redis

redis-cli -h 127.0.0.1 -p 6379
```

## mongo

```
docker run -d --name mongo -v /opt/docker/data/mongo:/data -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro --restart always -p 27017:27017 mongo

mongo 127.0.0.1:27017
show dbs
use tushare
db.sh_600196.insert({"test":"testdb"})

mongodump -h 127.0.0.1:27017 -d tushare -o /data/mongodump/tushare
mongorestore -h 127.0.0.1:27017 -d tushare --dir /data/mongodump/tushare
```

## save_tushare

```
docker build -t zhangsheng377/save_tushare -f Dockerfile_tushare .

docker run -ti -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro zhangsheng377/save_tushare

docker run -d --name save_tushare -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro --restart always zhangsheng377/save_tushare
```

## stock

```
docker build -t zhangsheng377/stock .

docker run -ti zhangsheng377/stock
docker run -ti zhangsheng377/stock /bin/bash
docker run -ti -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro zhangsheng377/stock

docker run -d --name stock -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro --restart always zhangsheng377/stock
```

## save_policies

```
docker build -t zhangsheng377/save_policies -f Dockerfile_policy .

docker run -ti -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro zhangsheng377/save_policies

docker run -d --name save_policies -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro --restart always zhangsheng377/save_policies
```

## 部署花生壳 phddns

```
docker build -t zhangsheng377/phddns -f Dockerfile_phddns .

docker run -ti -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro zhangsheng377/phddns  /bin/bash

docker run -d --name phddns -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro --restart always zhangsheng377/phddns
```

## 部署微信服务器

```
docker build -t zhangsheng377/server -f Dockerfile_server .

docker run -ti -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro zhangsheng377/server  /bin/bash

docker run -d --name server -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro -p 5000:5000 --restart always zhangsheng377/server
```
