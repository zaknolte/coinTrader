import pandas as pd
import plotly.graph_objects as go

from typing import List


def plot_candles(data: List[List]) -> None:
    """
    Display the supplied candle data into an interactive graph.

    **WARNING**: supplying an excessive amount of data points will slow down the graphing.

    :param data: List of lists containing [Time (seconds from epoch), Low price, High price, Open price, Close price, Volume]
    :return: None
    """
    df = pd.DataFrame(data, columns=["Time", "Low", "High", "Open", "Close", "Volume"])
    df["Time"] = pd.to_datetime(df["Time"], unit="s")
    fig = go.Figure(
        go.Candlestick(
            x=df["Time"],
            open=df["Open"],
            close=df["Close"],
            high=df["High"],
            low=df["Low"]
        )
    )
    fig.show()