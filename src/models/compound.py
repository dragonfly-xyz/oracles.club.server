from .create_db import db

class CompoundETH(db.Model):
    __tablename__ = 'compound'

    id = db.Column('id', db.Integer, primary_key=True)
    blocknumber = db.Column('blocknumber', db.Integer)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.blocknumber, self.timestamp, self.price)

class CompoundBTC(db.Model):
    __tablename__ = 'compoundbtc'

    id = db.Column('id', db.Integer, primary_key=True)
    blocknumber = db.Column('blocknumber', db.Integer)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.blocknumber, self.timestamp, self.price)

class CompoundBAT(db.Model):
    __tablename__ = 'compoundbat'

    id = db.Column('id', db.Integer, primary_key=True)
    blocknumber = db.Column('blocknumber', db.Integer)
    timestamp = db.Column('timestamp', db.Integer)
    price = db.Column('price', db.Float)

    def __repr__(self):
        return '{}, {}, {}'.format(self.blocknumber, self.timestamp, self.price)
