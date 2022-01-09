import pika

from UTILS import config_rabbitmq


class RabbitMqAgent(object):
    _credentials = pika.PlainCredentials(config_rabbitmq.rabbitmq_user, config_rabbitmq.rabbitmq_password)
    _parameters = pika.ConnectionParameters(host='192.168.10.5',
                                            port=5672,
                                            virtual_host='/',
                                            credentials=_credentials)
    _connection = pika.BlockingConnection(_parameters)
    channel = _connection.channel()


polices_channel = 'stock_polices'
user_send_channel = 'stock_user_send'
