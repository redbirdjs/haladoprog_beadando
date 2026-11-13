from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, ContentSwitcher, Sparkline, Label, ListItem, ListView, Rule
from charts import Chart, candlestick, linechart

import random

class TheApp(App):
  CSS_PATH = "style.tcss"
  BINDINGS = [
    Binding(key="f1", action="switch_content('home')", description="Home"),
    Binding(key="f2", action="switch_content('something')", description="Something"),
    Binding(key="q", action="quit", description="Quit"),
  ]

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
                    yield Label("Balance: ")
                    yield Label(f"▲ ${24535.4:.2f}", classes="value up")
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
              yield Sparkline([random.randrange(0, 2000) for _ in range(24)], summary_function=max, classes="h-full")

            with Container(id="stock-chart", classes="with-border h-full"):
              yield Label("[b]AAPL[/b] [dim]Apple - [i]Current price: $123.45[/i][/dim]", classes="w-full text-center")
              yield Chart(classes="h-full", get_chart_str=candlestick)
          
          with Vertical(id="right", classes="ml-1"):
            # yield Chart(classes="with-border h-full", get_chart_str=linechart)
            yield ListView(
              ListItem(
                Horizontal(
                  Label("[b]AAPL[/b] [dim]Apple[/dim]", classes="w-full"),
                  Label(f"▲ ${235.4:.2f}", classes="value up")
                )
              ),
              ListItem(
                Horizontal(
                  Label("[b]MSFT[/b] [dim]Microsoft[/dim]", classes="w-full"),
                  Label(f"▼ ${235.4:.2f}", classes="value down")
                )
              ),
              ListItem(
                Horizontal(
                  Label("[b]NVDA[/b] [dim]NVIDIA[/dim]", classes="w-full"),
                  Label(f"▼ ${300:.2f}", classes="value down")
                )
              ),
              ListItem(
                Horizontal(
                  Label("[b]AMZN[/b] [dim]Amazon[/dim]", classes="w-full"),
                  Label(f"▲ ${300:.2f}", classes="value up")
                )
              ),
              ListItem(
                Horizontal(
                  Label("[b]TSLA[/b] [dim]Tesla[/dim]", classes="w-full"),
                  Label(f"▼ ${300:.2f}", classes="value down")
                )
              ),
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