FROM ubuntu:latest
ENTRYPOINT []

# RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt clean && apt update && apt install git python3 python3-pip -y

COPY ta-lib-0.4.0-src.tar.gz ta-lib-0.4.0-src.tar.gz
RUN tar -zxvf ta-lib-0.4.0-src.tar.gz && cd /ta-lib && ./configure --prefix=/usr && make && make install

# RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install numpy pandas requests TA-Lib tabulate pymongo matplotlib qiniu redis tushare

RUN git clone https://github.com/zhangsheng377/stock.git
ARG QINIU_ACCESS_KEY
ARG QINIU_SECRET_KEY
RUN echo "from db_sheets import db_redis\n\
access_key = \"$QINIU_ACCESS_KEY\" \n\
secret_key = \"$QINIU_SECRET_KEY\" \n\
db_redis.set(\"qiniu_access_key\", access_key)\n\
db_redis.set(\"qiniu_secret_key\", secret_key)"
RUN echo "from db_sheets import db_redis\n\
access_key = \"$QINIU_ACCESS_KEY\" \n\
secret_key = \"$QINIU_SECRET_KEY\" \n\
db_redis.set(\"qiniu_access_key\", access_key)\n\
db_redis.set(\"qiniu_secret_key\", secret_key)"\
> /stock/UTILS/config_qiniu.py

WORKDIR /stock

# ENTRYPOINT ["/stock/docker_cmd.sh"]
CMD ["/bin/bash", "docker_cmd.sh"]
