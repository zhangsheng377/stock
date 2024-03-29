import json
import logging

import requests

from UTILS.config_port import user_send_host, user_send_port
from UTILS.db_sheets import get_users
from UTILS.rabbitmq_utils import RabbitMqAgent, user_send_channel
from UTILS.config import VERSION, LOGGING_LEVEL

logging.getLogger().setLevel(LOGGING_LEVEL)

user_result_len_map = {}


def handle_user_send(ch, method, properties, body):
    logging.info(f"{body}")
    try:
        json_body = json.loads(body)
        stock_id = json_body['stock_id']
        policy_name = json_body['policy_name']

        users = get_users()
        for user in users:
            if stock_id not in user['stocks']:
                continue
            if policy_name not in user['policies']:
                continue

            key = user['_id'] + '_' + stock_id
            old_result_len = user_result_len_map.get(key, 0)

            url = f'http://{user_send_host}:{user_send_port}/send_user'
            data = {'user_id': json.dumps(user['_id']), 'stock_id': json.dumps(stock_id),
                    'old_result_len': json.dumps(old_result_len)}  # 将携带的参数传给params
            re_len = requests.get(url, params=data).json()
            logging.info(f"old_result_len:{old_result_len} re_len:{re_len}")
            user_result_len_map[key] = re_len

    except Exception:
        logging.warning("save policy error.", exc_info=True)


if __name__ == "__main__":
    logging.info(f"VERSION: {VERSION}")
    # print(json.dumps({'stock_id': '688180', 'policy_name': 'magic_nine_turns'}))
    with RabbitMqAgent() as rabbitmq:
        rabbitmq.start_consuming(queue_name=user_send_channel, func_callback=handle_user_send)
