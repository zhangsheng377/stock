import json
import re
from datetime import datetime

import redis

from DATABASE import database_factory


def get_db_sheet(database_name, sheet_name):
    return database_factory(database_name=database_name, sheet_name=sheet_name, model="pymongo")


def _get_data(key: str, get_db_func):
    data_redis = db_redis.get(key)
    if data_redis is None:
        data = get_db_func()
        db_redis.set(key, json.dumps(data))
    else:
        data = json.loads(data_redis)
    return data


def get_db_users():
    user_db_sheet = get_db_sheet(database_name="user", sheet_name="user")
    return user_db_sheet.find()


def get_users():
    return _get_data('users', get_db_users)


def update_redis_users_from_db():
    data = get_db_users()
    db_redis.set('users', json.dumps(data))


def insert_users(document):
    user_db_sheet = get_db_sheet(database_name="user", sheet_name="user")
    if user_db_sheet.insert(document=document):
        users = get_users()
        db_redis.set('users', json.dumps(users))
        return True
    return False


def update_one_user(filter, update):
    user_db_sheet = get_db_sheet(database_name="user", sheet_name="user")
    result = user_db_sheet.update_one(filter=filter, update=update)
    update_redis_users_from_db()
    return result


def get_today_tick_data(db_sheet):
    date_str = datetime.now().strftime("%Y-%m-%d")
    # date_str = '2020-12-25'
    regex_str = '^' + date_str
    data = db_sheet.find(filter={'_id': {"$regex": regex_str}}, sort=[('_id', 1)])
    return data


def get_stock_data(stock_id):
    def get_db_stock_data():
        db_sheet = get_db_sheet(database_name="tushare", sheet_name="sh_" + stock_id)
        return get_today_tick_data(db_sheet)

    return _get_data(stock_id, get_db_stock_data)


def add_stock_data(stock_id, insert_data_json):
    db_sheet = get_db_sheet(database_name="tushare", sheet_name="sh_" + stock_id)
    if db_sheet.insert(insert_data_json):
        data = get_today_tick_data(db_sheet)
        db_redis.set(stock_id, json.dumps(data))
        return True
    return False


def get_stock_ids():
    def get_db_stock_ids():
        database = get_db_sheet(database_name="tushare", sheet_name="sh_600196").get_database()
        return database.list_collection_names(filter={"name": re.compile('^sh_\d{6}')})

    # return _get_data('stock_ids', get_db_stock_ids)
    # return get_db_stock_ids()
    stock_ids = {stock_id[3:] for stock_id in get_db_stock_ids()}
    users = get_users()
    for user in users:
        stock_ids = stock_ids | set(user['stocks'])
    return stock_ids


db_redis = redis.Redis(host='192.168.10.5', port=6379, db=0)

if __name__ == '__main__':
    users = get_users()
    print(users)
    print(type(users), type(users[0]))

    print(get_stock_ids())
