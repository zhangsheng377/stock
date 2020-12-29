import redis

from DATABASE import database_factory

db_sheets = {
    "600196": database_factory(database_name="tushare", sheet_name="sh_600196", model="pymongo"),
    "600511": database_factory(database_name="tushare", sheet_name="sh_600511", model="pymongo"),
    "601012": database_factory(database_name="tushare", sheet_name="sh_601012", model="pymongo"),
    "600559": database_factory(database_name="tushare", sheet_name="sh_600559", model="pymongo"),
}

db_redis = redis.Redis(host='192.168.10.5', port=6379, db=0)
