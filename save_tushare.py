import json
import logging
import sched
import threading
import time
from datetime import datetime
from functools import partial

import tushare as ts

from db_sheets import get_db_sheet, add_stock_data, get_stock_ids, db_redis

VERSION = "0.0.8"

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


def get_today_tick_data(db_sheet):
    date_str = datetime.now().strftime("%Y-%m-%d")
    # date_str = '2020-12-25'
    regex_str = '^' + date_str
    data = db_sheet.find(filter={'_id': {"$regex": regex_str}}, sort=[('_id', 1)])
    return data


def add_stock(stock_id, last_time):
    try:
        df = ts.get_realtime_quotes(stock_id).tail(1)  # Single stock symbol
        data_dict = df.to_dict()
        data_price = data_dict['price'][0]
        data_time = data_dict['time'][0]
        if data_price != "0.000" and data_time != last_time:
            last_time = data_time

            data_json_str = df.to_json(orient='records')[1:-1]
            data_json = json.loads(data_json_str)

            data_json['_id'] = data_json['date'] + " " + data_json['time']
            print(data_json)
            db_sheet = get_db_sheet(database_name="tushare", sheet_name="sh_" + stock_id)
            add_result = add_stock_data(stock_id, data_json, partial(get_today_tick_data, db_sheet=db_sheet))
            if add_result:
                return last_time, True
            else:
                return last_time, False
    except Exception as e:
        logging.warning("add_stock error.", e)
    return last_time, False


def func(stock_id, last_time):
    with stock_locks[stock_id]:
        try:
            now_hour = int(datetime.now().strftime('%H'))
            if 8 <= now_hour <= 16:
                last_time, result = add_stock(stock_id, last_time)
                if result:
                    print('插入成功\n')
                else:
                    print('已经存在于数据库\n')
        except Exception as e:
            logging.warning("save tushare error.", e)

        print(datetime.now())
        schdule.enter(1, 0, func, (stock_id, last_time))


def set_stock_name_map(stock_id):
    def get_db_stock_name():
        stock_db_sheet = get_db_sheet(database_name="tushare", sheet_name=stock_id)
        data_one = stock_db_sheet.find_one()
        return data_one['name']

    stock_code = stock_id[3:]
    stock_name_map = json.loads(db_redis.get("stock_name_map"))
    stock_name_map[stock_code] = get_db_stock_name()
    db_redis.set("stock_name_map", json.dumps(stock_name_map))


def discover_stock():
    try:
        stock_ids = get_stock_ids()
        for stock_id in stock_ids:
            stock_code = stock_id[3:]
            if stock_code not in stock_locks:
                print("add stock:", stock_code)
                set_stock_name_map(stock_id)
                stock_locks[stock_code] = threading.Lock()
                schdule.enter(0, 0, func, (stock_code, None))
    except Exception as e:
        logging.warning("discover_stock error.", e)
    schdule.enter(10, 0, discover_stock, )


if __name__ == "__main__":
    print(VERSION)
    schdule.enter(0, 0, discover_stock, )
    schdule.run()
