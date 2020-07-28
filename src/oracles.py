import asyncio
import models.dfusion
import models.chainlink
import models.maker
import models.compound
import models.uniswap
import models.coinbase
import models.tellor
from models.create_db import db
import chainlink_methods
import dfusion_methods
import compound_methods
import uniswap_methods
import coinbase_methods
import maker_methods
import tellor_methods
from flask import Flask
from flask_cors import CORS
from flask_caching import Cache
import requests
from requests.auth import HTTPBasicAuth
import simplejson as json
import ssl
import time
from threading import Thread
import websockets
import os

# Cache vars
config = {
    "DEBUG": True,
    "CACHE_TYPE": "redis",
    "CACHE_DEFAULT_TIMEOUT": 30,
    "SQLALCHEMY_DATABASE_URI": 'sqlite://'
}

# Start flask and db
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)
CORS(app)

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

# END API CALLS


@app.route('/makerETH')
@cache.cached(timeout=300)
def get_maker_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(0, 'ETH'))


@app.route('/makerBTC')
@cache.cached(timeout=300)
def get_maker_btc_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(0, 'BTC'))


@app.route('/makerBAT')
@cache.cached(timeout=300)
def get_maker_bat_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(0, 'BAT'))


@app.route('/chainlinkETH')
@cache.cached(timeout=300)
def get_chainlink_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(1, 'ETH'))


@app.route('/chainlinkBTC')
@cache.cached(timeout=300)
def get_chainlink_btc_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(1, 'BTC'))


@app.route('/chainlinkBAT')
@cache.cached(timeout=300)
def get_chainlink_bat_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(1, 'BAT'))


@app.route('/compoundETH')
@cache.cached(timeout=300)
def get_compound_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(2, 'ETH'))


@app.route('/compoundBTC')
@cache.cached(timeout=300)
def get_compound_btc_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(2, 'BTC'))


@app.route('/compoundBAT')
@cache.cached(timeout=300)
def get_compound_bat_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(2, 'BAT'))


@app.route('/dfusionETH')
@cache.cached(timeout=300)
def get_dfusion_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(3, 'ETH'))


@app.route('/dfusionBTC')
@cache.cached(timeout=300)
def get_dfusion_btc_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(3, 'BTC'))


@app.route('/uniswapETH')
@cache.cached(timeout=300)
def get_uniswap_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(4, 'ETH'))


@app.route('/uniswapBTC')
@cache.cached(timeout=300)
def get_uniswap_btc_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(4, 'BTC'))


@app.route('/uniswapBAT')
@cache.cached(timeout=300)
def get_uniswap_bat_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(4, 'BAT'))


@app.route('/coinbaseETH')
@cache.cached(timeout=300)
def get_coinbase_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(5, 'ETH'))


@app.route('/coinbaseBTC')
@cache.cached(timeout=300)
def get_coinbase_btc_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(5, 'BTC'))


@app.route('/tellorETH')
@cache.cached(timeout=300)
def get_tellor_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(6, 'ETH'))


@app.route('/tellorBTC')
@cache.cached(timeout=300)
def get_tellor_btc_historical_data():
    # Optionally can use flask here to return all necessary data
    return json.dumps(get_historical_data(6, 'BTC'))


