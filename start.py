#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('libs')
from bottle import route,run,template,request,static_file
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
import csv
import json
import datetime



class CashBookAccess():
    def get_all(self):
        result = self.__to_array(session.query(CashBook).
                                 all())
        return json.dumps(result)
    
    def find_by_user_id(self, user_id):
        total_result = []
        for row in session.query(BurdenRate).filter(BurdenRate.user_id == user_id).all():
            rate = row.rate / 100.0
            result.append(self.__to_array(session.query(CashBook).
                                          filter(CashBook.item.like('%%%s%%' % row.item_string)).
                                          all()),
                          lambda x:x.update({'expense':x['expense'] * rate})
            )
        return json.dumps(result)

    def find_by_user_id_and_date_range(self, user_id, start_date, end_date):
        pass

    def find_by_date_range(self, start_date, end_date):
        result = self.__to_array(session.query(CashBook).
                                 filter(CashBook.use_date >= start_date).
                                 filter(CashBook.use_date < end_date).
                                 all())
        return json.dumps(result)

    def __to_array(self, rows, func=lambda x:x):
        result = []
        for row in rows:
            result.append(func({
                'id':row.id,
                'use_date':row.use_date.isoformat(),
                'item':row.item,
                'expense':row.expense,
                'income':row.income
            }))
        return result


@route('/')
def index():
    return static_file('index.html', root='./static')

@route('/api/v1/cashbook', method='POST')
def post_cashbook():
    # nkf -m0Z1 ~/hoge.csv|grep '^[0-9]'|awk -F',' '{print $4","$5","$6}'
    reader = csv.reader(request.files.get('csv').file)
    for row in reader:
        use_date = datetime.datetime.strptime(row[0], '%Y/%m/%d').date()
        item = row[1].decode('utf-8')
        expense = row[2]
        session.add(CashBook(item=item, expense=expense, use_date=use_date))
    session.commit()

@route('/api/v1/cashbook')
def get_cashbook():
    return template('{{!json}}', json=CashBookAccess().get_all())

@route('/api/v1/cashbook/<year:int>')
def cashbook_find_by_year(year):
    result = []
    start_date = '%d-01' % (year)
    end_date = '%d-01' % (year + 1)
    for row in session.query(CashBook).filter(CashBook.use_date >= start_date).filter(CashBook.use_date < end_date).all():
        result.append({'use_date':row.use_date.isoformat(), 'item':row.item, 'expense':row.expense, 'income':row.income})
    return template('{{!json}}', json=json.dumps(result))

@route('/api/v1/cashbook/<year:int>/<month:int>')
def cashbook_find_by_month(year, month):
    result = []
    start_date = '%d-%02d' % (year, month)
    end_date = '%d-%02d' % (year, month + 1)
    for row in session.query(CashBook).filter(CashBook.use_date >= start_date).filter(CashBook.use_date < end_date).all():
        result.append({'use_date':row.use_date.isoformat(), 'item':row.item, 'expense':row.expense, 'income':row.income})
    return template('{{!json}}', json=json.dumps(result))

@route('/api/v1/user/<user_id:int>')
def cashbook_find_by_user(user_id):
    result = []
    for row1 in session.query(BurdenRate).filter(BurdenRate.user_id == user_id).all():
        rate = row1.rate / 100.0
        item_string = row1.item_string
        for row in session.query(CashBook).filter(CashBook.item.like('%%%s%%' % item_string)).all():
            result.append({'use_date':row.use_date.isoformat(), 'item':row.item, 'expense':row.expense * rate, 'income':row.income})
    return template('{{!json}}', json=json.dumps(result))

@route('/api/v1/user/<user_id:int>/<year:int>')
def cashbook_find_by_user_year(user_id, year):
    result = []
    for row1 in session.query(BurdenRate).filter(BurdenRate.user_id == user_id).all():
        rate = row1.rate / 100.0
        item_string = row1.item_string
        start_date = '%d-01' % (year)
        end_date = '%d-01' % (year + 1)
        for row in session.query(CashBook).filter(CashBook.item.like('%%%s%%' % item_string)).filter(CashBook.use_date >= start_date).filter(CashBook.use_date < end_date).all():
            result.append({'use_date':row.use_date.isoformat(), 'item':row.item, 'expense':row.expense * rate, 'income':row.income})
    return template('{{!json}}', json=json.dumps(result))

@route('/api/v1/user/<user_id:int>/<year:int>/<month:int>')
def cashbook_find_by_user_year_month(user_id, year, month):
    result = []
    for row1 in session.query(BurdenRate).filter(BurdenRate.user_id == user_id).all():
        rate = row1.rate / 100.0
        item_string = row1.item_string
        start_date = '%d-%02d' % (year, month)
        end_date = '%d-%02d' % (year, month+1)
        for row in session.query(CashBook).filter(CashBook.item.like('%%%s%%' % item_string)).filter(CashBook.use_date >= start_date).filter(CashBook.use_date < end_date).all():
            result.append({'use_date':row.use_date.isoformat(), 'item':row.item, 'expense':row.expense * rate, 'income':row.income})
    return template('{{!json}}', json=json.dumps(result))


Base = declarative_base()

class CashBook(Base):
    __tablename__ = 'cashbook'
    id = Column(Integer, primary_key=True)
    use_date = Column(Date)
    item = Column(String)
    income = Column(Integer, default=0)
    expense = Column(Integer, default=0)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class BurdenRateString(Base):
    __tablename__ = 'burdenrate_string'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    item_string = Column(String)
    rate = Column(Integer)

class BurdenRateItemId(Base):
    __tablename__ = 'burdenrate_item_id'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    item_id = Column(String)
    rate = Column(Integer)

if __name__ == "__main__":
    engine = create_engine('sqlite://', echo=True)
    session = sessionmaker(bind=engine)()
    Base.metadata.create_all(engine)

    if (1): # test
        session.add(User(name='hiroki'))
        session.add(BurdenRateString(user_id=1, item_string='AMAZON', rate=50))
        session.add(BurdenRateString(user_id=1, item_string=u'東京電力', rate=50))
        session.commit()
        
    run(port=8080, debug=True)
