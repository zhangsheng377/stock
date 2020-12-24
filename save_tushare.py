import json
import sched
import time
from datetime import datetime

import tushare as ts

from db_sheets import db_sheets

VERSION = "0.0.5"

schdule = sched.scheduler(time.time, time.sleep)

stock_locks = {}

'''
0：name，股票名字
1：open，今日开盘价
2：pre_close，昨日收盘价
3：price，当前价格
4：high，今日最高价
5：low，今日最低价
6：bid，竞买价，即“买一”报价
7：ask，竞卖价，即“卖一”报价
8：volume，成交量 maybe you need do volume/100
9：amount，成交金额（元 CNY）
10：b1_v，委买一（笔数 bid volume）
11：b1_p，委买一（价格 bid price）
12：b2_v，“买二”
13：b2_p，“买二”
14：b3_v，“买三”
15：b3_p，“买三”
16：b4_v，“买四”
17：b4_p，“买四”
18：b5_v，“买五”
19：b5_p，“买五”
20：a1_v，委卖一（笔数 ask volume）
21：a1_p，委卖一（价格 ask price）
...
30：date，日期；
31：time，时间；
'''


def func(stock_id, last_time):
    if not stock_locks[stock_id]:
        stock_locks[stock_id] = True
        df = ts.get_realtime_quotes(stock_id).tail(1)  # Single stock symbol
        data_dict = df.to_dict()
        data_time = data_dict['time'][0]
        if data_time != last_time:
            last_time = data_time

            data_json_str = df.to_json(orient='records')[1:-1]
            data_json = json.loads(data_json_str)

            data_json['_id'] = data_json['date'] + " " + data_json['time']
            print(data_json)
            insert_result = db_sheets[stock_id].insert(data_json)
            if insert_result:
                print('评论插入成功\n')
            else:
                print('已经存在于数据库\n')

        print(datetime.now())
        stock_locks[stock_id] = False
        schdule.enter(1, 0, func, (stock_id, last_time))


print(VERSION)
for stock_id in db_sheets.keys():
    stock_locks[stock_id] = False
    schdule.enter(0, 0, func, (stock_id, None))
schdule.run()
