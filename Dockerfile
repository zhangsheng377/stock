FROM ubuntu:latest
ENTRYPOINT []

RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt clean && apt update && apt install git python3 python3-pip -y

COPY ta-lib-0.4.0-src.tar.gz ta-lib-0.4.0-src.tar.gz
RUN tar -zxvf ta-lib-0.4.0-src.tar.gz && cd /ta-lib && ./configure --prefix=/usr && make && make install

RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install numpy pandas requests TA-Lib tabulate pymongo matplotlib qiniu

RUN git clone https://github.com/zhangsheng377/stock.git
COPY ftqq_tokens.py /stock/ftqq_tokens.py
COPY UTILS/config_qiniu.py /stock/UTILS/config_qiniu.py

WORKDIR /stock

# ENTRYPOINT ["/stock/docker_cmd.sh"]
CMD ["/bin/bash", "docker_cmd.sh"]

# docker build -t zhangsheng377/stock .
# docker run -ti zhangsheng377/stock
# docker run -ti zhangsheng377/stock /bin/bash
# docker run -ti -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro zhangsheng377/stock
# docker run -d -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro --restart always zhangsheng377/stock