import plotly.graph_objects as go


class CoinTrader:
    def __init__(self, funds, volatility_buffer=0.015):
        self.funds = funds
        self.volatility_buffer = volatility_buffer
        self.trade_mode = "buy"
        self.current_low = 0
        self.current_high = 0
        self.volume = 0

    def run_historical_trades(self, historical_data, conditional=None):
        if conditional is None:
            def conditional(data, mode):
                if mode == "buy":
                    if data["Low"] < self.current_low:
                        self.current_low = data["Low"]
                    if data["Close"] >= (data["Low"] + data["Low"] * self.volatility_buffer):
