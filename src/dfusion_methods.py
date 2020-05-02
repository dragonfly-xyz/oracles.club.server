import models.dfusion
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
Get all dfusion prices
'''
def get_dfusion_prices():
    dfusion_instance = db.session.query(models.dfusion.DfusionETH).order_by(models.dfusion.DfusionETH.blocknumber.desc()).limit(10)[-10:]
    dfusion_price = dfusion_instance[len(dfusion_instance) - 1].price
    dfusion_timestamp = dfusion_instance[len(dfusion_instance) - 1].timestamp
    dfusion_last_price = 0
    for instance in list(reversed(dfusion_instance)):
        if instance.price == dfusion_price:
            continue
        else:
            dfusion_last_price = instance.price
            break

    if dfusion_last_price == 0:
        dfusion_last_price = dfusion_price

    dfusion_btc_instance = db.session.query(models.dfusion.DfusionBTC).order_by(models.dfusion.DfusionBTC.blocknumber.desc()).limit(10)[-10:]
    dfusion_btc_price = dfusion_btc_instance[len(dfusion_btc_instance) - 1].price
    dfusion_btc_timestamp = dfusion_btc_instance[len(dfusion_btc_instance) - 1].timestamp
    dfusion_btc_last_price = 0
    for instance in list(reversed(dfusion_btc_instance)):
        if instance.price == dfusion_btc_price:
            continue
        else:
            dfusion_btc_last_price = instance.price
            break
    if dfusion_btc_last_price == 0:
        dfusion_btc_last_price = dfusion_btc_price


    return dfusion_price, dfusion_timestamp, dfusion_last_price, dfusion_btc_price, dfusion_btc_timestamp, dfusion_btc_last_price


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
Get latest DFusion Eth/USD price
'''
def get_dfusion_price():
    # Get latest block number
    block_number_request = get_latest_block_number()

    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address=0x6F400810b62df8E13fded51bE75fF5393eaa841F&topic0=0xafa5bc1fb80950b7cb2353ba0cf16a6d68de75801f2dac54b2dae9268450010a&apikey='.format(block_number_request) + api_key
    all = get(call)
    result = all['result']
    prices = []
    timestamp = 0
    eth_price = 0

    # This only pulls sells, we will need to pull buy orders in the future
    for event in result:
        if int(event['topics'][3], 16) == 1:
            if int(event['data'][:66], 16) == 4:
                sell_amt = int(event['data'][66:130], 16)
                buy_amt = int(event['data'][130:194], 16)

                price = buy_amt/sell_amt
                eth_price = price * pow(10, 12)
                if eth_price < 1:
                    eth_price = eth_price * pow(10, 8)

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if eth_price is not 0:
            prices.append(eth_price)
            f = open("dfusion.txt", "r")
            last_block = f.readline()
            f.close()

            if blockNum > int(last_block):
                os.remove('dfusion.txt')
                dfusion = models.dfusion.DfusionETH(timestamp=timestamp, blocknumber=blockNum, price=eth_price)
                db.session.add(dfusion)
                db.session.commit()

                # Write new file
                f = open("dfusion.txt", 'w')
                f.write('{}'.format(blockNum))
                f.close()

    if len(prices) > 1:
        return prices[-1], timestamp, prices[-2]


'''
Get latest DFusion BTC price
'''
def get_dfusion_btc_price():
    # Get latest block number
    block_number_request = get_latest_block_number() - 50000

    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address=0x6F400810b62df8E13fded51bE75fF5393eaa841F&topic0=0xafa5bc1fb80950b7cb2353ba0cf16a6d68de75801f2dac54b2dae9268450010a&topic3=0x0000000000000000000000000000000000000000000000000000000000000002&apikey='.format(block_number_request) + api_key
    call2 = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address=0x6F400810b62df8E13fded51bE75fF5393eaa841F&topic0=0xafa5bc1fb80950b7cb2353ba0cf16a6d68de75801f2dac54b2dae9268450010a&topic3=0x0000000000000000000000000000000000000000000000000000000000000003&apikey='.format(block_number_request) + api_key
    call3 = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address=0x6F400810b62df8E13fded51bE75fF5393eaa841F&topic0=0xafa5bc1fb80950b7cb2353ba0cf16a6d68de75801f2dac54b2dae9268450010a&topic3=0x0000000000000000000000000000000000000000000000000000000000000004&apikey='.format(block_number_request) + api_key
    call4 = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address=0x6F400810b62df8E13fded51bE75fF5393eaa841F&topic0=0xafa5bc1fb80950b7cb2353ba0cf16a6d68de75801f2dac54b2dae9268450010a&topic3=0x000000000000000000000000000000000000000000000000000000000000000b&apikey='.format(block_number_request) + api_key
    first = get(call)
    second = get(call2)
    third = get(call3)
    fourth = get(call4)
    result = first['result']
    for event in second['result']:
        result.append(event)
    for event in third['result']:
        result.append(event)
    for event in fourth['result']:
        result.append(event)

    prices = []
    timestamp = 0
    btc_price = 0

    # This only pulls sells, we will need to pull buy orders in the future
    for event in result:
        if int(event['topics'][3], 16) == 4 or int(event['topics'][3], 16) == 2 or int(event['topics'][3], 16) == 3:
            if int(event['data'][:66], 16) == 11:
                sell_amt = int(event['data'][66:130], 16) * pow(10, -6)
                buy_amt = int(event['data'][130:194], 16) * pow(10, -8)

                btc_price = sell_amt/buy_amt
        elif int(event['topics'][3], 16) == 11:
            if int(event['data'][:66], 16) == 4 or int(event['data'][:66], 16) == 2 or int(event['data'][:66], 16) == 3:
                buy_amt = int(event['data'][66:130], 16) * pow(10, -8)
                sell_amt = int(event['data'][130:194], 16) * pow(10, -6)

                btc_price = sell_amt/buy_amt

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if btc_price is not 0:
            prices.append(btc_price)
            f = open("dfusion_btc.txt", "r")
            last_block = f.readline()
            f.close()

            if blockNum > int(last_block):
                os.remove('dfusion_btc.txt')
                dfusion = models.dfusion.DfusionBTC(timestamp=timestamp, blocknumber=blockNum, price=btc_price)
                db.session.add(dfusion)
                db.session.commit()

                # Write new file
                f = open("dfusion_btc.txt", 'w')
                f.write('{}'.format(blockNum))
                f.close()

    if len(prices) > 1:
        return prices[-1], timestamp, prices[-2]


