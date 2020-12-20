import logging
import sched
import time
from datetime import datetime

from DATABASE import database_factory
from MODEL import macd_5_minute, magic_nine_turns
from UTILS.utils import send_result

mongo_db_600196 = database_factory(database_name="tushare", sheet_name="sh_600196", model="pymongo")

VERSION = "0.0.5"

schdule = sched.scheduler(time.time, time.sleep)

policies = [macd_5_minute.handel,
            magic_nine_turns.handel,
            ]


def func():
    try:
        data = get_today_tick_data()

        result_list = []
        for policy in policies:
            result_list.extend(policy(data))

        send_result(data, result_list)
    except Exception as e:
        if e.args[0] == 'data_df is empty':
            logging.info("data_df is empty.")
        else:
            logging.warning("handle data error.", e)

    print(datetime.now())
    schdule.enter(1, 0, func)


def get_today_tick_data():
    date_str = datetime.now().strftime("%Y-%m-%d")
    # date_str = '2020-12-18'
    regex_str = '^' + date_str
    data = mongo_db_600196.find(filter={'_id': {"$regex": regex_str}}, sort=[('_id', 1)])
    return data


print(VERSION)
schdule.enter(0, 0, func)
schdule.run()
