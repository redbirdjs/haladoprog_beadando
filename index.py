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
from trader_client import trading_client, get_portfolio_history, get_candle_chart, get_market_clock, send_orders

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
    Binding(key="r", action="refresh_content()", description="Refresh"),
    Binding(key="q", action="quit", description="Quit"),
  ]

  account = trading_client.get_account()
  portfolio = trading_client.get_all_positions()
  portfolio_history = get_portfolio_history()
  market_clock = get_market_clock()
  candle_data = get_candle_chart()
  index = 0

  assets = []
  ai_results = []

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
                    trend = get_trend(float(self.account.portfolio_value), float(self.portfolio_history.equity[0]))
                    yield Label(f"{indicator[trend]} [b]${float(self.account.portfolio_value):.2f}[/b]", id="portfolio-value", classes=f"value {trend}".strip())
                  with Horizontal():
                    yield Button("AI Assistant", id="ai_assistant_button", variant="primary", flat=True)
                  with Horizontal():
                    yield Label(f"The market is currently {'open!' if self.market_clock.is_open else '[u]closed![/u]'}", id="market-status")
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
              yield Sparkline(self.portfolio_history.equity, summary_function=max, classes="h-full")

            with Container(id="stock-chart-container", classes="with-border h-full"):
              yield Label(id="stock-title", classes="w-full text-center", content="")
              yield Chart(id="stock-chart", classes="h-full", data=None, get_chart_str=candlestick)
          
          with Vertical(id="right", classes="ml-1"):
            yield ListView(
              ListItem(Label("Loading...", classes="ml-1"), disabled=True),
              id="stock-list", classes="with-border h-full"
            )

      # AI
      with Vertical(id="ai_assistant", classes="with-border w-full h-full"):
        with Horizontal(classes="h-auto mx-1"):
          with Vertical(classes="w-full h-auto"):
            yield Label("AI Ultra Mambo Assistant")
          with Vertical(classes="w-auto h-auto color-ascii"):
            yield Label("⠀⠀⠀⢀⣾⣧⠀⠀⠀⢠⣾⣆⠀⠀⠀")
            yield Label("⠀⠀⠀⣼⣿⣿⣇⠀⠀⣾⣿⣿⡄⠀⠀")
            yield Label("⠀⠀⢠⣿⣿⣿⣿⣤⣴⣿⣿⣿⡇⠀⠀")
            yield Label("⠀⠀⢸⣿⡿⠛⠻⣿⣿⡿⡻⣿⡟⠀⠀")
            yield Label("⠀⠀⢸⣿⣇⡄⢷⣿⣿⡸⠇⣸⣷⠀⠀")
            yield Label("⠐⣒⣞⢿⣿⣿⣿⣿⣿⣿⣿⣿⠯⠭⣁")
            yield Label("⠀⠐⠚⠉⠉⣿⣿⣿⣿⣿⠋⠉⠉⠒⠀")
            yield Label("⠀⠀⠀⠀⣸⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀")
            yield Label("⠀⠀⠀⣰⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀")
            yield Label("⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀")
        yield SelectionList[int](id="ai-check-list", classes="with-border h-auto")
        with Horizontal(classes="h-auto"):
          yield Button("Execute orders", id="ai_assistant_buy_sell", variant="primary", flat=True, classes="ml-2")
          yield Button("Re-run", id="ai_assistant_rerun", variant="default", flat=True, classes="ml-1")

  def on_mount(self) -> None:
    self.title = "Mambo App"
    self.sub_title = "Home"
    self.action_switch_content('home')

  def action_switch_content(self, page_name: str) -> None:
    self.query_one(ContentSwitcher).current = page_name
    self.sub_title = page_name.replace("_", " ").title()
    self.run_worker(self.update_page(page_name))

  def action_refresh_content(self) -> None:
    page_name = self.query_one(ContentSwitcher).current
    self.run_worker(self.update_page(page_name))

  async def update_page(self, page):
    if page == "home":
      self.call_after_refresh(lambda: self.update_home_data())
      return

    if page == "ai_assistant":
      if len(self.ai_results) > 0:
        return

      selection_list = self.query_one("#ai-check-list", SelectionList)
      selection_list.clear_options()
      selection_list.border_title = "The AI is currently generating the options..."
      
      self.call_after_refresh(lambda: self.update_ai_answer())
      return

  async def update_home_data(self):
    self.account = trading_client.get_account()
    self.portfolio = trading_client.get_all_positions()
    self.portfolio_history = get_portfolio_history()
    self.market_clock = get_market_clock()
    self.candle_data = get_candle_chart()


    # Portfolio Value
    portfolio_value_label = self.query_one("#portfolio-value", Label)
    trend = get_trend(float(self.account.portfolio_value), float(self.portfolio_history.equity[0]))
    portfolio_value_label.content = f"{indicator[trend]} [b]${float(self.account.portfolio_value):.2f}[/b]"


    # Balance Chart
    sparkline = self.query_one("#portfolio-sparkline", Sparkline)
    sparkline.data = self.portfolio_history.equity


    # Market Label
    market_label = self.query_one("#market-status", Label)
    market_label.content = f"The market is currently {'open!' if self.market_clock.is_open else '[u]closed![/u]'}"


    # Stock List
    list_view = self.query_one("#stock-list", ListView)
    await list_view.clear()

    self.assets = []
    for item in self.portfolio:
      data = trading_client.get_asset(item.symbol)
      
      self.assets.append({
        "symbol": item.symbol,
        "name": data.name,
        "current_price": item.current_price,
        "quantity": item.qty
      })

    for item in self.assets:
      data = self.candle_data[item['symbol']]
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

  async def update_ai_answer(self):
    selection_list = self.query_one("#ai-check-list", SelectionList)
    selection_list.clear_options()

    # self.ai_results = []
    self.ai_results = generate_answer()

    if len(self.ai_results) == 0:
      selection_list.border_title = "No results."
      return

    success_color = self.app.theme_variables["success"]
    error_color = self.app.theme_variables["error"]

    max_qty_len = max([len(str(x['qty'])) for x in self.ai_results])

    from rich.text import Text
    for index, item in enumerate(self.ai_results):
      color = success_color if item['side'] == 'buy' else error_color
      selection_list.add_option((
        Text.from_markup(f"[b]{item['symbol'].ljust(4, " ")} [{color}]{item['side'].upper().ljust(4, " ")}[/{color}][/b] {" "*4} [dim]Quantity: [/dim]{str(item['qty']).rjust(max_qty_len, " ")} {" "*4} [dim]Reason: [i]{item['reason']}[/i][/dim]"),
        index
      ))

    selection_list.border_title = "Available options"

  def on_button_pressed(self, event: Button.Pressed) -> None:
    if event.button.id == "ai_assistant_button":
      self.action_switch_content('ai_assistant')
      return

    if event.button.id == "ai_assistant_buy_sell":
      self.action_buy_sell_stocks()
      return

    if event.button.id == "ai_assistant_rerun":
      self.ai_results = []
      self.action_refresh_content()
      return

  def action_buy_sell_stocks(self) -> None:
    selection_list = self.query_one("#ai-check-list", SelectionList)
    selected_items = [self.ai_results[index] for index in selection_list.selected]
    send_orders(selected_items)

    self.ai_results = []
    self.action_switch_content('home')

  def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
    if event.item == None or event.list_view.id != "stock-list":
      return

    title = self.query_one("#stock-title")
    asset = next((x for x in self.assets if x["symbol"] == event.item.id), None)
    if asset == None: 
      return

    title.content = f"[b]{asset['symbol']}[/b] [dim]{asset['name']} - [i]Current price: ${asset['current_price']}[/i][/dim]"

    chart = self.query_one("#stock-chart")
    chart.data = self.candle_data[event.item.id]

    chart.refresh_chart()


if __name__ == "__main__":
  app = TheApp()
  loading_app.exit()
  loading_app_thread.join()
  app.run()