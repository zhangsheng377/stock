import json
import logging
import sched
import threading
import time
from datetime import datetime

from UTILS.db_sheets import db_redis, get_stock_data
from policies import policies

VERSION = "0.0.4"

schdule = sched.scheduler(time.time, time.sleep)

stock_policy_locks = {}


def func_policy(stock_id, policy_name):
    with stock_policy_locks[stock_id][policy_name]:
        try:
            now_hour = int(datetime.now().strftime('%H'))
            if 8 <= now_hour <= 16:
                data = get_stock_data(stock_id)

                result_list = []
                if len(data) > 0:
                    result_list = policies[policy_name](data)
                db_redis.set(stock_id + '_' + policy_name, json.dumps(result_list))

        except Exception as e:
            logging.warning("save policy error.", e)

        print(datetime.now())
        schdule.enter(1, 0, func_policy, (stock_id, policy_name))


def discover_stock():
    try:
        stock_name_map = json.loads(db_redis.get("stock_name_map"))
        for stock_id in stock_name_map.keys():
            if stock_id not in stock_policy_locks:
                stock_policy_locks[stock_id] = {}
            for (policy_name, policy_handle) in policies.items():
                if policy_name not in stock_policy_locks[stock_id]:
                    stock_policy_locks[stock_id][policy_name] = threading.Lock()
                    schdule.enter(0, 0, func_policy, (stock_id, policy_name))
    except Exception as e:
        logging.warning("discover_stock error.", e)
    schdule.enter(10, 0, discover_stock, )


if __name__ == "__main__":
    print(VERSION)
    schdule.enter(0, 0, discover_stock, )
    schdule.run()
