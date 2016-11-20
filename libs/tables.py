from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CashBook(Base):
    __tablename__ = 'cashbook'
    id = Column(Integer, primary_key=True)
    payment_type = Column(String(1024))
    payment_id = Column(Integer)
    use_date = Column(Date)
    item = Column(String(1024))
    income = Column(Integer, default=0)
    expense = Column(Integer, default=0)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(1024))

class BurdenRateString(Base):
    __tablename__ = 'burdenrate_string'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    item_string = Column(String(1024))
    rate = Column(Integer)

class BurdenRateItemId(Base):
    __tablename__ = 'burdenrate_item_id'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    item_id = Column(String(1024))
    rate = Column(Integer)
