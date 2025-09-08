import requests
import json
from broker import acc_no
from broker.trade import headers
#매수 기능
balance_num, balance_code = acc_no.split('-')
order_cash_url = "/uapi/domestic-stock/v1/trading/order-cash"

#임의로 코드 설정, 프론트에서 입력 받을 계획
acc_pd_code = ""
pd_num = ""
order_type = ""
order_cnt = ""
order_price = ""
body = {
    "CANO": balance_num,
    "ACNT_PRDT_CD": acc_pd_code, #계좌 상품코드
    "PDNO": pd_num, #상품번호
    "ORD_DVSN": order_type, #주문 구분
    "ORD_QTY": order_cnt, #주문 수량
    "ORD_UNPR": order_price, #주문 단가, 시장가는 0으로 입력
    
}

URL_BASE = "https://openapivts.koreainvestment.com:29443"  # 모의투자 서버
URL = f"{URL_BASE}{order_cash_url}"

res = requests.post(URL, headers=headers, data=json.dumps(body))
data = res.json()



print(data)