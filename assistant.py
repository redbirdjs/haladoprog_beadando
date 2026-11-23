from transformers import AutoModelForCausalLM, AutoTokenizer
from trader_client import trading_client
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import OrderRequest
import json
import re

# Agent létrehozva
# TODO: agent és prompt pontosítása, hogy csak a szükséges adatokat adja vissza az AI

model_name = "Qwen/Qwen3-4B-Instruct-2507"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

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

def generate_answer(prompt: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    print(f"Response: {response}")

    markdown_cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.strip(), flags=re.IGNORECASE)
    suggestions_list = json.loads(markdown_cleaned)

    if len(suggestions_list) == 0:
        return []

    options = []
    for item in suggestions_list:
        options.append(OrderRequest(
            type="market",
            symbol=item['symbol'],
            qty=item['qty'],
            side=OrderSide.BUY if item['side'] == 'buy' else OrderSide.SELL,
            time_in_force=getTimeInForce(item['time_in_force'])
        ))

    return options

def getTimeInForce(tif):
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


prompt = f"""
The current buying power is: {trading_client.get_account().buying_power}
My portfolio is the following: {trading_client.get_all_positions()}

Give me some advice which stocks should I buy or sell!
"""
answer = generate_answer(prompt)
print(answer)