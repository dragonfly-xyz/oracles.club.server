import models.tellor
from models.create_db import db
import requests
from requests.auth import HTTPBasicAuth
import os
import time

# API vars
api_key = os.environ.get('ETHERSCAN_API_KEY')
endpoint_base = 'https://api.etherscan.io/api'
headers = {'Content-Type': 'application/json'}
contract_address = '0x0Ba45A8b5d5575935B8158a88C631E9F9C95a2e5'
value_event_topic = '0xc509d04e0782579ee59912139246ccbdf6c36c43abd90591d912017f3467dd16'
eth_topic = '0x0000000000000000000000000000000000000000000000000000000000000001'
btc_topic = '0x0000000000000000000000000000000000000000000000000000000000000002'

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
Get all Tellor price pairs
'''


def get_tellor_prices():
    tellor_instance = db.session.query(models.tellor.TellorETH).order_by(
        models.tellor.TellorETH.blocknumber.desc()).limit(2)[-2:]
    tellor_price = tellor_instance[0].price
    tellor_timestamp = tellor_instance[0].timestamp
    tellor_last_price = tellor_instance[1].price

    tellor_btc_instance = db.session.query(models.tellor.TellorBTC).order_by(
        models.tellor.TellorBTC.blocknumber.desc()).limit(2)[-2:]
    tellor_btc_price = tellor_btc_instance[0].price
    tellor_btc_timestamp = tellor_btc_instance[0].timestamp
    tellor_btc_last_price = tellor_btc_instance[1].price

    return tellor_price, tellor_timestamp, tellor_last_price, tellor_btc_price, tellor_btc_timestamp, tellor_btc_last_price


'''
Get latest block number
'''


def get_latest_block_number():
    global api_key
    while api_key is None:
        api_key = os.environ.get('ETHERSCAN_API_KEY')

    block_num_call = endpoint_base + \
        '?module=proxy&action=eth_blockNumber&apikey=' + api_key
    block_result = get(block_num_call)
    if block_result is None:
        time.sleep(1)
        get_latest_block_number()

    block_number = int(block_result['result'], 16)
    block_number_request = block_number - 10000

    return block_number_request


'''
Get latest tellor price.
'''


def get_tellor_price():
    # Get latest block number
    block_number_request = get_latest_block_number()

    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address={}&topic0={}&topic0_1_opr=and&topic1={}&apikey='.format(
        block_number_request, contract_address, value_event_topic, eth_topic) + api_key
    all = get(call)
    if all is None:
        tellor_instance = db.session.query(models.tellor.TellorETH).order_by(
            models.tellor.TellorETH.blocknumber)[-2:]
        tellor_price = tellor_instance[1].price
        tellor_timestamp = tellor_instance[1].timestamp
        tellor_last_price = tellor_instance[0].price

        return tellor_price, tellor_timestamp, tellor_last_price

    result = all['result']
    tellor_prices = []
    timestamp = 0
    for event in result:
        number = event['data'][66:130]
        eth_price = (int(number, 16) * 100 / 1000000) / 100

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if eth_price is not 0:
            tellor_prices.append(btc_price)

            f = open("tellor.txt", "r")
            last_block = f.readline()
            f.close()

            if blockNum > int(last_block):
                os.remove('tellor.txt')
                tellor = models.tellor.TellorETH(
                    timestamp=timestamp, blocknumber=blockNum, price=btc_price)
                db.session.add(tellor)
                db.session.commit()

                # Write new file
                f = open("tellor.txt", 'w')
                f.write('{}'.format(blockNum))
                f.close()

    if len(tellor_prices) > 1:
        return tellor_prices[-1], timestamp, tellor_prices[-2]


'''
Get latest tellor BTC price.
'''


def get_tellor_btc_price():
    # Get latest block number
    block_number_request = get_latest_block_number()
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address={}&topic0={}&topic0_1_opr=and&topic1={}&apikey='.format(
        block_number_request, contract_address, value_event_topic, btc_topic) + api_key
    all = get(call)
    if all is None:
        tellor_instance = db.session.query(models.tellor.TellorBTC).order_by(
            models.tellor.TellorBTC.blocknumber)[-2:]
        tellor_price = tellor_instance[1].price
        tellor_timestamp = tellor_instance[1].timestamp
        tellor_last_price = tellor_instance[0].price

        return tellor_price, tellor_timestamp, tellor_last_price

    result = all['result']
    tellor_prices = []
    timestamp = 0
    for event in result:
        number = event['data'][66:130]
        btc_price = (int(number, 16) * 100 / 1000000) / 100

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if btc_price is not 0:
            tellor_prices.append(btc_price)

            f = open("tellor_btc.txt", "r")
            last_block = f.readline()
            f.close()

            if blockNum > int(last_block):
                os.remove('tellor_btc.txt')
                tellor = models.tellor.TellorBTC(
                    timestamp=timestamp, blocknumber=blockNum, price=btc_price)
                db.session.add(tellor)
                db.session.commit()

                # Write new file
                f = open("tellor_btc.txt", 'w')
                f.write('{}'.format(blockNum))
                f.close()

    if len(tellor_prices) > 1:
        return tellor_prices[-1], timestamp, tellor_prices[-2]


'''
Get initial Tellor price data.
'''


def get_tellor_data(start_block, end_block):
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock={}&address={}&topic0={}&topic0_1_opr=and&topic1={}&apikey='.format(
        start_block, end_block, contract_address, value_event_topic, eth_topic) + api_key
    all = get(call)
    result = all['result']
    for event in result:
        number = event['data'][66:130]
        eth_price = (int(number, 16) * 100 / 1000000) / 100

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if eth_price is not 0:
            # Insert into db
            link = models.tellor.TellorETH(
                timestamp=timestamp, blocknumber=blockNum, price=eth_price)
            db.session.add(link)
            db.session.commit()


'''
Get Tellor BTC data
'''


def get_tellor_btc_data(start_block, end_block):
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock={}&address={}&topic0={}&topic0_1_opr=and&topic1={}&apikey='.format(
        start_block, end_block, contract_address, value_event_topic, btc_topic) + api_key
    all = get(call)

    result = all['result']
    for event in result:
        number = event['data'][66:130]
        btc_price = (int(number, 16) * 100 / 1000000) / 100

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if btc_price is not 0:
            # Insert into db
            link = models.tellor.TellorBTC(
                timestamp=timestamp, blocknumber=blockNum, price=btc_price)
            db.session.add(link)
            db.session.commit()


'''
Create all tellor latest block files
'''


def create_tellor_files():
    f = open('tellor.txt', "w")
    f.write('1')
    f.close()

    f = open('tellor_btc.txt', "w")
    f.write('1')
    f.close()


'''
Populate Tellor
'''


def populate_tellor():
    tellor_start = 10372672
    tellor_btc_start = 10338090
    tellor_end = tellor_start + 10000
    tellor_btc_end = tellor_btc_start + 10000
    latest_block = get_latest_block_number() + 10000
    tellor_btc_start = latest_block - 10

    while tellor_btc_start < latest_block:
        if tellor_end > latest_block:
            get_tellor_data(start_block=tellor_start, end_block='latest')
            get_tellor_btc_data(
                start_block=tellor_btc_start, end_block='latest')
        else:
            get_tellor_data(start_block=tellor_start, end_block=tellor_end)
            get_tellor_btc_data(start_block=tellor_btc_start,
                                end_block=tellor_btc_end)

        print(tellor_end)
        tellor_start = tellor_end + 1
        tellor_btc_start = tellor_btc_end + 1
        tellor_end = tellor_end + 10000
        tellor_btc_end = tellor_btc_end + 10000
