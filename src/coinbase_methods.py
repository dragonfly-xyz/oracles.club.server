import base64
import hashlib
import hmac
import models.coinbase
from models.create_db import db
import requests
from requests.auth import HTTPBasicAuth
from requests.auth import AuthBase
import os
import time

# API vars
api_key = os.environ.get('ETHERSCAN_API_KEY')
endpoint_base = 'https://api.etherscan.io/api'
headers = {'Content-Type': 'application/json'}

# API CALLS
def get(call):
    r = requests.get(call, auth=HTTPBasicAuth('', api_key), headers=headers)
    if check_err(r):
        return None
    return r.json()

def check_err(r):
    if r.status_code != 200:
        print(r.text)
        return True
    else:
        return False


'''
Get all coinbase prices
'''
def get_coinbase_prices():
    coinbase_instance = db.session.query(models.coinbase.CoinbaseETH).order_by(models.coinbase.CoinbaseETH.timestamp.desc()).limit(2)[-2:]
    coinbase_price = 0
    coinbase_timestamp = 0
    coinbase_last_price = 0
    if len(coinbase_instance) > 0:
        coinbase_last_price = coinbase_instance[0].price
        if len(coinbase_instance) > 1:
            coinbase_price = coinbase_instance[1].price
            coinbase_timestamp = coinbase_instance[1].timestamp

    coinbase_btc_instance = db.session.query(models.coinbase.CoinbaseBTC).order_by(models.coinbase.CoinbaseBTC.timestamp.desc()).limit(2)[-2:]
    coinbase_btc_price = 0
    coinbase_btc_timestamp = 0
    coinbase_btc_last_price = 0
    if len(coinbase_btc_instance) > 0:
        coinbase_btc_last_price = coinbase_btc_instance[0].price
        if len(coinbase_btc_instance) > 1:
            coinbase_btc_price = coinbase_btc_instance[1].price
            coinbase_btc_timestamp = coinbase_btc_instance[1].timestamp

    return coinbase_price, coinbase_timestamp, coinbase_last_price, coinbase_btc_price, coinbase_btc_timestamp, coinbase_btc_last_price


'''
Move to separate file
'''
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or b'').decode()
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode()

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request


'''
Get Coinbase current ETH Price
'''
def get_coinbase_price():
    api_url = 'https://api.pro.coinbase.com/'
    auth = CoinbaseExchangeAuth(os.environ.get('COINBASE_API_KEY'),
                                os.environ.get('COINBASE_SECRET_KEY'),
                                os.environ.get('COINBASE_PRIVATE_KEY'))
    r = requests.get(api_url + 'oracle', auth=auth).json()

    eth_price = r['prices']['ETH']
    timestamp = r['timestamp']

    f = open("coinbase.txt", "r")
    last_price = f.readline()
    f.close()
    if eth_price != float(last_price):
        os.remove('coinbase.txt')
        coinbase = models.coinbase.CoinbaseETH(timestamp=timestamp, price=eth_price)
        db.session.add(coinbase)
        db.session.commit()

        # Write new file
        print(eth_price)
        f = open("coinbase.txt", 'w')
        f.write('{}'.format(eth_price))
        f.close()

    return eth_price, timestamp


'''
Get Coinbase current BTC Price
'''
def get_coinbase_btc_price():
    api_url = 'https://api.pro.coinbase.com/'
    auth = CoinbaseExchangeAuth(os.environ.get('COINBASE_API_KEY'),
                                os.environ.get('COINBASE_SECRET_KEY'),
                                os.environ.get('COINBASE_PRIVATE_KEY'))
    r = requests.get(api_url + 'oracle', auth=auth).json()

    btc_price = r['prices']['BTC']
    timestamp = r['timestamp']

    f = open("coinbase_btc.txt", "r")
    last_price = f.readline()
    f.close()
    if btc_price != float(last_price):
        os.remove('coinbase_btc.txt')
        coinbase = models.coinbase.CoinbaseBTC(timestamp=timestamp, price=btc_price)
        db.session.add(coinbase)
        db.session.commit()
        print(btc_price)

        # Write new file
        f = open("coinbase_btc.txt", 'w')
        f.write('{}'.format(btc_price))
        f.close()

    return btc_price, timestamp


'''
Create all chainlink latest price files
'''
def create_coinbase_files():
    f = open('coinbae.txt', "w")
    f.write('1')
    f.close()

    f = open('coinbase_btc.txt', "w")
    f.write('1')
    f.close()
