import pika

from UTILS import config_rabbitmq
from UTILS.config_port import rabbitmq_host, rabbitmq_port


class RabbitMqAgent(object):
    _credentials = pika.PlainCredentials(config_rabbitmq.rabbitmq_user, config_rabbitmq.rabbitmq_password)
    _parameters = pika.ConnectionParameters(host=rabbitmq_host,
                                            port=rabbitmq_port,
                                            virtual_host='/',
                                            heartbeat_interval=10,
                                            credentials=_credentials)
    _connection = pika.BlockingConnection(_parameters)
    channel = _connection.channel()


polices_channel = 'stock_polices'
user_send_channel = 'stock_user_send'
