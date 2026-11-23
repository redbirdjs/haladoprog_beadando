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
from textual.widgets import Header, Footer, ContentSwitcher, Sparkline, Label, ListItem, ListView, Button, SelectionList

from charts import Chart, candlestick
from trader_client import trading_client, portfolio_history, candle_data, market_data

from assistant import generate_answer


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
    Binding(key="f2", action="switch_content('ai_assistant')", description="AI Assistant"),
    Binding(key="q", action="quit", description="Quit"),
  ]

  account = trading_client.get_account()
  portfolio = trading_client.get_all_positions()
  assets = []
  ai_results = []

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
      # Home
      with Container(id="home"):
        with Horizontal(classes="horizontal-main"):
          
          with Vertical(id="left"):
            with Container(id="profile", classes="with-border h-full"):
              with Horizontal():
                with Vertical(classes="w-full ml-1"):
                  yield Label(f"Account number: {self.account.account_number}")
                  with Horizontal(classes="h-auto"):
                    yield Label("Portfolio value: ")
                    trend = get_trend(float(self.account.portfolio_value), float(portfolio_history.equity[0]))
                    yield Label(f"{indicator[trend]} [b]${float(self.account.portfolio_value):.2f}[/b]", classes=f"value {trend}".strip())
                  with Horizontal():
                    yield Button("AI Assistant", id="ai_assistant_button", variant="primary", flat=True)
                  with Horizontal():
                    yield Label(f"The market is currently {'open!' if market_data.is_open else '[u]closed![/u]'}")
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
            yield ListView(id="stock-list", classes="with-border h-full")

      # AI
      with Container(id="ai_assistant", classes="with-border w-full"):
        yield SelectionList[int](id="ai-check-list")
        yield Button("Buy/Sell", id="ai_assistant_buy_sell", variant="primary", flat=True)

  def on_mount(self) -> None:
    self.title = "Mambo App"
    self.sub_title = "Home"
    self.action_switch_content('home')

  def action_switch_content(self, page_name: str) -> None:
    self.query_one(ContentSwitcher).current = page_name
    self.sub_title = page_name.replace("_", " ").title()
    self.run_worker(self.update_page())

  async def update_page(self):
    page = self.query_one(ContentSwitcher).current

    if page == 'home':
      list_view = self.query_one("#stock-list", ListView)
      await list_view.clear()

      for item in self.assets:
        data = candle_data[item['symbol']]
        trend = get_trend(float(data[-1].close), float(data[-1].open))

        list_view.append(
          ListItem(
            Horizontal(
              Label(f"[b]{item['symbol'].ljust(4, " ")}[/b] [dim]{item['name']}[/dim]\n     [dim]Quantity: [/dim]{item['quantity']}", classes="w-full"),
              Label(f"{indicator[trend]} ${float(item['current_price']):.2f}", classes=f"value {trend}".strip())
            ),
            id=item['symbol']
          )
        )
      return

    if page == "ai_assistant":
      if len(self.ai_results) > 0:
        return

      self.ai_results = generate_answer()
      # self.ai_results = [
      #   {
      #     "symbol": "string",
      #     "qty": 0,
      #     "side": "buy",
      #     "time_in_force": "day",
      #     "reason": "string"
      #   }
      # ]

      selection_list = self.query_one("#ai-check-list", SelectionList)
      selection_list.clear_options()

      for index, item in enumerate(self.ai_results):
        selection_list.add_option((
          f"{item['symbol'].ljust(4, " ")} {item['side'].upper()}\tQuantity: {item['qty']}\tReason: {item['reason']}",
          index
        ))
      return

  def on_button_pressed(self, event: Button.Pressed) -> None:
    if event.button.id == "ai_assistant_button":
      self.action_switch_content('ai_assistant')
      return

    if event.button.id == "ai_assistant_buy_sell":
      self.action_buy_sell_stocks()
      return

  def action_buy_sell_stocks(self) -> None:
    selection_list = self.query_one("#ai-check-list", SelectionList)
    with open("debug.txt", "w") as file:
      for index in selection_list.selected:
        file.write(self.ai_results[index].__str__())
        file.write("\n")

    self.ai_results = []
    self.action_switch_content('home')

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