@app.route('/current')
@cache.cached(timeout=30)
def get_current_data():
    # Return latest db data
    maker_eth_price, maker_eth_timestamp, maker_eth_last_price, maker_btc_price, maker_btc_timestamp, maker_btc_last_price, maker_bat_price, maker_bat_timestamp, maker_bat_last_price = maker_methods.get_maker_prices()
    chainlink_eth_price, chainlink_eth_timestamp, chainlink_eth_last_price, chainlink_btc_price, chainlink_btc_timestamp, chainlink_btc_last_price, chainlink_bat_price, chainlink_bat_timestamp, chainlink_bat_last_price = chainlink_methods.get_chainlink_prices()
    compound_eth_price, compound_eth_timestamp, compound_eth_last_price, compound_btc_price, compound_btc_timestamp, compound_btc_last_price, compound_bat_price, compound_bat_timestamp, compound_bat_last_price = compound_methods.get_compound_prices()
    uniswap_eth_price, uniswap_eth_timestamp, uniswap_eth_last_price, uniswap_btc_price, uniswap_btc_timestamp, uniswap_btc_last_price, uniswap_bat_price, uniswap_bat_timestamp, uniswap_bat_last_price = uniswap_methods.get_uniswap_prices()
    dfusion_eth_price, dfusion_eth_timestamp, dfusion_eth_last_price, dfusion_btc_price, dfusion_btc_timestamp, dfusion_btc_last_price = dfusion_methods.get_dfusion_prices()
    coinbase_eth_price, coinbase_eth_timestamp, coinbase_eth_last_price, coinbase_btc_price, coinbase_btc_timestamp, coinbase_btc_last_price = coinbase_methods.get_coinbase_prices()
    tellor_eth_price, tellor_eth_timestamp, tellor_eth_last_price, tellor_btc_price, tellor_btc_timestamp, tellor_btc_last_price = tellor_methods.get_tellor_prices()

    print("Sending")
    prices = {
        'ETHUSD': {
            'Maker': {
                'cur_price': maker_eth_price,
                'last_updated': maker_eth_timestamp,
                'prev_price': maker_eth_last_price
            },
            'Chainlink': {
                'cur_price': chainlink_eth_price,
                'last_updated': chainlink_eth_timestamp,
                'prev_price': chainlink_eth_last_price
            },
            'Compound': {
                'cur_price': compound_eth_price,
                'last_updated': compound_eth_timestamp,
                'prev_price': compound_eth_last_price
            },
            'Uniswap': {
                'cur_price': uniswap_eth_price,
                'last_updated': uniswap_eth_timestamp,
                'prev_price': uniswap_eth_last_price
            },
            'Dfusion': {
                'cur_price': dfusion_eth_price,
                'last_updated': dfusion_eth_timestamp,
                'prev_price': dfusion_eth_last_price
            },
            'Coinbase': {
                'cur_price': coinbase_eth_price,
                'last_updated': coinbase_eth_timestamp,
                'prev_price': coinbase_eth_last_price
            },
            'Tellor': {
                'cur_price':  tellor_eth_price,
                'last_updated': tellor_eth_timestamp,
                'prev_price': tellor_eth_last_price
            }
        },
        'BTCUSD': {
            'Maker': {
                'cur_price': maker_btc_price,
                'last_updated': maker_btc_timestamp,
                'prev_price': maker_btc_last_price
            },
            'Chainlink': {
                'cur_price': chainlink_btc_price,
                'last_updated': chainlink_btc_timestamp,
                'prev_price': chainlink_btc_last_price
            },
            'Compound': {
                'cur_price': compound_btc_price,
                'last_updated': compound_btc_timestamp,
                'prev_price': compound_btc_last_price
            },
            'Uniswap': {
                'cur_price': uniswap_btc_price,
                'last_updated': uniswap_btc_timestamp,
                'prev_price': uniswap_btc_last_price
            },
            'Dfusion': {
                'cur_price': dfusion_btc_price,
                'last_updated': dfusion_btc_timestamp,
                'prev_price': dfusion_btc_last_price
            },
            'Coinbase': {
                'cur_price': coinbase_btc_price,
                'last_updated': coinbase_btc_timestamp,
                'prev_price': coinbase_btc_last_price
            },
            'Tellor': {
                'cur_price': tellor_btc_price,
                'last_updated': tellor_btc_timestamp,
                'prev_price': tellor_btc_last_price
            }
        },
        'BATUSD': {
            'Maker': {
                'cur_price': maker_bat_price,
                'last_updated': maker_bat_timestamp,
                'prev_price': maker_bat_last_price
            },
            'Chainlink': {
                'cur_price': chainlink_bat_price,
                'last_updated': chainlink_bat_timestamp,
                'prev_price': chainlink_bat_last_price
            },
            'Compound': {
                'cur_price': compound_bat_price,
                'last_updated': compound_bat_timestamp,
                'prev_price': float(compound_bat_last_price)
            },
            'Uniswap': {
                'cur_price': uniswap_bat_price,
                'last_updated': uniswap_bat_timestamp,
                'prev_price': uniswap_bat_last_price
            }
        }
    }

    json_data = json.dumps(prices)
    return json_data


'''
Get data for websocket
'''


