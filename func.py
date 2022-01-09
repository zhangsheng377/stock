import json

from flask import Flask, request

from UTILS.utils import send_result, VERSION
from UTILS.db_sheets import db_redis, get_users, get_stock_data
from UTILS.config_port import user_send_port

application = Flask(__name__)


# application.debug = True


def ftqq_token_is_valid(ftqq_token):
    return ftqq_token is not None and ftqq_token != ''


def get_policy_data(stock_id, policy_name):
    data = db_redis.get(stock_id + '_' + policy_name)
    if data is None:
        data = '[]'
    return json.loads(data)


def get_user(user_id):
    users = get_users()
    for user in users:
        if user['_id'] == user_id:
            return user
    return None


@application.route('/send_user', methods=["GET"])
def send_user():
    # 以GET方式传参数，通过args取值
    user_id = request.args['user_id']
    stock_id = request.args['stock_id']
    old_result_len = request.args['old_result_len']
    result_len = _send_user(user_id, stock_id, old_result_len)
    return json.dumps(result_len)


def _send_user(user_id, stock_id, old_result_len):
    application.logger.info(f"{user_id}, {stock_id}, {old_result_len}")
    user = get_user(user_id)
    if user is None:
        return -1

    ftqq_token = user['ftqq_token']
    if not ftqq_token_is_valid(ftqq_token):
        return -1

    try:
        data = get_stock_data(stock_id)

        result_list = []
        for policy_name in user['policies']:
            result_list.extend(get_policy_data(stock_id, policy_name))

        return send_result(stock_id, data, result_list, ftqq_token, old_result_len)
    except Exception as e:
        if e.args[0] == 'data_df is empty':
            application.logger.info("data_df is empty.")
            return 0
        else:
            application.logger.warning("handle data error.", e)
            return -1


if __name__ == "__main__":
    application.logger.info(f"{VERSION}")
    application.run(host="0.0.0.0", port=user_send_port)
