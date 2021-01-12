import json
import logging
import sched
import threading
import time
from datetime import datetime

from UTILS.utils import send_result
from db_sheets import db_redis

VERSION = "0.0.10"

schdule = sched.scheduler(time.time, time.sleep)

user_stock_locks = {}

users = json.loads(db_redis.get('users'))


def func(user_name, stock_id, old_result_len):
    with user_stock_locks[user_name][stock_id]:
        try:
            data = get_stock_data(stock_id)

            result_list = []
            for policy_name in users[user_name]['policies']:
                result_list.extend(get_policy_data(stock_id, policy_name))

            old_result_len = send_result(stock_id, data, result_list, users[user_name]['ftqq_token'], old_result_len)
        except Exception as e:
            if e.args[0] == 'data_df is empty':
                logging.info("data_df is empty.")
            else:
                logging.warning("handle data error.", e)

        print(datetime.now())
        schdule.enter(1, 0, func, (user_name, stock_id, old_result_len))


def get_stock_data(stock_id):
    return json.loads(db_redis.get(stock_id))


def get_policy_data(stock_id, policy_name):
    return json.loads(db_redis.get(stock_id + '_' + policy_name))


def send_one(user_name, stock_id):
    data = get_stock_data(stock_id)
    result_list = []
    for policy_name in users[user_name]['policies']:
        result_list.extend(get_policy_data(stock_id, policy_name))
    return send_result(stock_id, data, result_list, users[user_name]['ftqq_token'], 0)


if __name__ == "__main__":
    print(VERSION)
    for (user_name, user_data) in users.items():
        user_stock_locks[user_name] = {}
        for stock_id in user_data['stocks']:
            user_stock_locks[user_name][stock_id] = threading.Lock()
            schdule.enter(0, 0, func, (user_name, stock_id, 0))
    schdule.run()
