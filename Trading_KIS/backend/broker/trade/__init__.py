from broker import acc_token, key, secret
headers = {
    "content-type": "application/json",
    "authorization": f"Bearer {acc_token}",
    "appkey": key,
    "appsecret": secret,
    "tr_id": "VTTC8434R",
    "custtype": "P"
    
}