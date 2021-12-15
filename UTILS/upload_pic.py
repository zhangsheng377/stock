import os

from qiniu import Auth, put_file

from db_sheets import db_redis
from UTILS import config_qiniu # 载入时会加载key


def upload(file_name):
    access_key = db_redis.get('qiniu_access_key').decode("utf-8")
    secret_key = db_redis.get('qiniu_secret_key').decode("utf-8")
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = 'public-bz'

    token = q.upload_token(bucket_name, file_name)
    ret, info = put_file(token, file_name, os.path.join('tmp', file_name))
    print(ret, info)
    return
