import threading
from textual.app import App, ComposeResult
from textual.widgets import LoadingIndicator

print("\033[H\033[J", end="")

class LoadingApp(App):
  def compose(self) -> ComposeResult:
    yield LoadingIndicator()

loading_app = None
loading_app_thread = None
if __name__ == "__main__":
  loading_app = LoadingApp()
  loading_app_thread = threading.Thread(
    target=loading_app.run,
    daemon=True
  )
  loading_app_thread.start()


from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, ContentSwitcher, Sparkline, Label, ListItem, ListView

from charts import Chart, candlestick
from trader_client import trading_client, portfolio_history, candle_data


indicator = {
  'up': '▲',
  'down': '▼',
  '': '—'
}

def get_trend(current: float, previous: float):
  if current > previous:
    return 'up'
  if current < previous:
    return 'down'
  return ''


class TheApp(App):
  CSS_PATH = "style.tcss"
  BINDINGS = [
    Binding(key="f1", action="switch_content('home')", description="Home"),
    Binding(key="f2", action="switch_content('something')", description="Something"),
    Binding(key="q", action="quit", description="Quit"),
  ]

  account = trading_client.get_account()
  portfolio = trading_client.get_all_positions()
  assets = []

  for item in portfolio:
    data = trading_client.get_asset(item.symbol)
    
    assets.append({
      "symbol": item.symbol,
      "name": data.name,
      "current_price": item.current_price,
      "quantity": item.qty
    })

  def compose(self) -> ComposeResult:
    yield Header()
    yield Footer()

    with ContentSwitcher(initial="home"):
      # First Content
      with Container(id="home"):
        with Horizontal(classes="horizontal-main"):
          
          with Vertical(id="left"):
            with Container(id="profile", classes="with-border h-full"):
              with Horizontal():
                with Vertical(classes="w-full ml-1"):
                  yield Label("Name")
                  with Horizontal():
                    yield Label("Portfolio value: ")
                    trend = get_trend(float(self.account.portfolio_value), float(portfolio_history.equity[0]))
                    yield Label(f"{indicator[trend]} [b]${float(self.account.portfolio_value):.2f}[/b]", classes=f"value {trend}".strip())
                with Vertical(classes="w-auto mr-1"):
                  yield Label("      ::::::::      ")
                  yield Label("   ::::::::::::::   ")
                  yield Label(" :::::::::  ::::::: ")
                  yield Label(":::::::      :::::::")
                  yield Label(":::::   :    :::::::")
                  yield Label("::::::       :::::::")
                  yield Label("::::::::     :::::::")
                  yield Label(" ::::::      :::::: ")
                  yield Label("  :::::      ::::   ")
                  yield Label("     ::      ::     ")
              yield Label(f"[b]Balance[/b][dim] - [i]Last 24h[/i][/dim]", classes="w-full text-center")
              yield Sparkline(portfolio_history.equity, summary_function=max, classes="h-full")

            with Container(id="stock-chart-container", classes="with-border h-full"):
              yield Label(id="stock-title", classes="w-full text-center", content="")
              yield Chart(id="stock-chart", classes="h-full", data=None, get_chart_str=candlestick)
          
          with Vertical(id="right", classes="ml-1"):
            items = []
            for item in self.assets:
              data = candle_data[item['symbol']]
              trend = get_trend(float(data[-1].close), float(data[-1].open))

              items.append(
                ListItem(
                  Horizontal(
                    Label(f"[b]{item['symbol'].ljust(4, " ")}[/b] [dim]{item['name']}[/dim]\n     [dim]Quantity: [/dim]{item['quantity']}", classes="w-full"),
                    Label(f"{indicator[trend]} ${float(item['current_price']):.2f}", classes=f"value {trend}".strip())
                  ),
                  id=item['symbol']
                )
              )

            yield ListView(
              *items,
              id="stock-list",
              classes="with-border h-full"
            )

      # Second Content
      yield Static("Something", id="something", classes="content_box")

  def on_mount(self) -> None:
    self.title = "Mambo App"
    self.sub_title = "Home"

  def action_switch_content(self, page_name: str) -> None:
    self.query_one(ContentSwitcher).current = page_name
    self.sub_title = page_name.title()

  def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
    if event.list_view.id != "stock-list":
      return

    title = self.query_one("#stock-title")
    asset = next((x for x in self.assets if x["symbol"] == event.item.id), None)
    title.content = f"[b]{asset['symbol']}[/b] [dim]{asset['name']} - [i]Current price: ${asset['current_price']}[/i][/dim]"

    chart = self.query_one("#stock-chart")
    chart.data = candle_data[event.item.id]

    chart.refresh_chart()


if __name__ == "__main__":
  app = TheApp()
  loading_app.exit()
  loading_app_thread.join()
  app.run()