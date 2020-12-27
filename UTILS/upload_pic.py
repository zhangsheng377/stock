import os

from qiniu import Auth, put_file

from db_sheets import db_redis


def upload(file_name):
    q = Auth(db_redis.get('qiniu_access_key'), db_redis.get('qiniu_secret_key'))
    # 要上传的空间
    bucket_name = 'public-bz'

    token = q.upload_token(bucket_name, file_name)
    ret, info = put_file(token, file_name, os.path.join('tmp', file_name))
    return
