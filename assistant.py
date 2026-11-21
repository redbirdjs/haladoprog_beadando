from transformers import AutoModelForCausalLM, AutoTokenizer
from trader_client import trading_client

# Agent létrehozva
# TODO: agent és prompt pontosítása, hogy csak a szükséges adatokat adja vissza az AI

model_name = "Qwen/Qwen2.5-0.5B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

SYSTEM_PROMPT = """

"""

prompt = f"""
I have no available buying power.
Here is my portfolio in Alpaca Positions format:
{trading_client.get_all_positions()}
"""
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

print(response)