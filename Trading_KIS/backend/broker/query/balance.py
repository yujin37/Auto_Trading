from broker import acc_no
from broker.query import headers
import requests
import json
#잔고 조회
balance_num, balance_code = acc_no.split('-')

balance_url = "/uapi/domestic-stock/v1/trading/inquire-balance"


body = {
    "CANO": balance_num,
    "ACNT_PRDT_CD": "01",
    "AFHR_FLPR_YN": "N",
    "INQR_DVSN": "02",
    "UNPR_DVSN": "01",
    "FUND_STTL_ICLD_YN": "N",
    "FNCG_AMT_AUTO_RDPT_YN": "N",
    "PRCS_DVSN": "01",
    "OFL_YN": "",
    "CTX_AREA_FK100": "",
    "CTX_AREA_NK100": ""
    
}
URL_BASE = "https://openapivts.koreainvestment.com:29443"  # 모의투자 서버
URL = f"{URL_BASE}{balance_url}"

res = requests.get(URL, headers=headers, params=body)
data = res.json()

print("rt_cd:", data.get("rt_cd"))