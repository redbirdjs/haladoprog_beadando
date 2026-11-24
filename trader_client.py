from alpaca.trading import TradingClient
from alpaca.trading.requests import GetPortfolioHistoryRequest, OrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

from env import api_key, api_secret

trading_client = TradingClient(api_key, api_secret, paper=True)
request_client = StockHistoricalDataClient(api_key, api_secret)

def get_market_clock():
    return trading_client.get_clock()

def get_portfolio_history():
    portfolio_params = GetPortfolioHistoryRequest(
        period="1D",
        timeframe="1Min"
    )

    portfolio_history = trading_client.get_portfolio_history(portfolio_params)
    return portfolio_history

def get_candle_chart():
    candle_data = []

    symbols = [item.symbol for item in trading_client.get_all_positions()]
    if len(symbols) == 0:
        return candle_data

    # stockokhoz tartozó adatok lekérdezése
    request_params = StockBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=TimeFrame.Minute,
        start=datetime(datetime.now().year, datetime.now().month, datetime.now().day-1, 16)
    )
    candle_data = request_client.get_stock_bars(request_params)

    return candle_data

def get_time_in_force(tif):
    if (tif == 'gtc'): 
        return TimeInForce.GTC
    if (tif == 'otg'): 
        return TimeInForce.OPG
    if (tif == 'cls'): 
        return TimeInForce.CLS
    if (tif == 'ioc'):
        return TimeInForce.IOC
    if (tif == 'fok'):
        return TimeInForce.FOK

    return TimeInForce.DAY

def convert_to_order(item):
    return OrderRequest(
        type="market",
        symbol=item['symbol'],
        qty=item['qty'],
        side=OrderSide.BUY if item['side'] == 'buy' else OrderSide.SELL,
        time_in_force=get_time_in_force(item['time_in_force'])
    )

def send_orders(orders):
    for order in orders:
        trading_client.submit_order(convert_to_order(order))

def get_all_orders(limit=250, return_tuple=False):
    request = GetOrdersRequest(
        status=QueryOrderStatus.ALL,
        limit=limit,
        nested=True
    )
    orders = trading_client.get_orders(filter=request)

    if return_tuple:
        return [(
            order.symbol, order.qty, order.side.value, order.status.value, order.created_at.strftime("%Y-%m-%d | %H:%M:%S"), order.expires_at.strftime("%Y-%m-%d | %H:%M:%S") if order.expires_at else None
        ) for order in orders]

    return [{
        "symbol": order.symbol,
        "qty": order.qty,
        "side": order.side.value,
        "status": order.status.value,
        "created_at": order.created_at.strftime("%Y-%m-%d | %H:%M:%S"),
        "expires_at": order.expires_at.strftime("%Y-%m-%d | %H:%M:%S") if order.expires_at else None,
    } for order in orders]