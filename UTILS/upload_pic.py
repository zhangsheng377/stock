import os

from qiniu import Auth, put_file, etag

from UTILS.config_qiniu import access_key, secret_key


def upload(file_name):
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = 'public-bz'

    token = q.upload_token(bucket_name, file_name)
    ret, info = put_file(token, file_name, os.path.join('tmp', file_name))
    return
