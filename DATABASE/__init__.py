# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def database_factory(database_name, sheet_name, model="pymongo"):
    if model == "pymongo":
        from .database_pymongo import DataBasePyMongo
        return DataBasePyMongo(database_name=database_name, sheet_name=sheet_name, host='172.17.0.5', port=49154)
    else:
        raise ValueError('model name: {} can not find.'.format(model))
        pass
