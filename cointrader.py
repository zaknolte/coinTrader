import sqlite3
import pandas as pd
import plotly.graph_objects as go
from typing import List


class CoinTrader:
    def __init__(self, funds, volatility_buffer=0.01, data=None):
        self.funds = funds
        self.volatility_buffer = volatility_buffer
        self.data = data or self.load_data("ETH60")
        self.trade_mode = "buy"
        self.trades = []
        self.current_low = 999_999_999
        self.current_high = 0
        self.buy_price = 0
        self.profit = 0

    def load_data(self, currency, to_df=True):
        with sqlite3.connect("candles.db") as conn:
            c = conn.cursor()
            # can't substitute table name
            # use parameters to check if table exists first before executing normal SELECT
            table = c.execute("SELECT * FROM sqlite_master WHERE type='table' and name = ?", (currency,))

            if table.fetchall():
                query = f"SELECT * FROM {currency}"
                if to_df:
                    df = pd.read_sql_query(query, conn)
                    df["time"] = pd.to_datetime(df["time"], unit="s")
                    return df.sort_values(by=["time"])

                return c.execute(query).fetchall()

            raise Exception(f"Table {currency} does not exist in database!")

    def conditional(self, data):
        if self.trade_mode == "buy":
            buffer = self.current_low + (self.current_low * self.volatility_buffer)
            if data["low"] < self.current_low:
                self.current_low = data["low"]
            elif data["open"] >= buffer or data["high"] >= buffer:
                self.trades.append({"time": data["time"], "price": buffer, "mode": "buy"})
                self.trade_mode = "sell"
                self.buy_price = buffer

        elif self.trade_mode == "sell":
            buffer = self.current_high - (self.current_high * self.volatility_buffer)
            if data["high"] > self.current_high:
                self.current_high = data["high"]
            elif (data["open"] <= buffer and buffer > self.buy_price) or (data["low"] <= buffer and buffer > self.buy_price):
                self.trades.append({"time": data["time"], "price": buffer, "mode": "sell"})
                self.trade_mode = "buy"
                self.current_low = buffer
                self.calc_profit(buffer)

    def calc_profit(self, price):
        volume = self.funds / self.buy_price
        self.profit += (price * volume - self.funds)

    def run_historical_trades(self, conditional=None):
        if conditional is None:
            conditional = self.conditional

        for data in self.data.iterrows():
            conditional(data[1])
        self.trades = pd.DataFrame(self.trades)

    def plot_trades(self, overlay=True):
        buys = self.trades[self.trades["mode"] == "buy"]
        sells = self.trades[self.trades["mode"] == "sell"]
        fig = go.Figure(
            go.Scatter(
                x=buys["time"],
                y=buys["price"],
                mode="markers",
                marker_color="blue",
                name="BUYS"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=sells["time"],
                y=sells["price"],
                mode="markers",
                marker_color="yellow",
                name="SELLS"
            )
        )
        if overlay:
            fig.add_trace(
                go.Candlestick(
                    x=self.data["time"],
                    open=self.data["open"],
                    close=self.data["close"],
                    high=self.data["high"],
                    low=self.data["low"]
                )
            )
        fig.show()

    def plot_candles(self) -> None:
        """
        Display the supplied candle data into an interactive graph.

        **WARNING**: supplying an excessive amount of data points will slow down the graphing.

        :param data: List of lists containing [Time (seconds from epoch), Low price, High price, Open price, Close price, Volume]
        :return: None
        """
        fig = go.Figure(
            go.Candlestick(
                x=self.data["time"],
                open=self.data["open"],
                close=self.data["close"],
                high=self.data["high"],
                low=self.data["low"]
            )
        )
        fig.show()
