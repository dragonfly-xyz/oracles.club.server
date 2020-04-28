from .create_db import db


class CoinbaseETH(db.Model):
    __tablename__ = 'coinbase'

    id = db.Column('id', db.Integer, primary_key=True)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.timestamp, self.price)

class CoinbaseBTC(db.Model):
    __tablename__ = 'coinbasebtc'

    id = db.Column('id', db.Integer, primary_key=True)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.timestamp, self.price)
