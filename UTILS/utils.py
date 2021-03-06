import json
import os
import uuid
from datetime import datetime

import pandas
import requests
import matplotlib.pyplot as plt

from UTILS.upload_pic import upload
from db_sheets import db_redis

stock_name_map = json.loads(db_redis.get('stock_name_map'))


def plot_result(data, data_result_df, file_name):
    data_df = pandas.DataFrame(data)
    if data_df.empty:
        raise Exception("data_df is empty")
    data_df['minute'] = data_df['time'].str.slice(stop=5)
    data_minute_df = data_df.drop_duplicates(subset=['minute'], keep='last')

    data_plt = data_minute_df[['time', 'price']]
    data_plt['time'] = pandas.to_datetime(data_plt['time'])
    data_plt['price'] = pandas.to_numeric(data_plt['price'])
    plt.plot(data_plt['time'], data_plt['price'])

    data_plt = data_result_df[['time', 'price', 'plt']]
    data_plt['time'] = pandas.to_datetime(data_plt['time'])
    data_plt['price'] = pandas.to_numeric(data_plt['price'])
    for index, row in data_plt.T.iteritems():
        plt.plot(row['time'], row['price'], row['plt'], markersize=10)
    # plt.show()

    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    plt.savefig(os.path.join('tmp', file_name))
    plt.close()

    upload(file_name + ".png")


def send_result(stock_id, data, result_list, ftqq_token, old_result_len):
    data_result_df = pandas.DataFrame(result_list)
    if len(data) > 0 and not data_result_df.empty and data_result_df.shape[0] != old_result_len:
        data_result_df = data_result_df.sort_values(by='time', ascending=True)
        old_result_len = data_result_df.shape[0]
        # print(data_result_df)
        # print(old_result_len)

        file_name = str(uuid.uuid1())
        try:
            plot_result(data, data_result_df, file_name)
        except Exception as e:
            print(e)

        data_result_df[' '] = '&nbsp;&nbsp;&nbsp;&nbsp;'
        data_result_df = data_result_df[['time', ' ', 'price', ' ', '指标']]
        try:
            result_markdown = data_result_df.to_markdown(index=False)
        except Exception as e:
            result_markdown = data_result_df.to_markdown(showindex=False)
        result_markdown += "\n\n![](http://image.zhangshengdong.com/{}.png)".format(file_name)
        print(result_markdown)

        res = requests.post('https://sc.ftqq.com/{}.send'.format(ftqq_token),
                            data={'text': stock_name_map[stock_id] + " " + stock_id,
                                  'desp': result_markdown + "\n\n" + datetime.now().strftime(
                                      "%Y-%m-%d %H:%M:%S")})
        print(res.text)

    return data_result_df.shape[0]
