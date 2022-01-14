from datetime import datetime, timedelta


def get_rest_seconds():
    now = datetime.now()

    today_begin = datetime(now.year, now.month, now.day, 8, 0, 0)
    tomorrow_begin = today_begin + timedelta(days=1)

    rest_seconds = (tomorrow_begin - now).seconds
    return rest_seconds
