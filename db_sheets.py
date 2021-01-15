import json

import redis

from DATABASE import database_factory

db_sheets = {
    "600196": database_factory(database_name="tushare", sheet_name="sh_600196", model="pymongo"),
    "600511": database_factory(database_name="tushare", sheet_name="sh_600511", model="pymongo"),
    "601012": database_factory(database_name="tushare", sheet_name="sh_601012", model="pymongo"),
    "600559": database_factory(database_name="tushare", sheet_name="sh_600559", model="pymongo"),
    "688123": database_factory(database_name="tushare", sheet_name="sh_688123", model="pymongo"),
    "300815": database_factory(database_name="tushare", sheet_name="sh_300815", model="pymongo"),
    "300719": database_factory(database_name="tushare", sheet_name="sh_300719", model="pymongo"),
    "600519": database_factory(database_name="tushare", sheet_name="sh_600519", model="pymongo"),
    "300999": database_factory(database_name="tushare", sheet_name="sh_300999", model="pymongo"),
}


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
