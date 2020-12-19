import pandas
import numpy
import talib


def MACD_CN(close, fastperiod=12, slowperiod=26, signalperiod=9):
    macdDIFF, macdDEA, macd = talib.MACDEXT(close, fastperiod=fastperiod, fastmatype=1, slowperiod=slowperiod,
                                            slowmatype=1, signalperiod=signalperiod, signalmatype=1)
    macd = macd * 2
    return macdDIFF, macdDEA, macd


def handel(data):
    data_df = pandas.DataFrame(data)
    if data_df.empty:
        raise Exception("data_df is empty")

    data_df['minute'] = data_df['time'].str.slice(stop=5)
    data_minute_df = data_df.drop_duplicates(subset=['minute'], keep='last')

    data_minute_df['tmp'] = data_minute_df['minute'].str.slice(start=4, stop=5)
    data_5_minute_df = pandas.concat([data_minute_df[data_minute_df['tmp'] == '0'],
                                      data_minute_df[data_minute_df['tmp'] == '5']])
    data_5_minute_df = data_5_minute_df.sort_values(by='minute', ascending=True)

    data_5_minute_df['macdDIFF'], data_5_minute_df['macdDEA'], data_5_minute_df['macd'] = MACD_CN(
        data_5_minute_df['price'])

    result_list = []

    for i in range(1, data_5_minute_df.shape[0]):
        before = data_5_minute_df.iloc[i - 1]['macd']
        now = data_5_minute_df.iloc[i]['macd']

        if numpy.sign(before) != numpy.sign(now):
            if now > 0:
                result_list.append({'time': data_5_minute_df.iloc[i]['time'],
                                    'price': data_5_minute_df.iloc[i]['price'],
                                    '指标': 'macd信号,将持续上涨',
                                    })
            elif now < 0:
                result_list.append({'time': data_5_minute_df.iloc[i]['time'],
                                    'price': data_5_minute_df.iloc[i]['price'],
                                    '指标': 'macd信号,将持续下跌',
                                    })
    return result_list
