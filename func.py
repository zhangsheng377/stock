import json
import logging
import sched
import threading
import time
from datetime import datetime

from UTILS.utils import send_result
from db_sheets import db_redis, get_db_sheet
from  save_tushare import add_stock

VERSION = "0.0.11"

schdule = sched.scheduler(time.time, time.sleep)

user_stock_locks = {}
user_stock_events = {}

users = {}


def func(user_name, stock_id, old_result_len):
    with user_stock_locks[user_name][stock_id]:
        try:
            now_hour = int(datetime.now().strftime('%H'))
            if 8 <= now_hour <= 16:
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
        user_stock_events[user_name][stock_id] = schdule.enter(1, 0, func, (user_name, stock_id, old_result_len))


def get_stock_data(stock_id):
    data = db_redis.get(stock_id)
    if data is None:
        data = '[]'
    return json.loads(data)


def get_policy_data(stock_id, policy_name):
    data = db_redis.get(stock_id + '_' + policy_name)
    if data is None:
        data = '[]'
    return json.loads(data)


def send_one(user, stock_id):
    print(user, stock_id)
    data = get_stock_data(stock_id)
    result_list = []
    for policy_name in user['policies']:
        result_list.extend(get_policy_data(stock_id, policy_name))
    return send_result(stock_id, data, result_list, user['ftqq_token'], 0)


def discover_user():
    try:
        for (user_name, user_data) in users.items():
            if user_name not in user_stock_locks:
                user_stock_locks[user_name] = {}
            if user_name not in user_stock_events:
                user_stock_events[user_name] = {}

            for stock_id in user_data['stocks']:
                if stock_id not in user_stock_locks[user_name]:
                    user_stock_locks[user_name][stock_id] = threading.Lock()
                    user_stock_events[user_name][stock_id] = schdule.enter(0, 0, func, (user_name, stock_id, 0))
                    add_stock(stock_id, None)
                    print("discover_user add {} {}".format(user_name, stock_id))

            while True:
                is_change = False
                for stock_id in user_stock_events[user_name].keys():
                    if stock_id not in user_data['stocks']:
                        schdule.cancel(user_stock_events[user_name][stock_id])
                        user_stock_events[user_name].pop(stock_id)
                        user_stock_locks[user_name].pop(stock_id)
                        is_change = True
                        print("discover_user cancel {} {}".format(user_name, stock_id))
                        break
                if not is_change:
                    break
    except Exception as e:
        logging.warning("discover_stock error.", e)
    schdule.enter(10, 0, discover_user, )


def update_user():
    try:
        user_db_sheet = get_db_sheet(database_name="user", sheet_name="user")
        for user in user_db_sheet.find():
            users[user['_id']] = user
    except Exception as e:
        logging.warning("update_user error.", e)
    schdule.enter(10, 0, update_user, )


if __name__ == "__main__":
    print(VERSION)
    schdule.enter(0, 0, update_user, )
    schdule.enter(1, 0, discover_user, )
    schdule.run()
