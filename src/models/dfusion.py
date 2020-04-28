from .create_db import db


class DfusionETH(db.Model):
    __tablename__ = 'dfusion'

    id = db.Column('id', db.Integer, primary_key=True)
    blocknumber = db.Column('blocknumber', db.Integer)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.blocknumber, self.timestamp, self.price)

class DfusionBTC(db.Model):
    __tablename__ = 'dfusionbtc'

    id = db.Column('id', db.Integer, primary_key=True)
    blocknumber = db.Column('blocknumber', db.Integer)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.blocknumber, self.timestamp, self.price)

class DfusionBAT(db.Model):
    __tablename__ = 'dfusionbat'

    id = db.Column('id', db.Integer, primary_key=True)
    blocknumber = db.Column('blocknumber', db.Integer)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.blocknumber, self.timestamp, self.price)





'''
Get all dfusion prices
'''
def get_dfusion_prices():
    dfusion_instance = db.session.query(DfusionETH).order_by(DfusionETH.blocknumber.desc()).limit(10)[-10:]
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

    dfusion_btc_instance = db.session.query(DfusionBTC).order_by(DfusionBTC.blocknumber.desc()).limit(10)[-10:]
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
