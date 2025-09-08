import json 
import requests
import os 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # broker 폴더 기준 상위
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)
#접근 토큰 발급    
def get_access_token():
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": key,
        "appsecret": secret
    }
    PATH = "oauth2/tokenP"
    URL = f"{config['URL_BASE']}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    ACCESS_TOKEN = res.json()["access_token"]
    return ACCESS_TOKEN

key = config['API_KEY']
secret = config['SECRET_API_KEY']
acc_no = config["ACCOUNT_NO"]

acc_token = get_access_token()
print(acc_token)