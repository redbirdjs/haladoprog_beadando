from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, ContentSwitcher, Sparkline, Label, ListItem, ListView, Rule
from charts import Chart, candlestick, linechart
from trader_client import trading_client, portfolio_history

import random

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
      "current_price": item.current_price
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
                    yield Label(f"▲ ${float(self.account.portfolio_value):.2f}", classes="value up")
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
              yield Label("[b]Balance[/b][dim] - [i]Last 24h[/i][/dim]", classes="w-full text-center")
              yield Sparkline(portfolio_history.equity, summary_function=max, classes="h-full")

            with Container(id="stock-chart", classes="with-border h-full"):
              yield Label("[b]AAPL[/b] [dim]Apple - [i]Current price: $123.45[/i][/dim]", classes="w-full text-center")
              
              def update_chart(w, h):
                return candlestick(data=None, width=w, height=h)
              
              yield Chart(classes="h-full", get_chart_str=update_chart)
          
          with Vertical(id="right", classes="ml-1"):
            # yield Chart(classes="with-border h-full", get_chart_str=linechart)
            items = []
            for item in self.assets:
              items.append(
                ListItem(
                  Horizontal(
                    Label(f"[b]{item['symbol']}[/b] [dim]{item['name']}[/dim]", classes="w-full"),
                    Label(f"▲ ${item['current_price']}", classes="value up")
                  )
                )
              )

            yield ListView(
              *items,
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


if __name__ == "__main__":
  app = TheApp()
  app.run()