import sqlite3
import datetime
import os

from data_query import get_candles_data
from constants import PRODUCTS, PRODUCT_KEYS, GRANULARITY


def fill_tables():
    if not os.path.exists("candles.db"):
        raise Exception("Database does not exist! Please run init_db() to create database and tables first.")

    for product in PRODUCT_KEYS:
        for gran in GRANULARITY:
            data = get_candles_data(product, gran, start=datetime.datetime(2024, 3, 11, 0, 0, 0))

            with sqlite3.connect("candles.db") as conn:
                c = conn.cursor()
                c.executemany(f"INSERT INTO {product[:-4]}{gran} VALUES(?, ?, ?, ?, ?, ?)", data)


def init_db():
    """
    Create sqlite database and initialize all product tables.

    The following products are default added: ["ETH", "BTC", "SOL", "ADA", "DOGE"]

    The following candle time sizes (seconds) are added for each product: ['60', '300', '900', '3600', '21600', '86400']

    Tables ex: ETH60, BTC3600, ADA900, etc.

    **WARNING** Will delete existing tables and create a fresh empty table.
    """
    tables = [i + str(j) for i in PRODUCTS for j in GRANULARITY]
    with sqlite3.connect("candles.db") as conn:
        c = conn.cursor()
        for table in tables:
            c.execute(f"DROP TABLE IF EXISTS {table}")
            c.execute(f"CREATE TABLE {table} (time, low, high, open, close, volume)")
    fill_tables()
