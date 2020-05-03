import models.compound
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
Get all Compound prices
'''
def get_compound_prices():
    compound_instance = db.session.query(models.compound.CompoundETH).order_by(models.compound.CompoundETH.blocknumber.desc()).limit(2)[-2:]
    compound_price = compound_instance[0].price
    compound_timestamp = compound_instance[0].timestamp
    compound_last_price = compound_instance[1].price

    compound_btc_instance = db.session.query(models.compound.CompoundBTC).order_by(models.compound.CompoundBTC.blocknumber.desc()).limit(2)[-2:]
    compound_btc_price = compound_btc_instance[0].price
    compound_btc_timestamp = compound_btc_instance[0].timestamp
    compound_btc_last_price = compound_btc_instance[1].price

    compound_bat_instance = db.session.query(models.compound.CompoundBAT).order_by(models.compound.CompoundBAT.blocknumber.desc()).limit(10)[-2:]
    compound_bat_price = float(compound_bat_instance[0].price)
    compound_bat_timestamp = compound_bat_instance[0].timestamp
    compound_bat_last_price = float(compound_bat_instance[1].price)

    return compound_price, compound_timestamp, compound_last_price, compound_btc_price, compound_btc_timestamp, compound_btc_last_price, compound_bat_price, compound_bat_timestamp, compound_bat_last_price


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
Get latest compound price
'''
def get_compound_price():
    # Get latest block number
    block_number_request = get_latest_block_number()

    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address=0x02557a5E05DeFeFFD4cAe6D83eA3d173B272c904&topic0=0xdd71a1d19fcba687442a1d5c58578f1e409af71a79d10fd95a4d66efd8fa9ae7&apikey='.format(block_number_request) + api_key
    all = get(call)
    result = all['result']
    compound_prices = []
    timestamp = 0
    for event in result:
        data = event['data']

        # Filter logs for usdc price
        if data[:66] == '0x0000000000000000000000000000000000000000000000000000000000000001':
            number = data[-24:]
            price = int(number, 16)
            updated_price = 1/(price * pow(10, -30))
            compound_prices.append(updated_price)

            blockNumHex = event['blockNumber']
            blockNum = int(blockNumHex, 16)

            timestampHex = event['timeStamp']
            timestamp = int(timestampHex, 16)


            f = open("compound.txt", "r")
            last_block = f.readline()
            f.close()
            if blockNum > int(last_block):
                os.remove('compound.txt')
                compound = models.compound.CompoundETH(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
                db.session.add(compound)
                db.session.commit()

                # Write new file
                f = open("compound.txt", 'w')
                f.write('{}'.format(blockNum))
                f.close()

    if len(compound_prices) > 1:
        return compound_prices[-1], timestamp, compound_prices[-2]


'''
Get latest compound btc price
'''
def get_compound_btc_price(eth_price):
    # Get latest block number
    block_number_request = get_latest_block_number()

    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address=0x02557a5E05DeFeFFD4cAe6D83eA3d173B272c904&topic0=0xdd71a1d19fcba687442a1d5c58578f1e409af71a79d10fd95a4d66efd8fa9ae7&apikey='.format(block_number_request) + api_key
    all = get(call)
    result = all['result']
    compound_prices = []
    timestamp = 0
    for event in result:
        data = event['data']

        # Filter logs for btc price
        if data[:66] == '0x0000000000000000000000002260fac5e5542a773aa44fbcfedf7c193bc2c599':
            number = data[-64:]
            price = int(number, 16)
            updated_price = (price * pow(10, -28)) * eth_price
            compound_prices.append(updated_price)

            blockNumHex = event['blockNumber']
            blockNum = int(blockNumHex, 16)

            timestampHex = event['timeStamp']
            timestamp = int(timestampHex, 16)


            f = open("compound_btc.txt", "r")
            last_block = f.readline()
            f.close()
            if blockNum > int(last_block):
                os.remove('compound_btc.txt')
                compound = models.compound.CompoundBTC(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
                db.session.add(compound)
                db.session.commit()

                # Write new file
                f = open("compound_btc.txt", 'w')
                f.write('{}'.format(blockNum))
                f.close()

    if len(compound_prices) > 1:
        return compound_prices[-1], timestamp, compound_prices[-2]


'''
Get latest compound bat price
'''
def get_compound_bat_price(eth_price):
    # Get latest block number
    block_number_request = get_latest_block_number()

    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock=latest&address=0x02557a5E05DeFeFFD4cAe6D83eA3d173B272c904&topic0=0xdd71a1d19fcba687442a1d5c58578f1e409af71a79d10fd95a4d66efd8fa9ae7&apikey='.format(block_number_request) + api_key
    all = get(call)
    result = all['result']
    compound_prices = []
    timestamp = 0
    for event in result:
        data = event['data']

        # Filter logs for usdc price
        if data[:66] == '0x0000000000000000000000000d8775f648430679a709e98d2b0cb6250d2887ef':
            number = data[-64:]
            price = int(number, 16)
            updated_price = float(price * pow(10, -18)) * eth_price
            compound_prices.append(updated_price)

            blockNumHex = event['blockNumber']
            blockNum = int(blockNumHex, 16)

            timestampHex = event['timeStamp']
            timestamp = int(timestampHex, 16)


            f = open("compound_bat.txt", "r")
            last_block = f.readline()
            f.close()
            if blockNum > int(last_block):
                os.remove('compound_bat.txt')
                compound = models.compound.CompoundBAT(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
                db.session.add(compound)
                db.session.commit()

                # Write new file
                f = open("compound_bat.txt", 'w')
                f.write('{}'.format(blockNum))
                f.close()

    if len(compound_prices) > 1:
        if compound_prices[-1] > 100 and len(compound_prices) > 2:
            return compound_prices[-2], timestamp, compound_prices[-3]
        else:
            return compound_prices[-1], timestamp, compound_prices[-2]


'''
Get initial Compound price data.
'''
def get_compound_data(start_block, end_block):
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock={}&address=0x02557a5E05DeFeFFD4cAe6D83eA3d173B272c904&topic0=0xdd71a1d19fcba687442a1d5c58578f1e409af71a79d10fd95a4d66efd8fa9ae7&apikey='.format(start_block, end_block) + api_key
    all = get(call)
    if all is None:
        compound_instance = db.session.query(models.compound.CompoundETH).order_by(models.compound.CompoundETH.blocknumber)[-2:]
        compound_price = compound_instance[1].price
        compound_timestamp = compound_instance[1].timestamp
        compound_last_price = compound_instance[0].price
        return compound_price, compound_timestamp, compound_last_price

    result = all['result']
    for event in result:
        data = event['data']

        # Filter logs for usdc price
        if data[:66] == '0x0000000000000000000000000000000000000000000000000000000000000001':
            number = data[-24:]
            price = int(number, 16)
            updated_price = 1/(price * pow(10, -30))

            blockNumHex = event['blockNumber']
            blockNum = int(blockNumHex, 16)

            timestampHex = event['timeStamp']
            timestamp = int(timestampHex, 16)

            # Insert into db
            compound = models.compound.CompoundETH(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
            db.session.add(compound)
            db.session.commit()


'''
Get initial Compound BTC price data.
'''
def get_compound_btc_data(start_block, end_block):
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock={}&address=0x02557a5E05DeFeFFD4cAe6D83eA3d173B272c904&topic0=0xdd71a1d19fcba687442a1d5c58578f1e409af71a79d10fd95a4d66efd8fa9ae7&apikey='.format(start_block, end_block) + api_key
    all = get(call)
    if all is None:
        compound_instance = db.session.query(models.compound.CompoundBTC).order_by(models.compound.CompoundBTC.blocknumber)[-2:]
        compound_price = compound_instance[1].price
        compound_timestamp = compound_instance[1].timestamp
        compound_last_price = compound_instance[0].price
        return compound_price, compound_timestamp, compound_last_price

    result = all['result']
    eth_instance = db.session.query(models.compound.CompoundETH).order_by(models.compound.CompoundETH.blocknumber.desc()).filter(models.compound.CompoundETH.blocknumber <= start_block).limit(1)
    eth_price = 100
    if len(eth_instance[:]) == 0:
        eth_instance = db.session.query(models.compound.CompoundETH).order_by(models.compound.CompoundETH.blocknumber.desc()).filter(
            models.compound.CompoundETH.blocknumber <= (start_block + 100000)).limit(1)
        if len(eth_instance[:]) == 0:
            eth_price = 100
        else:
            eth_price = eth_instance[0].price
    else:
        eth_price = eth_instance[0].price
    for event in result:
        data = event['data']

        # Filter logs for btc
        if data[:66] == '0x0000000000000000000000002260fac5e5542a773aa44fbcfedf7c193bc2c599':
            number = data[-66:]
            price = int(number, 16)
            updated_price = (price * pow(10, -28)) * eth_price

            blockNumHex = event['blockNumber']
            blockNum = int(blockNumHex, 16)

            timestampHex = event['timeStamp']
            timestamp = int(timestampHex, 16)

            # Insert into db
            compound = models.compound.CompoundBTC(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
            db.session.add(compound)
            db.session.commit()


'''
Get initial Compound BAT price data.
'''
def get_compound_bat_data(start_block, end_block):
    # To fix Compound bug, print output you get here!
    call = endpoint_base + '?module=logs&action=getLogs&fromBlock={}&toBlock={}&address=0x02557a5E05DeFeFFD4cAe6D83eA3d173B272c904&topic0=0xdd71a1d19fcba687442a1d5c58578f1e409af71a79d10fd95a4d66efd8fa9ae7&apikey='.format(start_block, end_block) + api_key
    all = get(call)
    if all is None:
        compound_instance = db.session.query(models.compound.CompoundBTC).order_by(models.compound.CompoundBTC.blocknumber)[-2:]
        compound_price = compound_instance[1].price
        compound_timestamp = compound_instance[1].timestamp
        compound_last_price = compound_instance[0].price
        return compound_price, compound_timestamp, compound_last_price

    result = all['result']
    eth_instance = db.session.query(models.compound.CompoundETH).order_by(models.compound.CompoundETH.blocknumber.desc()).filter(models.compound.CompoundETH.blocknumber <= start_block).limit(1)
    eth_price = 100
    if len(eth_instance[:]) == 0:
        eth_instance = db.session.query(models.compound.CompoundETH).order_by(models.compound.CompoundETH.blocknumber.desc()).filter(
            models.compound.CompoundETH.blocknumber <= (start_block + 100000)).limit(1)
        if len(eth_instance[:]) == 0:
            eth_price = 100
        else:
            eth_price = eth_instance[0].price
    else:
        eth_price = eth_instance[0].price
    for event in result:
        data = event['data']

        # Filter logs for btc
        if data[:66] == '0x0000000000000000000000000d8775f648430679a709e98d2b0cb6250d2887ef':
            number = data[-66:]
            price = int(number, 16)
            updated_price = (price * pow(10, -18)) * eth_price

            blockNumHex = event['blockNumber']
            blockNum = int(blockNumHex, 16)

            timestampHex = event['timeStamp']
            timestamp = int(timestampHex, 16)

            # Insert into db
            compound = models.compound.CompoundBAT(timestamp=timestamp, blocknumber=blockNum, price=updated_price)
            db.session.add(compound)
            db.session.commit()


'''
Populate Compound 
'''
def populate_compound():
    compound_start = 6747538
    compound_end = compound_start + 10000
    latest_block = get_latest_block_number() + 10000
    while compound_start < latest_block:
        if compound_end > latest_block:
            get_compound_data(start_block=compound_start, end_block='latest')
            get_compound_btc_data(start_block=compound_start, end_block='latest')
            get_compound_bat_data(start_block=compound_start, end_block='latest')
        else:
            get_compound_data(start_block=compound_start, end_block=compound_end)
            get_compound_btc_data(start_block=compound_start, end_block=compound_end)
            get_compound_bat_data(start_block=compound_start, end_block=compound_end)

        print(compound_end)
        compound_start = compound_end + 1
        compound_end = compound_end + 10000


'''
Create all compound latest block files
'''
def create_compound_files():
    f = open('compound.txt', "w")
    f.write('1')
    f.close()

    f = open('compound_btc.txt', "w")
    f.write('1')
    f.close()

    f = open('compound_bat.txt', "w")
    f.write('1')
    f.close()
