import json
import logging
import sched
import threading
import time

import tushare as ts

from UTILS.db_sheets import get_db_sheet, add_stock_data, get_stock_ids, db_redis
from UTILS.rabbitmq_utils import RabbitMqAgent, polices_channel
from policies import policies
from UTILS.utils import is_stock_time
from UTILS.config import VERSION, LOGGING_LEVEL

logging.getLogger().setLevel(LOGGING_LEVEL)

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


def declare_polices_handle(stock_id):
    with RabbitMqAgent() as rabbitmq:
        for (policy_name, policy_handle) in policies.items():
            rabbitmq.put(queue_name=polices_channel, route_key=polices_channel,
                         message_str=json.dumps({'stock_id': stock_id, 'policy_name': policy_name}))


def add_one_stock_record(stock_id, last_time):
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
            logging.info(f"{data_json}")
            if add_stock_data(stock_id, data_json):
                logging.info(f"add_one_stock_record: {stock_id}")
                declare_polices_handle(stock_id)
                return last_time, True
            else:
                logging.warning("add_stock_data error.")
    except Exception as e:
        logging.warning("add_stock error.", e)
    # logging.info(f"add_one_stock_record: {stock_id} {last_time}")
    return last_time, False


def stock_spider(stock_id, last_time):
    with stock_locks[stock_id]:
        try:
            if is_stock_time():
                last_time, result = add_one_stock_record(stock_id, last_time)
                if result:
                    logging.info('插入成功\n')
                else:
                    logging.info('已经存在于数据库\n')
        except Exception as e:
            logging.warning("save tushare error.", e)

        # logging.info(f"stock_spider {stock_id}")
        schdule.enter(1, 0, stock_spider, (stock_id, last_time))


def set_stock_name_map(stock_id):
    def get_db_stock_name():
        stock_db_sheet = get_db_sheet(database_name="tushare", sheet_name='sh_' + stock_id)
        data_one = stock_db_sheet.find_one()
        if data_one is None or 'name' not in data_one:
            return stock_id
        return data_one['name']

    stock_name_map = json.loads(db_redis.get("stock_name_map"))
    stock_name_map[stock_id] = get_db_stock_name()
    db_redis.set("stock_name_map", json.dumps(stock_name_map))


def discover_stock():
    try:
        stock_ids = get_stock_ids()
        for stock_id in stock_ids:
            if stock_id not in stock_locks:
                logging.info(f"discover stock: {stock_id}")
                set_stock_name_map(stock_id)
                stock_locks[stock_id] = threading.Lock()
                schdule.enter(0, 0, stock_spider, (stock_id, None))
    except Exception as e:
        logging.warning("discover_stock error.", e)
    schdule.enter(10, 0, discover_stock, )


if __name__ == "__main__":
    logging.info(f"VERSION: {VERSION}")
    schdule.enter(0, 0, discover_stock, )
    schdule.run()
    # print(ts.get_realtime_quotes('000726'))
