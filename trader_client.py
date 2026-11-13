from alpaca.trading import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from datetime import datetime, timezone

api_key = "PKFZCASF5ECECARFG374SUUXBD"
secret_key = "3xRE5SVzfxgFHqE4zehD6ByNw9zCcwkgajKasZjcqJqJ"

trading_client = TradingClient(api_key, secret_key, paper=True)
request_client = StockHistoricalDataClient(api_key, secret_key)

request_params = StockBarsRequest(
    symbol_or_symbols=["AAPL"],
    timeframe=TimeFrame.Minute,
    start=datetime.now(timezone.utc).replace(hour=9, minute=30, second=0, microsecond=0)
)

bars = request_client.get_stock_bars(request_params)