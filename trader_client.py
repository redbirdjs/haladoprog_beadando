from alpaca.trading import TradingClient
from alpaca.trading.requests import GetPortfolioHistoryRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from datetime import datetime, timezone

api_key = "PKFZCASF5ECECARFG374SUUXBD"
secret_key = "3xRE5SVzfxgFHqE4zehD6ByNw9zCcwkgajKasZjcqJqJ"

trading_client = TradingClient(api_key, secret_key, paper=True)
request_client = StockHistoricalDataClient(api_key, secret_key)

market_data = trading_client.get_clock()

# portfolio változás adatok
portfolio_params = GetPortfolioHistoryRequest(
    period="1D",
    timeframe="1Min"
)

portfolio_history = trading_client.get_portfolio_history(portfolio_params)

# portfolio symbols
symbols = [item.symbol for item in trading_client.get_all_positions()]

# stockokhoz tartozó adatok lekérdezése
request_params = StockBarsRequest(
    symbol_or_symbols=symbols,
    timeframe=TimeFrame.Minute,
    start=datetime(datetime.now().year, datetime.now().month, datetime.now().day-1, 16)
)
candle_data = []
if len(symbols) > 0:
    candle_data = request_client.get_stock_bars(request_params)