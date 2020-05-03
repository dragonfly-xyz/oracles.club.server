import models.uniswap
from models.create_db import db
import requests
from requests.auth import HTTPBasicAuth
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
Get all Uniswap pairs
'''
def get_uniswap_prices():
    uniswap_instance = db.session.query(models.uniswap.UniswapETH).order_by(models.uniswap.UniswapETH.blocknumber.desc()).limit(10)[-10:]
    uniswap_price = uniswap_instance[0].price
    uniswap_timestamp = uniswap_instance[0].timestamp
    uniswap_last_price = 0
    for instance in list(uniswap_instance):
        if instance.price == uniswap_price:
            continue
        else:
            uniswap_last_price = instance.price
            break
    if uniswap_last_price == 0:
        uniswap_last_price = uniswap_price

    uniswap_btc_instance = db.session.query(models.uniswap.UniswapBTC).order_by(models.uniswap.UniswapBTC.blocknumber.desc()).limit(10)[-10:]
    uniswap_btc_price = uniswap_btc_instance[0].price
    uniswap_btc_timestamp = uniswap_btc_instance[0].timestamp
    uniswap_btc_last_price = 0
    for instance in list(uniswap_btc_instance):
        if instance.price == uniswap_btc_price:
            continue
        else:
            uniswap_btc_last_price = instance.price
            break
    if uniswap_btc_last_price == 0:
        uniswap_btc_last_price = uniswap_btc_price

    uniswap_bat_instance = db.session.query(models.uniswap.UniswapBAT).order_by(models.uniswap.UniswapBAT.blocknumber.desc()).limit(10)[-10:]
    uniswap_bat_price = float(uniswap_bat_instance[0].price)
    uniswap_bat_timestamp = uniswap_bat_instance[0].timestamp
    uniswap_bat_last_price = 0
    for instance in list(uniswap_bat_instance):
        if instance.price == uniswap_bat_price:
            continue
        else:
            uniswap_bat_last_price = float(instance.price)
            break

    if uniswap_bat_last_price == 0:
        uniswap_bat_last_price = uniswap_bat_price

    return uniswap_price, uniswap_timestamp, uniswap_last_price, uniswap_btc_price, uniswap_btc_timestamp, uniswap_btc_last_price, uniswap_bat_price, uniswap_bat_timestamp, uniswap_bat_last_price


'''
Get latest block number
'''
def get_latest_block_number():
    global api_key
    while api_key is None:
        print('latest')
        api_key = os.environ.get('ETHERSCAN_API_KEY')

    block_num_call = endpoint_base + '?module=proxy&action=eth_blockNumber&apikey=' + api_key
    block_result = get(block_num_call)
    if block_result is None:
        time.sleep(1)
        get_latest_block_number()

    block_number = int(block_result['result'], 16)
    block_number_request = block_number - 10000

    return block_number_request


'''
Get latest Uniswap price
'''
def get_uniswap_price():
    # Get latest block number
    call = endpoint_base + '?module=account&action=tokenbalance&contractaddress=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48&address=0x97deC872013f6B5fB443861090ad931542878126&tag=latest&apikey=' + api_key
    all = get(call)
    usdc_amt = int(all['result']) * pow(10, -6)

    call2 = endpoint_base + '?module=account&action=balance&address=0x97deC872013f6B5fB443861090ad931542878126&tag=latest&apikey=' + api_key
    all2 = get(call2)
    eth_amt = int(all2['result']) * pow(10, -18)

    eth_usd_price = usdc_amt/eth_amt
    block_number = get_latest_block_number()

    # Write to DB
    uniswap = models.uniswap.UniswapETH(timestamp=int(time.time()), blocknumber=block_number, price=eth_usd_price)
    db.session.add(uniswap)
    db.session.commit()
    return eth_usd_price


'''
Get latest Uniswap BTC price
'''
def get_uniswap_btc_price(eth_price):
    # Get latest block number
    call = endpoint_base + '?module=account&action=tokenbalance&contractaddress=0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599&address=0x4d2f5cFbA55AE412221182D8475bC85799A5644b&tag=latest&apikey=' + api_key
    all = get(call)
    btc_amt = int(all['result']) * pow(10, -8)

    call2 = endpoint_base + '?module=account&action=balance&address=0x4d2f5cFbA55AE412221182D8475bC85799A5644b&tag=latest&apikey=' + api_key
    all2 = get(call2)
    eth_amt = int(all2['result']) * pow(10, -18)

    btc_eth_price = eth_amt/btc_amt
    btc_usd_price = btc_eth_price * eth_price
    block_number = get_latest_block_number()

    # Write to DB
    uniswap = models.uniswap.UniswapBTC(timestamp=int(time.time()), blocknumber=block_number, price=btc_usd_price)
    db.session.add(uniswap)
    db.session.commit()
    return btc_usd_price


'''
Get latest Uniswap BTC price
'''
def get_uniswap_bat_price(eth_price):
    # Get latest block number
    call = endpoint_base + '?module=account&action=tokenbalance&contractaddress=0x0d8775f648430679a709e98d2b0cb6250d2887ef&address=0x2E642b8D59B45a1D8c5aEf716A84FF44ea665914&tag=latest&apikey=' + api_key
    all = get(call)
    bat_amt = int(all['result']) * pow(10, -18)

    call2 = endpoint_base + '?module=account&action=balance&address=0x2E642b8D59B45a1D8c5aEf716A84FF44ea665914&tag=latest&apikey=' + api_key
    all2 = get(call2)
    eth_amt = int(all2['result']) * pow(10, -18)

    bat_eth_price = eth_amt/bat_amt
    bat_usd_price = bat_eth_price * eth_price
    block_number = get_latest_block_number()

    # Write to DB
    uniswap = models.uniswap.UniswapBAT(timestamp=int(time.time()), blocknumber=block_number, price=bat_usd_price)
    db.session.add(uniswap)
    db.session.commit()
    return bat_usd_price


'''
Populate all uniswap tables
'''
# TODO: consider redoing with Etherscan, using e.g. Ivan's code on Telegram
def populate_all_uniswap_tables(usdc_block_number, btc_block_number, bat_block_number, latest_block):
    usdc_url = 'https://api.aleth.io/v1' + '/ether-balances/0x97deC872013f6B5fB443861090ad931542878126?block={}'
    start = usdc_block_number+1
    while start < latest_block:
        request = usdc_url.format(start)
        response = requests.get(request, auth=HTTPBasicAuth('', os.environ.get('ALETHIO_API_KEY')), headers=headers).json()
        if 'data' not in response:
            break
        eth_balance = int(response['data']['attributes']['balance']) * pow(10, -18)

        # Get token balance
        token_usdc_url = 'https://api.aleth.io/v1/token-balances?block={}&filter[token]={}&filter[account]={}'.format(start, '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', '0x97deC872013f6B5fB443861090ad931542878126')
        token_response = requests.get(token_usdc_url, auth=HTTPBasicAuth('', os.environ.get('ALETHIO_API_KEY')), headers=headers).json()
        if 'data' not in token_response:
            break
        data = token_response['data'][0]['attributes']['balance']
        if data is None:
            start = start + 10000
            continue

        token_balance = int(token_response['data'][0]['attributes']['balance']) * pow(10, -6)
        eth_usd_price = token_balance / eth_balance

        # Write to DB
        uniswap = models.uniswap.UniswapETH(timestamp=int(time.time()), blocknumber=start, price=eth_usd_price)
        db.session.add(uniswap)
        db.session.commit()
        start = start + 10000

    start = btc_block_number + 1
    btc_url = 'https://api.aleth.io/v1' + '/ether-balances/0x4d2f5cFbA55AE412221182D8475bC85799A5644b?block={}'
    while start < latest_block:
        request = btc_url.format(start)
        response = requests.get(request, auth=HTTPBasicAuth('', os.environ.get('ALETHIO_API_KEY')), headers=headers).json()
        if 'data' not in response:
            break
        eth_balance = int(response['data']['attributes']['balance']) * pow(10, -18)

        # Get token balance
        token_wbtc_url = 'https://api.aleth.io/v1/token-balances?block={}&filter[token]={}&filter[account]={}'.format(start, '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599', '0x4d2f5cFbA55AE412221182D8475bC85799A5644b')
        token_response = requests.get(token_wbtc_url, auth=HTTPBasicAuth('', os.environ.get('ALETHIO_API_KEY')), headers=headers).json()
        if 'data' not in token_response:
            break
        data = token_response['data'][0]['attributes']['balance']
        if data is None:
            start = start + 10000
            continue

        token_balance = int(token_response['data'][0]['attributes']['balance']) * pow(10, -8)
        eth_btc_price = eth_balance / token_balance

        # Get eth price
        eth_instance = db.session.query(models.compound.CompoundETH).order_by(models.compound.CompoundETH.blocknumber.desc()).filter(
            models.compound.CompoundETH.blocknumber <= start).limit(1)
        eth_price = 100
        if len(eth_instance[:]) == 0:
            eth_instance = db.session.query(models.compound.CompoundETH).order_by(models.compound.CompoundETH.blocknumber.desc()).filter(
                models.compound.CompoundETH.blocknumber <= (start + 100000)).limit(1)
            if len(eth_instance[:]) == 0:
                eth_price = 100
            else:
                eth_price = eth_instance[0].price
        else:
            eth_price = eth_instance[0].price
        btc_usd_price = eth_btc_price * eth_price
        print(btc_usd_price)

        # Write to DB
        uniswap = models.uniswap.UniswapBTC(timestamp=int(time.time()), blocknumber=start, price=btc_usd_price)
        db.session.add(uniswap)
        db.session.commit()
        start = start + 10000

    start = bat_block_number + 1
    bat_url = 'https://api.aleth.io/v1' + '/ether-balances/0x2E642b8D59B45a1D8c5aEf716A84FF44ea665914?block={}'
    while start < latest_block:
        request = bat_url.format(start)
        response = requests.get(request, auth=HTTPBasicAuth('', os.environ.get('ALETHIO_API_KEY')), headers=headers).json()
        if 'data' not in response:
            break
        eth_balance = int(response['data']['attributes']['balance']) * pow(10, -18)

        # Get token balance
        token_bat_url = 'https://api.aleth.io/v1/token-balances?block={}&filter[token]={}&filter[account]={}'.format(start, '0x0d8775f648430679a709e98d2b0cb6250d2887ef', '0x2E642b8D59B45a1D8c5aEf716A84FF44ea665914')
        token_response = requests.get(token_bat_url, auth=HTTPBasicAuth('', os.environ.get('ALETHIO_API_KEY')), headers=headers).json()
        if 'data' not in token_response:
            break
        data = token_response['data'][0]['attributes']['balance']
        if data is None:
            start = start + 10000
            continue

        token_balance = int(token_response['data'][0]['attributes']['balance']) * pow(10, -18)
        eth_bat_price = eth_balance / token_balance

        # Get eth price
        eth_instance = db.session.query(models.compound.CompoundETH).order_by(models.compound.CompoundETH.blocknumber.desc()).filter(
            models.compound.CompoundETH.blocknumber <= start).limit(1)
        eth_price = 100
        if len(eth_instance[:]) == 0:
            eth_instance = db.session.query(models.compound.CompoundETH).order_by(models.compound.CompoundETH.blocknumber.desc()).filter(
                models.compound.CompoundETH.blocknumber <= (start + 100000)).limit(1)
            if len(eth_instance[:]) == 0:
                eth_price = 100
            else:
                eth_price = eth_instance[0].price
        else:
            eth_price = eth_instance[0].price
        bat_usd_price = eth_bat_price * eth_price
        print(bat_usd_price)

        # Write to DB
        uniswap = models.uniswap.UniswapBAT(timestamp=int(time.time()), blocknumber=start, price=bat_usd_price)
        db.session.add(uniswap)
        db.session.commit()
        start = start + 10000


'''
Populate Uniswap
'''
def populate_uniswap():
    uniswap_start_usdc = 6783192
    uniswap_start_bat = 6660894
    uniswap_start_btc = 7004537
    latest_block = get_latest_block_number() + 9000

    populate_all_uniswap_tables(uniswap_start_usdc, uniswap_start_btc, uniswap_start_bat, latest_block)


'''
Create all uniswap latest block files
'''
def create_uniswap_files():
    f = open('uniswap.txt', "w")
    f.write('1')
    f.close()

    f = open('uniswap_btc.txt', "w")
    f.write('1')
    f.close()

    f = open('uniswap_bat.txt', "w")
    f.write('1')
    f.close()
