from DATABASE import database_factory

db_sheets = {
    "600196": database_factory(database_name="tushare", sheet_name="sh_600196", model="pymongo"),
    "600511": database_factory(database_name="tushare", sheet_name="sh_600511", model="pymongo"),
}
