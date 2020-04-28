from .create_db import db

class ChainlinkETH(db.Model):
    __tablename__ = 'chainlink'

    id = db.Column('id', db.Integer, primary_key=True)
    blocknumber = db.Column('blocknumber', db.Integer)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.blocknumber, self.timestamp, self.price)

class ChainlinkBTC(db.Model):
    __tablename__ = 'chainlinkbtc'

    id = db.Column('id', db.Integer, primary_key=True)
    blocknumber = db.Column('blocknumber', db.Integer)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.blocknumber, self.timestamp, self.price)

class ChainlinkBAT(db.Model):
    __tablename__ = 'chainlinkbat'

    id = db.Column('id', db.Integer, primary_key=True)
    blocknumber = db.Column('blocknumber', db.Integer)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.blocknumber, self.timestamp, self.price)
