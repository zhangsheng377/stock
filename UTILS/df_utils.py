import pandas as pd

def get_minute_df(df) -> pd.DataFrame:
    df['minute'] = df['time'].str.slice(stop=5)
    df['price'] = df['price'].astype(float)
    avg_minute_price = df.groupby('minute')['price'].mean().rename('minute_price')
    data_minute_df = df.drop_duplicates(subset=['minute'], keep='last')
    data_minute_df = data_minute_df.merge(avg_minute_price, left_on='minute', right_index=True, how='left')
    data_minute_df['minute_price'] = data_minute_df['minute_price'].fillna(method='ffill')
    return data_minute_df
