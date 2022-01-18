import json
import logging

from UTILS.db_sheets import db_redis, get_stock_data
from UTILS.rabbitmq_utils import RabbitMqAgent, polices_channel, user_send_channel
from UTILS.time_utils import get_rest_seconds
from policies import policies
from UTILS.config import VERSION, LOGGING_LEVEL

logging.getLogger().setLevel(LOGGING_LEVEL)

stock_police_result_len_map = {}


def handle_police(ch, method, properties, body):
    logging.debug(f"{body}")
    try:
        json_body = json.loads(body)
        stock_id = json_body['stock_id']
        policy_name = json_body['policy_name']

        data = get_stock_data(stock_id)
        if len(data) <= 0:
            logging.warning(f"get_stock_data ken <= 0. len={len(data)}")
            return

        logging.debug(f"had data: {len(data)}")
        result_list = policies[policy_name](data)

        key = stock_id + '_' + policy_name
        old_result_len = stock_police_result_len_map.get(key, 0)
        if len(result_list) == old_result_len:
            logging.debug(f"len(result_list) == old_result_len. old_result_len={old_result_len}")
            return

        db_redis.set(key, json.dumps(result_list), ex=get_rest_seconds())
        stock_police_result_len_map[key] = len(result_list)
        with RabbitMqAgent() as rabbitmq:
            rabbitmq.put(queue_name=user_send_channel, route_key=user_send_channel,
                         message_str=json.dumps({'stock_id': stock_id, 'policy_name': policy_name}))

        logging.debug(f"old_result_len={old_result_len}, len(result_list)={len(result_list)}")

    except Exception:
        logging.warning("save policy error.", exc_info=True)


if __name__ == "__main__":
    logging.info(f"VERSION: {VERSION}")
    with RabbitMqAgent() as rabbitmq:
        rabbitmq.start_consuming(queue_name=polices_channel, func_callback=handle_police)
