import os
import logging

from qiniu import Auth, put_file

from UTILS import config_qiniu  # 载入时会加载key
from UTILS.config import LOGGING_LEVEL

logging.getLogger().setLevel(LOGGING_LEVEL)


def upload(file_name):
    q = Auth(config_qiniu.access_key, config_qiniu.secret_key)
    # 要上传的空间
    bucket_name = 'public-bz'

    token = q.upload_token(bucket_name, file_name)
    ret, info = put_file(token, file_name, os.path.join('tmp', file_name))
    logging.info(f"{ret}, {info}")
    # if info.status_code != 200:
    #     t = config_qiniu.access_key
    return
