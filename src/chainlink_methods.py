import models.chainlink
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
Get all Chainlink price pairs
'''
def get_chainlink_prices():
    chainlink_instance = db.session.query(models.chainlink.ChainlinkETH).order_by(models.chainlink.ChainlinkETH.blocknumber.desc()).limit(2)[-2:]
    chainlink_price = chainlink_instance[1].price
    chainlink_timestamp = chainlink_instance[1].timestamp
    chainlink_last_price = chainlink_instance[0].price

    chainlink_btc_instance = db.session.query(models.chainlink.ChainlinkBTC).order_by(models.chainlink.ChainlinkBTC.blocknumber.desc()).limit(2)[-2:]
    chainlink_btc_price = chainlink_btc_instance[1].price
    chainlink_btc_timestamp = chainlink_btc_instance[1].timestamp
    chainlink_btc_last_price = chainlink_btc_instance[0].price

    chainlink_bat_instance = db.session.query(models.chainlink.ChainlinkBAT).order_by(models.chainlink.ChainlinkBAT.blocknumber.desc()).limit(2)[-2:]
    chainlink_bat_price = float(chainlink_bat_instance[1].price)
    chainlink_bat_timestamp = chainlink_bat_instance[1].timestamp
    chainlink_bat_last_price = float(chainlink_bat_instance[0].price)

    return chainlink_price, chainlink_timestamp, chainlink_last_price, chainlink_btc_price, chainlink_btc_timestamp, chainlink_btc_last_price, chainlink_bat_price, chainlink_bat_timestamp, chainlink_bat_last_price


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
Get latest chainlink price.
'''
def get_chainlink_price():
    # Get latest block number
    block_number_request = get_latest_block_number()

    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address=0xF79D6aFBb6dA890132F9D7c355e3015f15F3406F&topic0=0x0559884fd3a460db3073b7fc896cc77986f16e378210ded43186175bf646fc5f&apikey='.format(block_number_request) + api_key
    all = get(call)
    if all is None:
        chainlink_instance = db.session.query(models.chainlink.ChainlinkETH).order_by(models.chainlink.ChainlinkETH.blocknumber)[-2:]
        chainlink_price = chainlink_instance[1].price
        chainlink_timestamp = chainlink_instance[1].timestamp
        chainlink_last_price = chainlink_instance[0].price

        return chainlink_price, chainlink_timestamp, chainlink_last_price

    result = all['result']
    chainlink_prices = []
    timestamp = 0
    for event in result:
        number = event['topics'][1]
        eth_price = int(number, 16)

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if eth_price is not 0:
            updated_price = eth_price * pow(10, -8)
            chainlink_prices.append(updated_price)

            f = open("chainlink.txt", "r")
            last_block = f.readline()
            f.close()

            if blockNum > int(last_block):
                os.remove('chainlink.txt')
                chainlink = models.chainlink.ChainlinkETH(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
                db.session.add(chainlink)
                db.session.commit()

                # Write new file
                f = open("chainlink.txt", 'w')
                f.write('{}'.format(blockNum))
                f.close()

    if len(chainlink_prices) > 1:
        return chainlink_prices[-1], timestamp, chainlink_prices[-2]


'''
Get latest chainlink BTC price.
'''
def get_chainlink_btc_price():
    # Get latest block number
    block_number_request = get_latest_block_number()

    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address=0xF5fff180082d6017036B771bA883025c654BC935&topic0=0x0559884fd3a460db3073b7fc896cc77986f16e378210ded43186175bf646fc5f&apikey='.format(block_number_request) + api_key
    all = get(call)
    if all is None:
        chainlink_instance = db.session.query(models.chainlink.ChainlinkBTC).order_by(models.chainlink.ChainlinkBTC.blocknumber)[-2:]
        chainlink_price = chainlink_instance[1].price
        chainlink_timestamp = chainlink_instance[1].timestamp
        chainlink_last_price = chainlink_instance[0].price

        return chainlink_price, chainlink_timestamp, chainlink_last_price

    result = all['result']
    chainlink_prices = []
    timestamp = 0
    for event in result:
        number = event['topics'][1]
        btc_price = int(number, 16)

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if btc_price is not 0:
            updated_price = btc_price * pow(10, -8)
            chainlink_prices.append(updated_price)

            f = open("chainlink_btc.txt", "r")
            last_block = f.readline()
            f.close()

            if blockNum > int(last_block):
                os.remove('chainlink_btc.txt')
                chainlink = models.chainlink.ChainlinkBTC(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
                db.session.add(chainlink)
                db.session.commit()

                # Write new file
                f = open("chainlink_btc.txt", 'w')
                f.write('{}'.format(blockNum))
                f.close()

    if len(chainlink_prices) > 1:
        return chainlink_prices[-1], timestamp, chainlink_prices[-2]


'''
Get latest chainlink BTC price.
'''
def get_chainlink_bat_price(eth_price):
    # Get latest block number
    block_number_request = get_latest_block_number()

    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address=0x9b4e2579895efa2b4765063310Dc4109a7641129&topic0=0x0559884fd3a460db3073b7fc896cc77986f16e378210ded43186175bf646fc5f&apikey='.format(block_number_request) + api_key
    all = get(call)
    if all is None:
        chainlink_instance = db.session.query(models.chainlink.ChainlinkBAT).order_by(models.chainlink.ChainlinkBAT.blocknumber)[-2:]
        chainlink_price = chainlink_instance[1].price
        chainlink_timestamp = chainlink_instance[1].timestamp
        chainlink_last_price = chainlink_instance[0].price

        return chainlink_price, chainlink_timestamp, chainlink_last_price

    result = all['result']
    chainlink_prices = []
    timestamp = 0
    for event in result:
        number = event['topics'][1]
        bat_price = int(number, 16)

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if bat_price is not 0:
            updated_price = bat_price * pow(10, -18) * eth_price
            chainlink_prices.append(updated_price)

            f = open("chainlink_bat.txt", "r")
            last_block = f.readline()
            f.close()

            if blockNum > int(last_block):
                os.remove('chainlink_bat.txt')
                chainlink = models.chainlink.ChainlinkBAT(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
                db.session.add(chainlink)
                db.session.commit()

                # Write new file
                f = open("chainlink_bat.txt", 'w')
                f.write('{}'.format(blockNum))
                f.close()

    if len(chainlink_prices) > 1:
        return chainlink_prices[-1], timestamp, chainlink_prices[-2]


'''
Get initial Chainlink price data.
'''
def get_chainlink_data(start_block, end_block):
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock={}&address=0xF79D6aFBb6dA890132F9D7c355e3015f15F3406F&topic0=0x0559884fd3a460db3073b7fc896cc77986f16e378210ded43186175bf646fc5f&apikey='.format(start_block, end_block) + api_key
    all = get(call)
    result = all['result']
    for event in result:
        number = event['topics'][1]
        eth_price = int(number, 16)

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if eth_price is not 0:
            updated_price = eth_price * pow(10, -8)

            # Insert into db
            link = models.chainlink.ChainlinkETH(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
            db.session.add(link)
            db.session.commit()


'''
Get Chainlink BTC data
'''
def get_chainlink_btc_data(start_block, end_block):
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock={}&address=0xF5fff180082d6017036B771bA883025c654BC935&topic0=0x0559884fd3a460db3073b7fc896cc77986f16e378210ded43186175bf646fc5f&apikey='.format(start_block, end_block) + api_key
    all = get(call)

    result = all['result']
    for event in result:
        number = event['topics'][1]
        btc_price = int(number, 16)

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if btc_price is not 0:
            updated_price = btc_price * pow(10, -8)

            # Insert into db
            link = models.chainlink.ChainlinkBTC(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
            db.session.add(link)
            db.session.commit()


'''
Get Chainlink BTC data
'''
def get_chainlink_bat_data(start_block, end_block):
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock={}&address=0x9b4e2579895efa2b4765063310Dc4109a7641129&topic0=0x0559884fd3a460db3073b7fc896cc77986f16e378210ded43186175bf646fc5f&apikey='.format(start_block, end_block) + api_key
    all = get(call)

    result = all['result']
    eth_instance = db.session.query(models.chainlink.ChainlinkETH).order_by(models.chainlink.ChainlinkETH.blocknumber.desc()).filter(models.chainlink.ChainlinkETH.blocknumber <= start_block).limit(1)
    eth_price = 100
    if len(eth_instance[:]) == 0:
        eth_instance = db.session.query(models.chainlink.ChainlinkETH).order_by(models.chainlink.ChainlinkETH.blocknumber).filter(
            models.chainlink.ChainlinkETH.blocknumber <= start_block + 200000).limit(1)
        eth_price = eth_instance[0].price
    else:
        eth_price = eth_instance[0].price
    for event in result:
        number = event['topics'][1]
        bat_price = int(number, 16)

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if bat_price is not 0:
            updated_price = bat_price * pow(10, -18) * eth_price

            # Insert into db
            link = models.chainlink.ChainlinkBAT(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
            db.session.add(link)
            db.session.commit()


'''
Create all chainlink latest block files
'''
def create_chainlink_files():
    f = open('chainlink.txt', "w")
    f.write('1')
    f.close()

    f = open('chainlink_btc.txt', "w")
    f.write('1')
    f.close()

    f = open('chainlink_bat.txt', "w")
    f.write('1')
    f.close()


'''
Populate Chainlink
'''
def populate_chainlink():
    chainlink_start = 9288026
    chainlink_btc_start = 9080614
    chainlink_bat_start = 9152704
    chainlink_end = chainlink_start + 10000
    chainlink_btc_end = chainlink_btc_start + 10000
    chainlink_bat_end = chainlink_bat_start + 10000
    latest_block = get_latest_block_number() + 10000
    while chainlink_btc_start < latest_block:
        if chainlink_end > latest_block:
            get_chainlink_data(start_block=chainlink_start, end_block='latest')
            get_chainlink_btc_data(start_block=chainlink_btc_start, end_block='latest')
            get_chainlink_bat_data(start_block=chainlink_bat_start, end_block='latest')
        else:
            get_chainlink_data(start_block=chainlink_start, end_block=chainlink_end)
            get_chainlink_btc_data(start_block=chainlink_btc_start, end_block=chainlink_btc_end)
            get_chainlink_bat_data(start_block=chainlink_bat_start, end_block=chainlink_bat_end)

        print(chainlink_end)
        chainlink_start = chainlink_end + 1
        chainlink_btc_start = chainlink_btc_end + 1
        chainlink_bat_start = chainlink_bat_end + 1
        chainlink_end = chainlink_end + 10000
        chainlink_btc_end = chainlink_btc_end + 10000
        chainlink_bat_end = chainlink_bat_end + 10000
