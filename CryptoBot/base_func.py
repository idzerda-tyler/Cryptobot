import urllib.parse
import hashlib
import hmac
import base64
import requests
import time
import json
from datetime import datetime

api_url = "https://api.binance.us"


def get_binanceus_signature(data, secret):
    postdata = urllib.parse.urlencode(data)
    message = postdata.encode()
    byte_key = bytes(secret, 'UTF-8')
    mac = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
    return mac

# Attaches auth headers and returns results of a POST request

def binanceus_request_get(uri_path, data, api_key, api_sec):
    headers = {}
    headers['X-MBX-APIKEY'] = api_key
    signature = get_binanceus_signature(data, api_sec)
    params={
        **data,
        "signature": signature,
        }
    req = requests.get((api_url + uri_path), params=params, headers=headers)
    return req.json()

def binanceus_request_post(uri_path, data, api_key, api_sec):
    headers = {}
    headers['X-MBX-APIKEY'] = api_key
    signature = get_binanceus_signature(data, api_sec)
    params={
        **data,
        "signature": signature,
        }
    req = requests.post((api_url + uri_path), params=params, headers=headers)
    return req.json()



def get_holdings(api_key, api_sec, symbol):
    uri_path = "/api/v3/account"
    crypto = symbol[:-3]
    currency = symbol[3:]

    data = {
        "timestamp": int(round(time.time() * 1000)),
    }
    x = binanceus_request_get(uri_path, data, api_key, api_sec)
    y = x['balances']
    t2 = list(filter(lambda x: x['asset'] == crypto, y))
    t1 = list(filter(lambda x: x['asset'] == currency, y))
    return t1,t2


def get_rate_limit(api_key, api_sec):
    #recvWindow = < recvWindow >
    uri_path = "/api/v3/rateLimit/order"
    data = {
        #"recvWindow": recvWindow,
        "timestamp": int(round(time.time() * 1000))
    }
    x = binanceus_request_get(uri_path,data,api_key,api_sec)
    return x

def post_order(symbol, side, type, quantity, api_key, api_sec):
    uri_path = "/api/v3/order/test" #add /test for testing
    data = {
        "symbol": symbol,
        "side": side,
        "type": type,
        "quantity": quantity,
        "timestamp": int(round(time.time() * 1000))
    }

    result = binanceus_request_post(uri_path, data, api_key, api_sec)
    return result

def get_price(symbol):
    resp = requests.get('https://api.binance.us/api/v3/ticker/price?symbol={}'.format(symbol)).json()
    price = round(float(resp['price']),4)
    return price


def sma(symbol,limit):
    avg = 0
    resp = requests.get('https://api.binance.us/api/v3/klines?symbol={}&interval=1m&limit={}'.format(symbol, limit)).json()
    for i in range(len(resp[1:])):
        avg += float(resp[i][4])
    avg /= len(resp)

    return(avg)

def sma_trend(symbol, limit1, limit2):
    #limit1 should be less than limit2
    if (sma(symbol, limit1)>sma(symbol, limit2)):
        return "Positive"
    elif (sma(symbol, limit1)<sma(symbol, limit2)):
        return "Negative"
    else:
        return "Neutral"

def sma_direction(old_limit, new_limit):
    if old_limit == 0:
        return new_limit,"start"
    elif new_limit<old_limit:
        return new_limit,"Down"
    elif new_limit>old_limit:
        return new_limit,"UP"
    elif new_limit == old_limit:
        return old_limit,"No change"

def timestamp():
    current_time = datetime.now()
    timestamp = current_time.timestamp()
    date_time = datetime.fromtimestamp(timestamp)
    str_time = date_time.strftime("%I%p %M:%S")
    return str_time

def sma_data(symbol, sma_limit1, sma_limit2, sma_small, sma_large):
    sma_small = sma_small
    sma_large = sma_large

    str_time = timestamp()
    sma7 = sma(symbol, sma_limit1)
    sma50 = sma(symbol, sma_limit2)

    sma_small, sma_direction_small = sma_direction(sma_small, sma7)
    sma_large, sma_direction_large = sma_direction(sma_large, sma50)

    print("Current timestamp", str_time, "SMA{}:".format(sma_limit1), sma7, "SMA{}:".format(sma_limit2), sma50)
    print("SMA7 DIRECTION :", sma_direction_small)
    print("SMA50 DIRECTION:", sma_direction_large)
    if sma7 > sma50:
        print("above")
        thing = 1
    elif sma7 < sma50:
        print("below")
        thing = 0
    else:
        print("same")
    return sma_small, sma_large, thing


def sma_test(symbol,limit):
    avg = 0
    resp = requests.get('https://api.binance.us/api/v3/klines?symbol={}&interval=1m&limit={}'.format(symbol, limit)).json()
    for i in range(len(resp)):
        print(float(resp[i][4]))



