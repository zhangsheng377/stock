import json
import logging
import sched
import time
from datetime import datetime

import numpy
import pandas
import requests
import talib

from ftqq_tokens import ftqq_tokens

schdule = sched.scheduler(time.time, time.sleep)
sign_len = 0
old_date = ""


def func():
    global sign_len
    global old_date
    res = requests.post(
        'http://ig507.com/data/time/history/trade/600196/5?licence=985508AC-EE35-5AC5-2B90-0A74F5AA20FB')
    try:
        data_json_list = json.loads(res.text)
        data_df = pandas.DataFrame(data_json_list)
        data_df['macd'], data_df['signal'], data_df['hist'] = talib.MACD(data_df['c'])

        date_str = datetime.now().strftime("%Y-%m-%d")
        # date_str = '2020-12-07'
        if date_str != old_date:
            old_date = date_str
            sign_len = 0
        data_df_today = data_df[data_df['d'].str.contains(date_str)]
        data_df_today['date'] = data_df_today['d'].str[11:]
        # print(data_df_today[['date', 'c', 'macd', 'signal', 'hist']].to_markdown(index=False))

        is_list = ['']
        for i in range(1, data_df_today.shape[0]):
            before = data_df_today.iloc[i - 1]['hist']
            now = data_df_today.iloc[i]['hist']
            if numpy.sign(before) != numpy.sign(now):
                is_list.append("macd信号,将持续当前走势")
            elif numpy.sign(now + (now - before) / 2) != numpy.sign(now):
                is_list.append("macd斜率信号,可能持续当前走势")
            else:
                is_list.append('')
        # data_df_today['is'] = is_list
        data_df_today.loc[:, 'is'] = is_list
        # print(data_df_today)

        data_df_is = data_df_today[data_df_today['is'] != '']
        if not data_df_is.empty and data_df_is.shape[0] > sign_len:
            sign_len = data_df_is.shape[0]
            print(data_df_is)

            # data_df_result = data_df_is[['date', 'c', 'macd', 'signal', 'hist', 'is']]
            data_df_result = data_df_is[['date', 'c', 'is']]
            data_df_result[' '] = '&nbsp;&nbsp;&nbsp;&nbsp;'
            data_df_result = data_df_result[['date', ' ', 'c', ' ', 'is']]
            data_df_result = data_df_result.rename(columns={"date": "time", "c": "股价", "is": "指标"})
            try:
                result_markdown = data_df_result.to_markdown(index=False)
            except Exception as e:
                result_markdown = data_df_result.to_markdown(showindex=False)
            print(result_markdown)

            for ftqq_token in ftqq_tokens:
                res = requests.post('https://sc.ftqq.com/{}.send'.format(ftqq_token),
                                    data={'text': 'ig507_600196',
                                          'desp': result_markdown + "\n\n" + datetime.now().strftime(
                                              "%Y-%m-%d %H:%M:%S")})
            print(res.text)
    except Exception as e:
        logging.warning("handle data error.", e)

    print(datetime.now())
    schdule.enter(60 * 5, 0, func)


schdule.enter(0, 0, func)
schdule.run()