def get_data_websocket():
    # Return latest db data
    maker_eth_price, maker_eth_timestamp, maker_eth_last_price, maker_btc_price, maker_btc_timestamp, maker_btc_last_price, maker_bat_price, maker_bat_timestamp, maker_bat_last_price = maker_methods.get_maker_prices()
    chainlink_eth_price, chainlink_eth_timestamp, chainlink_eth_last_price, chainlink_btc_price, chainlink_btc_timestamp, chainlink_btc_last_price, chainlink_bat_price, chainlink_bat_timestamp, chainlink_bat_last_price = chainlink_methods.get_chainlink_prices()
    compound_eth_price, compound_eth_timestamp, compound_eth_last_price, compound_btc_price, compound_btc_timestamp, compound_btc_last_price, compound_bat_price, compound_bat_timestamp, compound_bat_last_price = compound_methods.get_compound_prices()
    uniswap_eth_price, uniswap_eth_timestamp, uniswap_eth_last_price, uniswap_btc_price, uniswap_btc_timestamp, uniswap_btc_last_price, uniswap_bat_price, uniswap_bat_timestamp, uniswap_bat_last_price = uniswap_methods.get_uniswap_prices()
    dfusion_eth_price, dfusion_eth_timestamp, dfusion_eth_last_price, dfusion_btc_price, dfusion_btc_timestamp, dfusion_btc_last_price = dfusion_methods.get_dfusion_prices()
    coinbase_eth_price, coinbase_eth_timestamp, coinbase_eth_last_price, coinbase_btc_price, coinbase_btc_timestamp, coinbase_btc_last_price = coinbase_methods.get_coinbase_prices()
    tellor_eth_price, tellor_eth_timestamp, tellor_eth_last_price, tellor_btc_price, tellor_btc_timestamp, tellor_btc_last_price = tellor_methods.get_tellor_prices()

    print("Sending")
    prices = {
        'ETHUSD': {
            'Maker': {
                'cur_price': maker_eth_price,
                'last_updated': maker_eth_timestamp,
                'prev_price': maker_eth_last_price
            },
            'Chainlink': {
                'cur_price': chainlink_eth_price,
                'last_updated': chainlink_eth_timestamp,
                'prev_price': chainlink_eth_last_price
            },
            'Compound': {
                'cur_price': compound_eth_price,
                'last_updated': compound_eth_timestamp,
                'prev_price': compound_eth_last_price
            },
            'Uniswap': {
                'cur_price': uniswap_eth_price,
                'last_updated': uniswap_eth_timestamp,
                'prev_price': uniswap_eth_last_price
            },
            'Dfusion': {
                'cur_price': dfusion_eth_price,
                'last_updated': dfusion_eth_timestamp,
                'prev_price': dfusion_eth_last_price
            },
            'Coinbase': {
                'cur_price': coinbase_eth_price,
                'last_updated': coinbase_eth_timestamp,
                'prev_price': coinbase_eth_last_price
            },
            'Tellor': {
                'cur_price': tellor_eth_price,
                'last_updated': tellor_eth_timestamp,
                'prev_price': tellor_eth_last_price
            }
        },
        'BTCUSD': {
            'Maker': {
                'cur_price': maker_btc_price,
                'last_updated': maker_btc_timestamp,
                'prev_price': maker_btc_last_price
            },
            'Chainlink': {
                'cur_price': chainlink_btc_price,
                'last_updated': chainlink_btc_timestamp,
                'prev_price': chainlink_btc_last_price
            },
            'Compound': {
                'cur_price': compound_btc_price,
                'last_updated': compound_btc_timestamp,
                'prev_price': compound_btc_last_price
            },
            'Uniswap': {
                'cur_price': uniswap_btc_price,
                'last_updated': uniswap_btc_timestamp,
                'prev_price': uniswap_btc_last_price
            },
            'Dfusion': {
                'cur_price': dfusion_btc_price,
                'last_updated': dfusion_btc_timestamp,
                'prev_price': dfusion_btc_last_price
            },
            'Coinbase': {
                'cur_price': coinbase_btc_price,
                'last_updated': coinbase_btc_timestamp,
                'prev_price': coinbase_btc_last_price
            },
            'Tellor': {
                'cur_price': tellor_btc_price,
                'last_updated': tellor_btc_timestamp,
                'prev_price': tellor_btc_last_price
            }
        },
        'BATUSD': {
            'Maker': {
                'cur_price': maker_bat_price,
                'last_updated': maker_bat_timestamp,
                'prev_price': maker_bat_last_price
            },
            'Chainlink': {
                'cur_price': chainlink_bat_price,
                'last_updated': chainlink_bat_timestamp,
                'prev_price': chainlink_bat_last_price
            },
            'Compound': {
                'cur_price': compound_bat_price,
                'last_updated': compound_bat_timestamp,
                'prev_price': float(compound_bat_last_price)
            },
            'Uniswap': {
                'cur_price': uniswap_bat_price,
                'last_updated': uniswap_bat_timestamp,
                'prev_price': uniswap_bat_last_price
            }
        }
    }

    json_data = json.dumps(prices)
    return json_data


