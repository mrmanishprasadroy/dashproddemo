import pandas as pd
import numpy as np
import json


def get_production():
    query_result = pd.read_csv('data/prod_tab.csv')
    # Fill Weight value to mean value or previous value
    query_result = query_result.replace('', np.nan)
    mean_weight = query_result['EXITWEIGHTMEAS'].mean(skipna=True)
    query_result.loc[query_result.EXITWEIGHTMEAS == 0, 'EXITWEIGHTMEAS'] = mean_weight
    query_result['EXITWEIGHTMEAS'] = query_result['EXITWEIGHTMEAS'].apply(lambda x: np.round(x, decimals=2))
    # query_result.fillna(method='ffill', inplace=True)
    # query_result['Date'] = query_result['DTDEPARTURE'].dt.date
    # query_result.dropna(axis=0, how='all')
    print(query_result.head())
    return query_result


def get_stop_time():
    query_result = pd.read_csv('data/stop_tab.csv')
    # query_result.set_index(['DTSTORE'], inplace=True)
    # query_result['PLANT'] = query_result.PLANT.map({1: 'PL', 2: 'TCM', 3: 'PLTCM'})
    query_result['DURATION'] = pd.to_datetime(query_result['DTEND']) - pd.to_datetime(query_result['DTSTART'])
    query_result['DURATION'] = query_result['DURATION'] / np.timedelta64(1, 'm')
    query_result['DTSTORE'] = pd.to_datetime(query_result['DTSTORE'])
    query_result['DATE'] = query_result.DTSTORE.dt.date
    query_result['YEAR'] = query_result.DTSTORE.dt.year
    query_result['MONTH'] = query_result.DTSTORE.dt.date.map(lambda x: x.strftime('%Y-%m'))
    query_result['DAY'] = query_result.DTSTORE.dt.day
    query_result['HOUR'] = query_result.DTSTORE.dt.hour
    print(query_result.tail())
    return query_result


def get_segment_data():
    with open('data/segmentdata.json') as json_file:
        data = json.load(json_file)
    return data


def get_process_data():
    with open('data/processdata.json') as json_file:
        data = json.load(json_file)
    return data
