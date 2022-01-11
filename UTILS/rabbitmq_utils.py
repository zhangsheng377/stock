import pika

from UTILS import config_rabbitmq
from UTILS.config_port import rabbitmq_host, rabbitmq_port


class RabbitMqAgent(object):
    _credentials = pika.PlainCredentials(config_rabbitmq.rabbitmq_user, config_rabbitmq.rabbitmq_password)
    _parameters = pika.ConnectionParameters(host=rabbitmq_host,
                                            port=rabbitmq_port,
                                            virtual_host='/',
                                            heartbeat=10,
                                            credentials=_credentials)
    _connection = pika.BlockingConnection(_parameters)
    channel = _connection.channel()


polices_channel = 'stock_polices'
user_send_channel = 'stock_user_send'

if __name__ == "__main__":
    rabbitmq_channel = RabbitMqAgent.channel
    rabbitmq_channel.queue_declare(queue='hello')
    rabbitmq_channel.basic_publish(exchange='', routing_key='hello', body=bytes('Hello World!', encoding='utf-8'))
    print(" [x] Sent 'Hello World!'")