'''
Get historical data from db
'''


def get_historical_data(switch, token):
    # I'm too fucking lazy to implement a switcher so...
    if switch is 0:
        # Maker
        result = []
        if token == 'ETH':
            table = models.maker.MakerETH
        elif token == 'BTC':
            table = models.maker.MakerBTC
        else:
            table = models.maker.MakerBAT
        for instance in db.session.query(table).order_by(table.blocknumber):
            str = {
                'blocknumber': instance.blocknumber,
                'timestamp': instance.timestamp,
                'price': instance.price
            }
            result.append(str)

        return result
    elif switch is 1:
        # Chainlink
        result = []
        if token == 'ETH':
            table = models.chainlink.ChainlinkETH
        elif token == 'BTC':
            table = models.chainlink.ChainlinkBTC
        else:
            table = models.chainlink.ChainlinkBAT
        for instance in db.session.query(table).order_by(table.blocknumber):
            str = {
                'blocknumber': instance.blocknumber,
                'timestamp': instance.timestamp,
                'price': instance.price
            }
            result.append(str)

        return result
    elif switch is 2:
        # Compound
        result = []
        if token == 'ETH':
            table = models.compound.CompoundETH
        elif token == 'BTC':
            table = models.compound.CompoundBTC
        else:
            table = models.compound.CompoundBAT
        for instance in db.session.query(table).order_by(table.blocknumber):
            str = {
                'blocknumber': instance.blocknumber,
                'timestamp': instance.timestamp,
                'price': instance.price
            }
            result.append(str)

        return result
    elif switch is 3:
        # Dfusion
        result = []
        if token == 'ETH':
            table = models.dfusion.DfusionETH
        elif token == 'BTC':
            table = models.dfusion.DfusionBTC
        else:
            table = models.dfusion.DfusionBAT
        for instance in db.session.query(table).order_by(table.blocknumber):
            str = {
                'blocknumber': instance.blocknumber,
                'timestamp': instance.timestamp,
                'price': instance.price
            }
            result.append(str)

        return result
    elif switch is 4:
        # Uniswap
        result = []
        if token == 'ETH':
            table = models.uniswap.UniswapETH
        elif token == 'BTC':
            table = models.uniswap.UniswapBTC
        else:
            table = models.uniswap.UniswapBAT
        for instance in db.session.query(table).order_by(table.blocknumber):
            str = {
                'blocknumber': instance.blocknumber,
                'timestamp': instance.timestamp,
                'price': instance.price
            }
            result.append(str)

        return result
    elif switch is 5:
        # Coinbase
        result = []
        if token == 'ETH':
            table = models.coinbase.CoinbaseETH
        else:
            table = models.coinbase.CoinbaseBTC
        for instance in db.session.query(table).order_by(table.timestamp):
            str = {
                'timestamp': instance.timestamp,
                'price': instance.price
            }
            result.append(str)

        return result
    elif switch is 6:
        # Tellor
        result = []
        if token == 'ETH':
            table = models.tellor.TellorETH
        elif token == 'BTC':
            table = models.tellor.TellorBTC
        for instance in db.session.query(table).order_by(table.blocknumber):
            str = {
                'blocknumber': instance.blocknumber,
                'timestamp': instance.timestamp,
                'price': instance.price
            }
            result.append(str)

        return result


