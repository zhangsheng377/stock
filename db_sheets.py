import json

import redis

from DATABASE import database_factory


def get_db_sheet(database_name, sheet_name):
    return database_factory(database_name=database_name, sheet_name=sheet_name, model="pymongo")


stock_name_map = {
    "600196": "复星医药",
    "600511": "国药股份",
    "601012": "隆基股份",
    "600559": "老白干酒",
    "688123": "聚辰股份",
    "300815": "玉禾田",
    "300719": "安达维尔",
    "600519": "贵州茅台",
    "300999": "金龙鱼",
}

db_redis = redis.Redis(host='192.168.10.5', port=6379, db=0)

db_redis.set("stock_name_map", json.dumps(stock_name_map))
