import random
import plotext as plt
from rich.text import Text
from textual.widgets import Static
from datetime import datetime, timedelta

plt.add_theme(
  "__default__",
  canvas="default",
  text="default",
  sequence=[107],
  grid="default"
)


class Chart(Static):
  ALLOW_SELECT = False
  data = None

  def __init__(self, data, get_chart_str, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.data = data
    self.str_fn = get_chart_str

  def on_mount(self):
    self.refresh_chart()

  def on_resize(self):
    self.refresh_chart()

  def refresh_chart(self):
    if self.data == None:
      return

    width = self.size.width
    height = self.size.height

    data = {'date': [], 'open': [], 'close': [], 'high': [], 'low': []}
    for item in self.data[-(width // 2 - 3):]:
      data['date'].append(item.timestamp)
      data['open'].append(item.open)
      data['close'].append(item.close)
      data['high'].append(item.high)
      data['low'].append(item.low)

    output = self.str_fn(data, width, height)
    self.update(output)

def __random_candlestick_data(size: int):
  data = {'date': [], 'open': [], 'close': [], 'high': [], 'low': []}

  for i in range(size):
    data['date'].append(datetime.now() + timedelta(minutes=i*5))
    data['open'].append(data['close'][i-1] if i > 0 else random.randrange(100, 1000))
    data['close'].append(data['open'][i] + random.randrange(-20, 20))
    data['high'].append(max(data['open'][i], data['close'][i]) + random.randrange(0, 20))
    data['low'].append(min(data['open'][i], data['close'][i]) - random.randrange(0, 20))

  return data

def candlestick(data: dict | None, width: int, height: int) -> str:
  if data == None:
    data = __random_candlestick_data(width // 3)

  fig = plt.figure
  fig.clear()
  fig.date("x").activate(form="%H:%M")
  signal = fig.candlestick(data)
  fig.draw(signal)
  fig.theme("__default__")
  fig.plot_size(width, height)
  return Text.from_ansi(fig.build().string())


def __random_linechart_data(size: int):
  data = {'date': [], 'value': []}

  for i in range(size):
    data['date'].append(datetime.now() + timedelta(minutes=i*5))
    data['value'].append(random.randrange(0, 200))

  return data

def linechart(data: dict | None, width: int, height: int) -> str:
  if data == None:
    data = __random_linechart_data(width // 5)

  fig = plt.figure
  fig.clear()
  fig.date('x').activate(form="%H:%M")
  signal = fig.signal(data["date"], data["value"]).lines()
  fig.draw(signal)
  fig.theme("__default__")
  fig.plot_size(width, height)
  return Text.from_ansi(fig.build().string())