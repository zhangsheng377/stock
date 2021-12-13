import pandas

from UTILS.df_utils import get_minute_df


def handel(data):
    data_df = pandas.DataFrame(data)
    if data_df.empty:
        raise Exception("data_df is empty")

    data_minute_df = get_minute_df(data_df)

    result_list = []

    count = 0
    direction = 'none'
    for i in range(4, data_minute_df.shape[0]):
        before = data_minute_df.iloc[i - 4]['minute_price']
        now = data_minute_df.iloc[i]['minute_price']

        if now > before:
            if direction == 'up':
                if count == 9:
                    result_list.append({'time': data_minute_df.iloc[i]['time'],
                                        'price': data_minute_df.iloc[i]['price'],
                                        '指标': '神奇九转,连续上涨,将大概率下跌',
                                        'plt': 'go',
                                        })
                    count = -1
            else:
                direction = 'up'
                count = 0
        elif now < before:
            if direction == 'down':
                if count == 9:
                    result_list.append({'time': data_minute_df.iloc[i]['time'],
                                        'price': data_minute_df.iloc[i]['price'],
                                        '指标': '神奇九转,连续下跌,将大概率上涨',
                                        'plt': 'ro',
                                        })
                    count = -1
            else:
                direction = 'down'
                count = 0
        count += 1

    return result_list
