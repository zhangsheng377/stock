import logging
import os
import sys
import traceback

import pika

from UTILS import config_rabbitmq
from UTILS.config_port import rabbitmq_host, rabbitmq_port
from UTILS.config import LOGGING_LEVEL

logging.getLogger().setLevel(LOGGING_LEVEL)

polices_channel = 'stock_polices'
user_send_channel = 'stock_user_send'


class RabbitMqAgent(object):
    def __init__(self):
        self._host = rabbitmq_host  # broker IP
        self._port = rabbitmq_port  # broker port
        self._vhost = '/'  # vhost
        self._credentials = pika.PlainCredentials(config_rabbitmq.rabbitmq_user, config_rabbitmq.rabbitmq_password)
        self._connection = None

    def connect(self):
        try:
            # 连接RabbitMQ的参数对象
            parameter = pika.ConnectionParameters(host=self._host,
                                                  port=self._port,
                                                  virtual_host=self._vhost,
                                                  credentials=self._credentials,
                                                  heartbeat=10)
            self._connection = pika.BlockingConnection(parameter)  # 建立连接
        except Exception as e:
            traceback.print_exc()
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)

    def __enter__(self):
        self.connect()
        return self

    def put(self, message_str, queue_name, route_key, exchange=''):
        if self._connection is None:
            logging.error(f"put without connect!")
            return

        channel = self._connection.channel()  # 获取channel
        channel.queue_declare(queue=queue_name)  # 申明使用的queue

        #  调用basic_publish方法向RabbitMQ发送数据， 这个方法应该只支持str类型的数据
        channel.basic_publish(
            exchange=exchange,  # 指定exchange
            routing_key=route_key,  # 指定路由
            body=message_str  # 具体发送的数据
        )

    def start_consuming(self, queue_name, func_callback):
        if self._connection is None:
            logging.error(f"start_consuming without connect!")
            return
        channel = self._connection.channel()
        channel.queue_declare(queue=queue_name)

        # 调用basic_consume方法，可以传入一个回调函数
        channel.basic_consume(on_message_callback=func_callback,
                              queue=queue_name,
                              auto_ack=True)
        channel.start_consuming()  # 相当于run_forever(), 当Queue中没有数据，则一直阻塞等待

    def close(self):
        print("close")
        """关闭RabbitMQ的连接"""
        if self._connection is not None:
            self._connection.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    with RabbitMqAgent() as rabbitmq:
        rabbitmq.put(queue_name='hello', route_key='hello', message_str='Hello World!')
        print(" [x] Sent 'Hello World!'")


    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)


    try:
        with RabbitMqAgent() as rabbitmq:
            rabbitmq.start_consuming(queue_name='hello', func_callback=callback)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
