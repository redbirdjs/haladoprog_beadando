from unittest import result

from transformers import AutoModelForCausalLM, AutoTokenizer
from smolagents import CodeAgent, WebSearchTool, VisitWebpageTool, TransformersModel
from trader_client import trading_client
import json
import re

# Agent létrehozva
# TODO: agent és prompt pontosítása, hogy csak a szükséges adatokat adja vissza az AI

model_name = "Qwen/Qwen3-4B-Instruct-2507"

model = TransformersModel(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)

tokenizer=AutoTokenizer.from_pretrained(model_name),

SYSTEM_PROMPT = """
You are an autonomous algorithmic trading decision agent. Your job is to analyze the user's current stock portfolio, available buying power, and real-time internet news to generate actionable trade orders.

### CORE DECISION LOGIC
1. **Analyze News & Catalysts:** Search for the latest financial news, earnings reports, macroeconomic shifts, and market sentiment affecting the user's holdings and major market movers.
2. **If Portfolio is NOT Empty:**
   - Evaluate each existing position against recent news and momentum.
   - Generate `sell` orders for holdings facing negative catalysts, deteriorating fundamentals, or overextended rallies where taking profit is prudent. Never sell more `qty` than the user currently owns.
   - Generate `buy` orders to average down on fundamentally strong dips, add to winners with fresh positive catalysts, or diversify sector risk.
   - Only give `buy` orders if there is enough buying power!
3. **If Portfolio IS Empty (`[]`):**
   - Identify high-conviction, profitable stock opportunities backed by strong recent news catalysts, earnings momentum, or favorable sector trends.
   - Generate `buy` orders only, sizing `qty` reasonably based on the provided `buying_power` (or conservative 1-10 share starter positions if cash balance is omitted).

### STRICT OUTPUT RULES
- Return **ONLY** a valid JSON array matching the exact schema below. DO NOT INCLUDE markdown formatting, explanations, or extra text.
- Generate a **maximum of 5 actions** (0 to 5 items). If no good trades exist, return `[]`.
- `symbol`: Valid uppercase stock ticker (e.g., `"NVDA"`, `"AAPL"`).
- `qty`: Positive number representing share quantity.
- `side`: Strictly `"buy"` or `"sell"`.
- `time_in_force`: Strictly one of `"day"`, `"gtc"`, `"opg"`, `"cls"`, `"ioc"`, `"fok"`.
- `reason`: A very short, single-sentence explanation (max 15-20 words) explaining why this trade makes sense based on the news or portfolio state.

### OUTPUT SCHEMA
[
  {
    "symbol": "string",
    "qty": 0,
    "side": "buy",
    "time_in_force": "day",
    "reason": "string"
  }
]
"""

"""
EXAMPLE PROMPT
The current buying power is 0$.
If my buying power can't afford the stocks, give me some sell options!
My portfolio positions are the following:
{trading_client.get_all_positions()}
"""

agent = CodeAgent(model=model, 
                  tools=[WebSearchTool(), VisitWebpageTool()], 
                  instructions=SYSTEM_PROMPT,
                  max_steps=6
                  )

def generate_answer():
    current_positions = trading_client.get_all_positions()
    prompt_positions = [{
        "symbol": pos.symbol,
        "qty": pos.qty,
        "qty_available": pos.qty_available,
        "current_price": pos.current_price,
        "change_today": pos.change_today
    } for pos in current_positions]

    prompt = f"""
    The current buying power is: $ {trading_client.get_account().buying_power}
    My portfolio is the following:
    {prompt_positions}

    Give me options what to buy or sell!
    Always try to suggest new opportunities, but only if there is enough buying power to afford it!
    Only and ONLY return a valid JSON array matching the exact schema in your instructions. Do not include markdown formatting, explanations, or extra text.
    """

    response = agent.run(prompt)
    
    # Ha az AI szöveget vagy markdownt ad vissza, átalakítjuk felhasználható formába
    if type(response) != list:
        markdown_cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.strip(), flags=re.IGNORECASE)
        suggestions_list = json.loads(markdown_cleaned)

        if len(suggestions_list) == 0:
            return []

        return suggestions_list

    return response