'''
Get latest block number
'''


def get_latest_block_number():
    global api_key
    while api_key is None:
        print('latest')
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
Update eth price
'''


def update_eth_price():
    maker_methods.get_maker_price()
    chainlink_eth_price, _, _ = chainlink_methods.get_chainlink_price()
    eth_price, _, _ = compound_methods.get_compound_price()
    uniswap_eth_price = uniswap_methods.get_uniswap_price()
    dfusion_methods.get_dfusion_price()
    coinbase_methods.get_coinbase_price()
    tellor_methods.get_tellor_price()

    return eth_price, chainlink_eth_price, uniswap_eth_price


'''
Update btc price
'''


def update_btc_price(compound_eth_price, uniswap_eth_price):
    maker_methods.get_maker_btc_price()
    chainlink_methods.get_chainlink_btc_price()
    compound_methods.get_compound_btc_price(compound_eth_price)
    uniswap_methods.get_uniswap_btc_price(uniswap_eth_price)
    dfusion_methods.get_dfusion_btc_price()
    coinbase_methods.get_coinbase_btc_price()
    tellor_methods.get_tellor_btc_price()


'''
Update bat price
'''


def update_bat_price(compound_eth_price, chainlink_eth_price, uniswap_eth_price):
    maker_methods.get_maker_bat_price()
    chainlink_methods.get_chainlink_bat_price(chainlink_eth_price)
    compound_methods.get_compound_bat_price(compound_eth_price)
    uniswap_methods.get_uniswap_bat_price(uniswap_eth_price)
    dfusion_methods.get_dfusion_bat_price()


'''
Update current oracle prices every minute
'''


def update_all_prices():
    while True:
        print('Fetching data')
        try:
            compound_eth_price, chainlink_eth_price, uniswap_eth_price = update_eth_price()
            update_btc_price(compound_eth_price, uniswap_eth_price)
            update_bat_price(compound_eth_price,
                             chainlink_eth_price, uniswap_eth_price)
        except:
            print("error fetching data, passing")
            pass

        time.sleep(30)


'''
Websocket server responses
'''


async def respond(websocket, path):
    while True:
        json_data = get_data_websocket()
        try:
            await websocket.send(json_data)
        except:
            print("There was an error, passing")
            pass
        await asyncio.sleep(60)


'''
Start websocket
'''


def start_loop(loop, server):
    loop.run_until_complete(server)
    loop.run_forever()


'''
Populate Database Tables
'''


def populate_tables():
    chainlink_methods.populate_chainlink()
    maker_methods.populate_maker()
    compound_methods.populate_compound()
    dfusion_methods.populate_dfusion()
    uniswap_methods.populate_uniswap()
    tellor_methods.populate_tellor()
    print('Done populating tables')


'''
Create DB
'''


def create_db():
    # Create all tables
    db.create_all()
    db.session.commit()

    # Populate tables
    populate_tables()


if __name__ == '__main__':
    # Upon startup create and populate DB
    # If file exists, DB has been created, read from and update DB
    # If not, make file, populate db
    db.init_app(app)

    try:
        f = open('db_exists.txt')
        f.close()
    except FileNotFoundError:
        # Create current block files upon startup
        maker_methods.create_maker_files()
        compound_methods.create_compound_files()
        uniswap_methods.create_uniswap_files()
        dfusion_methods.create_dfusion_files()
        chainlink_methods.create_chainlink_files()
        coinbase_methods.create_coinbase_files()
        tellor_methods.create_tellor_files()

        create_db()
        open('db_exists.txt', "w")

    # Create websocket on separate thread send updates every minute w/ current prices
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # ssl_context.load_cert_chain('')

    print('Starting websocket')
    websocket_loop = asyncio.new_event_loop()
    start_server = websockets.serve(
        respond, '0.0.0.0', 5678, loop=websocket_loop, ssl=ssl_context)
    t = Thread(target=start_loop, args=(websocket_loop, start_server))
    t.start()

    # Fetch new prices upon startup
    fetch_thread = Thread(target=update_all_prices, args=(), daemon=True)
    fetch_thread.start()

    # Start flask app
    app.run(host="0.0.0.0", port=443, ssl_context=ssl_context,
            threaded=True, use_reloader=False)
