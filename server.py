from flask import Flask, request
import datetime
import xmltodict
import time
import re

from func import send_one
from UTILS.db_sheets import get_users, insert_users, update_one_user

application = Flask(__name__)


# application.debug = True


def get_filter_users(filter: dict):
    users = get_users()
    result = []
    for user in users:
        is_find = True
        for key, value in filter.items():
            if key not in user or user[key] != value:
                is_find = False
                break
        if is_find:
            result.append(user)
    return result


@application.route('/')
def hello_world():
    return 'Hello, World!' + '<br /><br />' + str(datetime.datetime.now())


@application.route('/wx', methods=["GET", "POST"])
def get():
    if request.method == "GET":  # 判断请求方式是GET请求
        my_echostr = request.args.get('echostr')  # 获取携带的echostr参数
        return my_echostr
    else:
        # 表示微信服务器转发消息过来
        xml_str = request.data
        if not xml_str:
            return ""
        resp_dict = None
        re_content = "信息错误"
        # 对xml字符串进行解析
        xml_dict = xmltodict.parse(xml_str)
        xml_dict = xml_dict.get("xml")

        # 提取消息类型
        msg_type = xml_dict.get("MsgType")
        if msg_type == "text":  # 表示发送的是文本消息
            content = xml_dict.get("Content")
            if content == "清除缓存":
                re_content = "缓存已清除"
            elif content == "查询已订阅股票":
                result = get_filter_users(filter={'wechat': xml_dict.get("FromUserName")})
                if result:
                    re_content = str(result[0]['stocks'])
                else:
                    re_content = "尚未绑定微信"
            elif re.fullmatch(r'\d{6}\.\w{2}', content):
                re_content = "code: " + content
            elif content.startswith("查询 "):
                try:
                    datas = content.split(" ")
                    stock_id = datas[1]
                    result = get_filter_users(filter={'wechat': xml_dict.get("FromUserName")})
                    if result:
                        user_name = result[0]['_id']
                        re_len = send_one(result[0], stock_id)
                        re_content = "发送成功: {} {} {}".format(user_name, stock_id, re_len)
                    else:
                        re_content = "尚未绑定微信"
                except Exception as e:
                    re_content = "发送失败: " + str(e)
                    application.logger.error(re_content)
            elif content.startswith("绑定 "):
                datas = content.split(" ")
                user_name = datas[1]
                # 此处逻辑需要细考
                if get_filter_users(filter={'_id': user_name}):
                    re_content = "您要绑定的用户名:{}，已被人绑定!请联系微信435878393".format(user_name)
                elif get_filter_users(filter={'wechat': xml_dict.get("FromUserName")}):
                    re_content = "您的微信已被绑定!请联系微信435878393"
                else:
                    if insert_users(document={'_id': user_name, 'wechat': xml_dict.get("FromUserName")}):
                        re_content = "绑定成功"
                    else:
                        re_content = "绑定失败"
            elif content.startswith("订阅 "):
                datas = content.split(" ")
                stock_id = datas[1]
                result = get_filter_users(filter={'wechat': xml_dict.get("FromUserName")})
                if result:
                    data = result[0]
                    if 'stocks' not in data.keys():
                        data['stocks'] = []
                    stocks = set(data['stocks'])
                    stocks.add(stock_id)
                    _filter = {'wechat': xml_dict.get("FromUserName")}
                    _update = {'$set': {'stocks': list(stocks)}}
                    result = update_one_user(filter=_filter, update=_update)
                    re_content = f"订阅失败. {_filter} {_update} {result.raw_result}"
                    if result is not None and result.modified_count > 0:
                        re_content = "订阅成功"
                else:
                    re_content = "尚未绑定微信"
            elif content.startswith("取消订阅 "):
                datas = content.split(" ")
                stock_id = datas[1]
                result = get_filter_users(filter={'wechat': xml_dict.get("FromUserName")})
                if result:
                    data = result[0]
                    if 'stocks' not in data.keys():
                        data['stocks'] = []
                    stocks = set(data['stocks'])
                    if stock_id in stocks:
                        stocks.remove(stock_id)
                        _filter = {'wechat': xml_dict.get("FromUserName")}
                        _update = {'$set': {'stocks': list(stocks)}}
                        result = update_one_user(filter=_filter, update=_update)
                        re_content = f"尚未订阅{stock_id}. {_filter} {_update} {result.raw_result}"
                        if result is not None and result.modified_count > 0:
                            re_content = "取消订阅成功"
                    else:
                        re_content = f"尚未订阅{stock_id}"
                else:
                    re_content = "尚未绑定微信"
            else:
                re_content = content

        if not resp_dict:
            # 构造返回值，经由微信服务器回复给用户的消息内容
            resp_dict = {
                "xml": {
                    "ToUserName": xml_dict.get("FromUserName"),
                    "FromUserName": xml_dict.get("ToUserName"),
                    "CreateTime": int(time.time()),
                    "MsgType": "text",
                    "Content": re_content,
                }
            }

        # 将字典转换为xml字符串
        resp_xml_str = xmltodict.unparse(resp_dict)
        # 返回消息数据给微信服务器
        return resp_xml_str


if __name__ == "__main__":
    # application.run(host="0.0.0.0", port=5000)
    application.run(host="0.0.0.0")
