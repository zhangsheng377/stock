import logging
import sched
import time
from datetime import datetime

import pandas
import requests

from ftqq_tokens import ftqq_tokens
from DATABASE import database_factory
from MODEL import macd_5_minute, magic_nine_turns

mongo_db_600196 = database_factory(database_name="tushare", sheet_name="sh_600196", model="pymongo")

VERSION = "0.0.5"

schdule = sched.scheduler(time.time, time.sleep)
old_time = ""

policies = [macd_5_minute.handel,
            magic_nine_turns.handel,
            ]


def func():
    global old_time
    try:
        # date_str = datetime.now().strftime("%Y-%m-%d")
        date_str = '2020-12-18'

        regex_str = '^' + date_str
        data = mongo_db_600196.find(filter={'_id': {"$regex": regex_str}}, sort=[('_id', 1)])

        result_list = []
        for policy in policies:
            result_list.extend(policy(data))

        data_result_df = pandas.DataFrame(result_list)
        if not data_result_df.empty and data_result_df['time'][data_result_df.shape[0] - 1] != old_time:
            data_result_df = data_result_df.sort_values(by='time', ascending=True)
            old_time = data_result_df['time'][data_result_df.shape[0] - 1]
            print(data_result_df)
            print(old_time)

            data_result_df[' '] = '&nbsp;&nbsp;&nbsp;&nbsp;'
            data_result_df = data_result_df[['time', ' ', 'price', ' ', '指标']]
            try:
                result_markdown = data_result_df.to_markdown(index=False)
            except Exception as e:
                result_markdown = data_result_df.to_markdown(showindex=False)
            print(result_markdown)

            for ftqq_token in ftqq_tokens:
                res = requests.post('https://sc.ftqq.com/{}.send'.format(ftqq_token),
                                    data={'text': 'ig507_600196',
                                          'desp': result_markdown + "\n\n" + datetime.now().strftime(
                                              "%Y-%m-%d %H:%M:%S")})
                print(res.text)
    except Exception as e:
        if e.args[0] == 'data_df is empty':
            logging.info("data_df is empty.")
        else:
            logging.warning("handle data error.", e)

    print(datetime.now())
    schdule.enter(1, 0, func)


print(VERSION)
schdule.enter(0, 0, func)
schdule.run()
