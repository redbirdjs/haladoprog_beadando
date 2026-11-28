```
pip install plotext rich textual alpaca-py transformers torch smolagents
```

CUDA torch letöltése:
```
pip install torch --index-url https://download.pytorch.org/whl/cu132
```

# Alpaca API kulcs beállítása:
A kulcs két részből áll.
```
api_key = ""
api_secret = ""
```
A kulcsot az Alpaca trading oldalán lehet igényelni. A projekt futtathatósága érdekében egy működő API kulcs van feltöltve. Ez a kulcs egy "paper trading" felhasználóhoz tartozik, amely **valós pénzt nem tartalmaz**, ezért még ha kompromitálódik is, nagy problémát nem tud okozni.

# Projekt elindítása:
```
py index.py
```