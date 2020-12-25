import logging
import sched
import threading
import time
from datetime import datetime

from MODEL import macd_5_minute, magic_nine_turns
from UTILS.utils import send_result
from ftqq_tokens import users
from db_sheets import db_sheets

VERSION = "0.0.7"

schdule = sched.scheduler(time.time, time.sleep)

user_stock_locks = {}

policies = [
    macd_5_minute.handel,
    magic_nine_turns.handel,
]


def func(user_name, stock_id, old_result_len):
    with user_stock_locks[user_name][stock_id]:
        try:
            # print(db_sheet, ftqq_token, old_result_len)
            data = get_today_tick_data(db_sheets[stock_id])

            result_list = []
            for policy in policies:
                result_list.extend(policy(data))

            old_result_len = send_result(stock_id, data, result_list, users[user_name]['ftqq_token'], old_result_len)
        except Exception as e:
            if e.args[0] == 'data_df is empty':
                logging.info("data_df is empty.")
            else:
                logging.warning("handle data error.", e)

        print(datetime.now())
        schdule.enter(1, 0, func, (user_name, stock_id, old_result_len))


def get_today_tick_data(db_sheet):
    date_str = datetime.now().strftime("%Y-%m-%d")
    # date_str = '2020-12-18'
    regex_str = '^' + date_str
    data = db_sheet.find(filter={'_id': {"$regex": regex_str}}, sort=[('_id', 1)])
    return data


print(VERSION)
for (user_name, user_data) in users.items():
    user_stock_locks[user_name] = {}
    for stock_id in user_data['stocks']:
        user_stock_locks[user_name][stock_id] = threading.Lock()
        schdule.enter(0, 0, func, (user_name, stock_id, 0))
schdule.run()
