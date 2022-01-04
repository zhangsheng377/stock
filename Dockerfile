FROM ubuntu:latest
ENTRYPOINT []

# RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt clean && apt update && apt install git python3 python3-pip -y

COPY ta-lib-0.4.0-src.tar.gz ta-lib-0.4.0-src.tar.gz
RUN tar -zxvf ta-lib-0.4.0-src.tar.gz && cd /ta-lib && ./configure --prefix=/usr && make && make install

# RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install numpy pandas requests TA-Lib tabulate pymongo matplotlib qiniu redis tushare pika

RUN git clone https://github.com/zhangsheng377/stock.git --depth=1
ARG QINIU_ACCESS_KEY
ARG QINIU_SECRET_KEY
RUN echo "access_key = \"$QINIU_ACCESS_KEY\" \n\
secret_key = \"$QINIU_SECRET_KEY\" "\
> /stock/UTILS/config_qiniu.py

ARG RABBITMQ_USER
ARG RABBITMQ_PASSWORD
RUN echo "rabbitmq_user = \"$RABBITMQ_USER\" \n\
rabbitmq_password = \"$RABBITMQ_PASSWORD\" "\
> /stock/UTILS/config_rabbitmq.py

WORKDIR /stock

# ENTRYPOINT ["/stock/docker_cmd.sh"]
CMD ["/bin/bash", "docker_cmd.sh"]