'''
Get latest DFusion BAT price
'''
def get_dfusion_bat_price():
    # Get latest block number
    block_number_request = get_latest_block_number() - 500000

    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address=0x6F400810b62df8E13fded51bE75fF5393eaa841F&topic0=0xafa5bc1fb80950b7cb2353ba0cf16a6d68de75801f2dac54b2dae9268450010a&topic3=0x0000000000000000000000000000000000000000000000000000000000000004&apikey='.format(block_number_request) + api_key
    all = get(call)
    result = all['result']
    prices = []
    timestamp = 0
    bat_price = 0

    # This only pulls sells, we will need to pull buy orders in the future
    for event in result:
        if int(event['topics'][3], 16) == 4:
            if int(event['data'][:66], 16) == 43:
                sell_amt = int(event['data'][66:130], 16)
                buy_amt = int(event['data'][130:194], 16)

                price = buy_amt/sell_amt
                bat_price = price * pow(10, 12)

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if bat_price is not 0:
            prices.append(bat_price)
            f = open("dfusion_bat.txt", "r")
            last_block = f.readline()
            f.close()

            if blockNum > int(last_block):
                os.remove('dfusion_bat.txt')
                dfusion = models.dfusion.DfusionBAT(timestamp=timestamp, blocknumber=blockNum, price=bat_price)
                db.session.add(dfusion)
                db.session.commit()

                # Write new file
                f = open("dfusion_bat.txt", 'w')
                f.write('{}'.format(blockNum))
                f.close()

    if len(prices) > 1:
        return prices[-1], timestamp, prices[-2]


'''
Get initial Dfusion data
'''
def get_dfusion_data(start_block, end_block):
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock={}&address=0x6F400810b62df8E13fded51bE75fF5393eaa841F&topic0=0xafa5bc1fb80950b7cb2353ba0cf16a6d68de75801f2dac54b2dae9268450010a&apikey='.format(start_block, end_block) + api_key
    all = get(call)
    result = all['result']
    eth_price = 0

    # This only pulls sells, we will need to pull buy orders in the future
    for event in result:
        if int(event['topics'][3], 16) == 1:
            if int(event['data'][:66], 16) == 4:
                sell_amt = int(event['data'][66:130], 16)
                buy_amt = int(event['data'][130:194], 16)

                price = buy_amt/sell_amt
                eth_price = price * pow(10, 12)
                if eth_price < 1:
                    eth_price = eth_price * pow(10, 8)

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if eth_price is not 0:
            # Insert into db
            link = models.dfusion.DfusionETH(timestamp=timestamp, blocknumber=blockNum, price=eth_price)
            db.session.add(link)
            db.session.commit()


'''
Get initial Dfusion data
'''
def get_dfusion_btc_data(start_block, end_block):
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock={}&address=0x6F400810b62df8E13fded51bE75fF5393eaa841F&topic0=0xafa5bc1fb80950b7cb2353ba0cf16a6d68de75801f2dac54b2dae9268450010a&topic3=0x0000000000000000000000000000000000000000000000000000000000000004&apikey='.format(start_block, end_block) + api_key
    all = get(call)
    result = all['result']
    btc_price = 0

    # This only pulls sells, we will need to pull buy orders in the future
    for event in result:
        if int(event['topics'][3], 16) == 4:
            if int(event['data'][:66], 16) == 11:
                sell_amt = int(event['data'][66:130], 16) * pow(10, -6)
                buy_amt = int(event['data'][130:194], 16) * pow(10, -8)

                btc_price = sell_amt/buy_amt

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if btc_price is not 0:
            # Insert into db
            link = models.dfusion.DfusionBTC(timestamp=timestamp, blocknumber=blockNum, price=btc_price)
            db.session.add(link)
            db.session.commit()


'''
Populate Dfusion
'''
def populate_dfusion():
    dfusion_start = 9340147
    dfusion_end = dfusion_start + 10000
    latest_block = get_latest_block_number() + 10000
    while dfusion_start < latest_block:
        if dfusion_end > latest_block:
            get_dfusion_data(start_block=dfusion_start, end_block='latest')
            get_dfusion_btc_data(start_block=dfusion_start, end_block='latest')
        else:
            get_dfusion_data(start_block=dfusion_start, end_block=dfusion_end)
            get_dfusion_btc_data(start_block=dfusion_start, end_block=dfusion_end)

        print(dfusion_end)
        dfusion_start = dfusion_end + 1
        dfusion_end = dfusion_end + 10000


'''
Create all dfusion latest block files
'''
def create_dfusion_files():
    f = open('dfusion.txt', "w")
    f.write('1')
    f.close()

    f = open('dfusion_btc.txt', "w")
    f.write('1')
    f.close()

    f = open('dfusion_bat.txt', "w")
    f.write('1')
    f.close()
