from .create_db import db

class UniswapETH(db.Model):
    __tablename__ = 'uniswap'

    id = db.Column('id', db.Integer, primary_key=True)
    blocknumber = db.Column('blocknumber', db.Integer)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.blocknumber, self.timestamp, self.price)

class UniswapBTC(db.Model):
    __tablename__ = 'uniswapbtc'

    id = db.Column('id', db.Integer, primary_key=True)
    blocknumber = db.Column('blocknumber', db.Integer)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.blocknumber, self.timestamp, self.price)

class UniswapBAT(db.Model):
    __tablename__ = 'uniswapbat'

    id = db.Column('id', db.Integer, primary_key=True)
    blocknumber = db.Column('blocknumber', db.Integer)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.blocknumber, self.timestamp, self.price)
