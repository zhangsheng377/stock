import json
import datetime

from flask import Flask, request

from UTILS.utils import send_result, get_policy_datas
from UTILS.config import VERSION, LOGGING_LEVEL
from UTILS.db_sheets import get_users, get_stock_data
from UTILS.config_port import user_send_port

application = Flask(__name__)
# application.debug = True
application.logger.setLevel(LOGGING_LEVEL)


def ftqq_token_is_valid(ftqq_token):
    return ftqq_token is not None and ftqq_token != ''


def get_user(user_id):
    users = get_users()
    for user in users:
        if user['_id'] == user_id:
            return user
    return None


@application.route('/')
def hello_world():
    return 'Hello, World!' + '<br /><br />' + str(datetime.datetime.now())


@application.route('/send_user', methods=["GET"])
def send_user():
    # 以GET方式传参数，通过args取值
    user_id = json.loads(request.args['user_id'])
    stock_id = json.loads(request.args['stock_id'])
    old_result_len = json.loads(request.args['old_result_len'])
    result_len = _send_user(user_id, stock_id, old_result_len)
    return json.dumps(result_len)


def _send_user(user_id, stock_id, old_result_len):
    application.logger.info(f"{user_id}, {stock_id}, {old_result_len}")
    user = get_user(user_id)
    if user is None:
        application.logger.warning(f"user is None. \n\n\n")
        return old_result_len

    ftqq_token = user['ftqq_token']
    if not ftqq_token_is_valid(ftqq_token):
        application.logger.warning(f"not ftqq_token_is_valid(ftqq_token). \n\n\n")
        return old_result_len

    try:
        data = get_stock_data(stock_id)

        result_list = get_policy_datas(stock_id, user['policies'])
        if len(result_list) == old_result_len:
            application.logger.warning(f"len(result_list) == old_result_len. old_result_len={old_result_len}. \n\n\n")
            return old_result_len

        return send_result(stock_id, data, result_list, ftqq_token, old_result_len)

    except Exception as e:
        if e.args[0] == 'data_df is empty':
            application.logger.info("data_df is empty. \n\n\n")
        else:
            application.logger.warning("handle data error.", exc_info=True)
    return old_result_len


if __name__ == "__main__":
    application.logger.info(f"VERSION: {VERSION}")
    # application.run(host="0.0.0.0", port=user_send_port)
    application.run(host="0.0.0.0")
