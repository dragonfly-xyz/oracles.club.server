import models.maker
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
Get all Maker prices pairs
'''
def get_maker_prices():
    maker_instance = db.session.query(models.maker.MakerETH).order_by(models.maker.MakerETH.blocknumber.desc()).limit(2)[-2:]
    maker_price = maker_instance[0].price
    maker_timestamp = maker_instance[0].timestamp
    maker_last_price = maker_instance[1].price

    maker_btc_instance = db.session.query(models.maker.MakerBTC).order_by(models.maker.MakerBTC.blocknumber.desc()).limit(2)[-2:]
    maker_btc_price = maker_btc_instance[0].price
    maker_btc_timestamp = maker_btc_instance[0].timestamp
    maker_btc_last_price = maker_btc_instance[1].price

    maker_bat_instance = db.session.query(models.maker.MakerBAT).order_by(models.maker.MakerBAT.blocknumber.desc()).limit(2)[-2:]
    maker_bat_price = maker_bat_instance[0].price
    maker_bat_timestamp = maker_bat_instance[0].timestamp
    maker_bat_last_price = maker_bat_instance[1].price

    return maker_price, maker_timestamp, maker_last_price, maker_btc_price, maker_btc_timestamp, maker_btc_last_price, maker_bat_price, maker_bat_timestamp, maker_bat_last_price


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
Get's latest price from the maker oracle
'''
def get_maker_price():
    # Get latest block number
    block_number_request = get_latest_block_number()

    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address=0x81FE72B5A8d1A857d176C3E7d5Bd2679A9B85763&topic0=0x296ba4ca62c6c21c95e828080cb8aec7481b71390585605300a8a76f9e95b527&apikey='.format(block_number_request) + api_key
    all = get(call)

    # Fix none check
    if all is None:
        maker_instance = db.session.query(models.maker.MakerETH).order_by(models.maker.MakerETH.blocknumber)[-2:]
        maker_price = maker_instance[1].price
        maker_timestamp = maker_instance[1].timestamp
        maker_last_price = maker_instance[0].price
        return maker_price, maker_timestamp, maker_last_price

    result = all['result']
    maker_prices = []
    timestamp = 0
    for event in result:
        number = event['data']
        eth_price = int(number, 16)

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if eth_price is not 0:
            updated_price = eth_price * pow(10, -18)
            maker_prices.append(updated_price)
            f = open("maker.txt", "r")
            last_block = f.readline()
            f.close()

            if blockNum > int(last_block):
                os.remove('maker.txt')
                maker = models.maker.MakerETH(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
                db.session.add(maker)
                db.session.commit()

                # Write new file
                f = open("maker.txt", 'w')
                f.write('{}'.format(blockNum))
                f.close()

    if len(maker_prices) > 1:
        return maker_prices[-1], timestamp, maker_prices[-2]


'''
Get maker bat price
'''
def get_maker_bat_price():
    # Get latest block number
    block_number_request = get_latest_block_number()
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address=0xB4eb54AF9Cc7882DF0121d26c5b97E802915ABe6&topic0=0x296ba4ca62c6c21c95e828080cb8aec7481b71390585605300a8a76f9e95b527&apikey='.format(block_number_request) + api_key
    all = get(call)

    # Fix none check
    if all is None:
        maker_instance = db.session.query(models.maker.MakerBAT).order_by(models.maker.MakerBAT.blocknumber)[-2:]
        maker_price = maker_instance[1].price
        maker_timestamp = maker_instance[1].timestamp
        maker_last_price = maker_instance[0].price
        return maker_price, maker_timestamp, maker_last_price

    result = all['result']
    maker_prices = []
    timestamp = 0
    for event in result:
        number = event['data']
        bat_price = int(number, 16)

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if bat_price is not 0:
            updated_price = bat_price * pow(10, -18)
            maker_prices.append(updated_price)
            f = open("maker_bat.txt", "r")
            last_block = f.readline()
            f.close()

            if blockNum > int(last_block):
                os.remove('maker_bat.txt')
                maker = models.maker.MakerBAT(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
                db.session.add(maker)
                db.session.commit()

                # Write new file
                f = open("maker_bat.txt", 'w')
                f.write('{}'.format(blockNum))
                f.close()

    if len(maker_prices) > 1:
        return maker_prices[-1], timestamp, maker_prices[-2]

'''
Get maker btc price
'''
def get_maker_btc_price():
    # Get latest block number
    block_number_request = get_latest_block_number()
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address=0xe0F30cb149fAADC7247E953746Be9BbBB6B5751f&topic0=0xb78ebc573f1f889ca9e1e0fb62c843c836f3d3a2e1f43ef62940e9b894f4ea4c&apikey='.format(block_number_request) + api_key
    all = get(call)

    # Fix none check
    if all is None:
        maker_instance = db.session.query(models.maker.MakerBTC).order_by(models.maker.MakerBTC.blocknumber)[-2:]
        maker_price = maker_instance[1].price
        maker_timestamp = maker_instance[1].timestamp
        maker_last_price = maker_instance[0].price
        return maker_price, maker_timestamp, maker_last_price

    result = all['result']
    maker_prices = []
    timestamp = 0
    for event in result:
        number = event['data'][:66]
        btc_price = int(number, 16)

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if btc_price is not 0:
            updated_price = btc_price * pow(10, -18)
            maker_prices.append(updated_price)
            f = open("maker_btc.txt", "r")
            last_block = f.readline()
            f.close()

            if blockNum > int(last_block):
                os.remove('maker_btc.txt')
                maker = models.maker.MakerBTC(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
                db.session.add(maker)
                db.session.commit()

                # Write new file
                f = open("maker_btc.txt", 'w')
                f.write('{}'.format(blockNum))
                f.close()

    if len(maker_prices) > 1:
        return maker_prices[-1], timestamp, maker_prices[-2]

'''
Get initial Maker price data.
'''
def get_maker_data(start_block, end_block):
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock={}&address=0x81FE72B5A8d1A857d176C3E7d5Bd2679A9B85763&topic0=0x296ba4ca62c6c21c95e828080cb8aec7481b71390585605300a8a76f9e95b527&apikey='.format(start_block, end_block) + api_key
    all = get(call)
    result = all['result']
    for event in result:
        number = event['data']
        eth_price = int(number, 16)

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if eth_price is not 0:
            updated_price = eth_price * pow(10, -18)

            # Insert into db
            maker = models.maker.MakerETH(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
            db.session.add(maker)
            db.session.commit()


'''
Get initial Maker BAT price data.
'''
def get_maker_bat_data(start_block, end_block):
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock={}&address=0xB4eb54AF9Cc7882DF0121d26c5b97E802915ABe6&topic0=0x296ba4ca62c6c21c95e828080cb8aec7481b71390585605300a8a76f9e95b527&apikey='.format(start_block, end_block) + api_key
    all = get(call)
    result = all['result']
    for event in result:
        number = event['data']
        eth_price = int(number, 16)

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if eth_price is not 0:
            updated_price = eth_price * pow(10, -18)

            # Insert into db
            maker = models.maker.MakerBAT(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
            db.session.add(maker)
            db.session.commit()


'''
Get initial Maker BTC price data.
'''
def get_maker_btc_data(start_block, end_block):
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock={}&address=0xe0F30cb149fAADC7247E953746Be9BbBB6B5751f&topic0=0xb78ebc573f1f889ca9e1e0fb62c843c836f3d3a2e1f43ef62940e9b894f4ea4c&apikey='.format(start_block, end_block) + api_key
    all = get(call)
    result = all['result']
    for event in result:
        number = event['data'][:66]
        btc_price = int(number, 16)

        blockNumHex = event['blockNumber']
        blockNum = int(blockNumHex, 16)

        timestampHex = event['timeStamp']
        timestamp = int(timestampHex, 16)

        if btc_price is not 0:
            updated_price = btc_price * pow(10, -18)

            # Insert into db
            maker = models.maker.MakerBTC(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
            db.session.add(maker)
            db.session.commit()


'''
Populate Maker
'''
def populate_maker():
    maker_start = 8925094
    maker_btc_start = 8925077
    maker_bat_start = 8925118
    maker_end = maker_start + 10000
    latest_block = get_latest_block_number() + 10000
    while maker_start < latest_block:
        if maker_end > latest_block:
            get_maker_data(start_block=maker_start, end_block='latest')
            get_maker_btc_data(maker_start, 'latest')
            get_maker_bat_data(maker_start, 'latest')
        else:
            get_maker_data(start_block=maker_start, end_block=maker_end)
            get_maker_btc_data(start_block=maker_btc_start, end_block=maker_end)
            get_maker_bat_data(start_block=maker_bat_start, end_block=maker_end)

        print(maker_end)
        maker_start = maker_end + 1
        maker_btc_start = maker_end + 1
        maker_bat_start = maker_end + 1
        maker_end = maker_end + 10000


'''
Create all uniswap latest block files
'''
def create_maker_files():
    f = open('maker.txt', "w")
    f.write('1')
    f.close()

    f = open('maker_btc.txt', "w")
    f.write('1')
    f.close()

    f = open('maker_bat.txt', "w")
    f.write('1')
    f.close()
