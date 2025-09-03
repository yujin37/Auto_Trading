import mojito
import json

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

key = config['API_KEY']
secret = config['SECRET_API_KEY']
acc_no = config["ACCOUNT_NO"]

broker = mojito.KoreaInvestment(
    api_key = key,
    api_secret = secret,
    acc_no = acc_no, 
    mock=True
)

#현재가 조회
resp = broker.fetch_price("005930")
#종목코드 조회
symbols = broker.fetch_symbols()
print(symbols)
