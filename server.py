from flask import Flask, request
import datetime
import xmltodict
import time
import re

from func import send_one

application = Flask(__name__)


# application.debug = True


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
            elif re.fullmatch(r'\d{6}\.\w{2}', content):
                re_content = "code: " + content
            elif content.startswith("发送"):
                try:
                    datas = content.split(" ")
                    user_name = datas[1]
                    stock_id = datas[2]
                    re_len = send_one(user_name, stock_id)
                    re_content = "发送成功: {} {} {}".format(user_name, stock_id, re_len)
                except Exception as e:
                    re_content = "发送失败：" + str(e)
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
