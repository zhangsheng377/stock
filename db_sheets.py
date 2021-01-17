import json

import redis

from DATABASE import database_factory


def get_db_sheet(database_name, sheet_name):
    return database_factory(database_name=database_name, sheet_name=sheet_name, model="pymongo")


db_redis = redis.Redis(host='192.168.10.5', port=6379, db=0)
