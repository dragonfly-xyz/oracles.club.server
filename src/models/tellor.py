from .create_db import db

# Table Definitions
class TellorETH(db.Model):
    __tablename__ = 'tellor'

    id = db.Column('id', db.Integer, primary_key=True)
    blocknumber = db.Column('blocknumber', db.Integer)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.blocknumber, self.timestamp, self.price)

class TellorBTC(db.Model):
    __tablename__ = 'tellorbtc'

    id = db.Column('id', db.Integer, primary_key=True)
    blocknumber = db.Column('blocknumber', db.Integer)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.blocknumber, self.timestamp, self.price)
