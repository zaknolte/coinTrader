import requests
import math
import datetime
import sqlite3

from typing import List


def get_candles_data(product: str, granularity: int, start: datetime.datetime, end=datetime.datetime.utcnow()) -> List[List]:
    """
    Query the coinbase web API to retrieve the candle data for a given product code at a given granularity (candle time size).

    :param product: Coinbase crypto pair to retrieve. Ex: ETH-USD, BTC-USD
    :param granularity: Candle size in seconds. Must be one of: [60, 300, 900, 3600, 21600, 86400]
    :param start: UTC start time of query. Ex: 2023-10-06T10:34:47.123456Z
    :param end: UTC end time of query. Ex: 2023-11-06T10:34:47.123456Z
    :return: data: List of lists containing [Time (seconds from epoch), Low price, High price, Open price, Close price, Volume]
    """
    data = []
    MAX_CANDLES = 300  # Coinbase API limit
    new_start = start

    total_minutes = (end - start).total_seconds() / 60
    total_candles = total_minutes / (granularity / 60)
    total_steps = math.ceil(total_candles / MAX_CANDLES)

    for i in range(total_steps):
        step_end = new_start + datetime.timedelta(minutes=300 * granularity / 60)
        print(f"Collecting {product} data from {new_start} through {step_end} at granularity {granularity}...")
        query = f"granularity={granularity}&start={new_start}&end={step_end}"
        r = requests.get(f"https://api.exchange.coinbase.com/products/eth-usd/candles?{query}")
        d = r.json()
        data.extend(d)
        new_start = step_end

    return data


get_candles_data("ETH-USD", 300, datetime.datetime(2024, 3, 1, 0, 0, 0))
