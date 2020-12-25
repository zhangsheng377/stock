import json
import logging
import sched
import threading
import time
from datetime import datetime

from db_sheets import db_sheets, db_redis
from policies import policies

VERSION = "0.0.1"

schdule = sched.scheduler(time.time, time.sleep)

stock_policy_locks = {}

stock_locks = {}


def get_today_tick_data(db_sheet):
    date_str = datetime.now().strftime("%Y-%m-%d")
    # date_str = '2020-12-25'
    regex_str = '^' + date_str
    data = db_sheet.find(filter={'_id': {"$regex": regex_str}}, sort=[('_id', 1)])
    return data


def func_stock(stock_id):
    with stock_locks[stock_id]:
        try:
            data = get_today_tick_data(db_sheets[stock_id])

            db_redis.set(stock_id, json.dumps(data))
        except Exception as e:
            logging.warning("save data error.", e)

        print(datetime.now())
        schdule.enter(1, 0, func_stock, (stock_id,))


def func_policy(stock_id, policy_name):
    with stock_policy_locks[stock_id][policy_name]:
        try:
            data = get_today_tick_data(db_sheets[stock_id])

            if len(data) > 0:
                result_list = policies[policy_name](data)
                db_redis.set(stock_id + '_' + policy_name, json.dumps(result_list))

        except Exception as e:
            logging.warning("save policy error.", e)

        print(datetime.now())
        schdule.enter(1, 0, func_policy, (stock_id, policy_name))


print(VERSION)
for (stock_id, _) in db_sheets.items():
    stock_locks[stock_id] = threading.Lock()
    schdule.enter(0, 0, func_stock, (stock_id,))

    stock_policy_locks[stock_id] = {}
    for (policy_name, policy_handle) in policies.items():
        stock_policy_locks[stock_id][policy_name] = threading.Lock()
        schdule.enter(0, 0, func_policy, (stock_id, policy_name))
schdule.run()