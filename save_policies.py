import json
import logging

from UTILS.db_sheets import db_redis, get_stock_data
from UTILS.rabbitmq_utils import RabbitMqAgent, polices_channel, user_send_channel
from policies import policies
from UTILS.utils import VERSION, LOGGING_LEVEL

logging.getLogger().setLevel(LOGGING_LEVEL)


def handle_police(ch, method, properties, body):
    logging.info(f"{body}")
    try:
        json_body = json.loads(body)
        stock_id = json_body['stock_id']
        policy_name = json_body['policy_name']

        data = get_stock_data(stock_id)

        result_list = []
        if len(data) > 0:
            logging.info(f"had data: {len(data)}")
            result_list = policies[policy_name](data)
            with RabbitMqAgent() as rabbitmq:
                rabbitmq.put(queue_name=user_send_channel, route_key=user_send_channel,
                             message_str=json.dumps({'stock_id': stock_id, 'policy_name': policy_name}))
        db_redis.set(stock_id + '_' + policy_name, json.dumps(result_list))

    except Exception as e:
        logging.warning("save policy error.", e)


if __name__ == "__main__":
    logging.info(f"VERSION: {VERSION}")
    with RabbitMqAgent() as rabbitmq:
        rabbitmq.start_consuming(queue_name=polices_channel, func_callback=handle_police)
