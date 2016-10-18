#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('libs')
from bottle import route,run,template,request,static_file,view
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
        result = []
        for burden_rate_row in session.query(BurdenRateString).filter(BurdenRateString.user_id == user_id).all():
            rate = burden_rate_row.rate / 100.0
            for row in self.__to_array(session.query(CashBook).
                                       filter(CashBook.item.like('%%%s%%' % burden_rate_row.item_string)).
                                       all()
            ):
                row['expense'] *= rate
                result.append(row)
        return json.dumps(result)

    def find_by_user_id_and_date_range(self, user_id, start_date, end_date):
        result = []
        for burden_rate_row in session.query(BurdenRateString).filter(BurdenRateString.user_id == user_id).all():
            rate = burden_rate_row.rate / 100.0
            for row in self.__to_array(session.query(CashBook).
                                       filter(CashBook.item.like('%%%s%%' % burden_rate_row.item_string)).
                                       filter(CashBook.use_date >= start_date).
                                       filter(CashBook.use_date < end_date).
                                       all()
            ):
                row['expense'] *= rate
                result.append(row)
        return json.dumps(result)

    def find_by_date_range(self, start_date, end_date):
        result = self.__to_array(session.query(CashBook).
                                 filter(CashBook.use_date >= start_date).
                                 filter(CashBook.use_date < end_date).
                                 all())
        return json.dumps(result)

    def __to_array(self, rows):
        result = []
        for row in rows:
            result.append({
                'id':row.id,
                'use_date':row.use_date.isoformat(),
                'item':row.item,
                'expense':row.expense,
                'income':row.income,
                'payment_type':row.payment_type,
                'payment_id':row.payment_id
            })
        return result


@route('/')
def index():
    return template('index', title="TOP")

@route('/api/v1/cashbook', method='POST')
def post_cashbook():
    # nkf -m0Z1 ~/hoge.csv|grep '^[0-9]'|awk -F',' '{print "hoge,"$1","$4","$5","$6}'
    # CSV format : payment_type, payment_id, use_date, item, expense
    # test : curl -X POST -F csv=@hoge.csv http://localhost:8080/api/v1/cashbook  
    reader = csv.reader(request.files.get('csv').file)
    for row in reader:
        payment_type = row[0]
        payment_id = row[1]
        use_date = datetime.datetime.strptime(row[2], '%Y/%m/%d').date()
        item = row[3].decode('utf-8')
        expense = row[4]
        session.add(CashBook(payment_type=payment_type, payment_id=payment_id, item=item, expense=expense, use_date=use_date))
    session.commit()

@route('/api/v1/cashbook')
def get_cashbook():
    return template('{{!json}}', json=CashBookAccess().get_all())

@route('/api/v1/cashbook/<year:int>')
def cashbook_find_by_year(year):
    start_date = '%d-01' % (year)
    end_date = '%d-01' % (year + 1)
    return template('{{!json}}', json=CashBookAccess().find_by_date_range(start_date, end_date))

@route('/api/v1/cashbook/<year:int>/<month:int>')
def cashbook_find_by_month(year, month):
    start_date = '%d-%02d' % (year, month)
    end_date = '%d-%02d' % (year, month + 1)
    return template('{{!json}}', json=CashBookAccess().find_by_date_range(start_date, end_date))

@route('/api/v1/user/<user_id:int>')
def cashbook_find_by_user(user_id):
    return template('{{!json}}', json=CashBookAccess().find_by_user_id(user_id))

@route('/api/v1/user/<user_id:int>/<year:int>')
def cashbook_find_by_user_year(user_id, year):
    start_date = '%d-01' % (year)
    end_date = '%d-01' % (year + 1)
    return template('{{!json}}', json=CashBookAccess().find_by_user_id_and_date_range(user_id, start_date, end_date))

@route('/api/v1/user/<user_id:int>/<year:int>/<month:int>')
def cashbook_find_by_user_year_month(user_id, year, month):
    start_date = '%d-%02d' % (year, month)
    end_date = '%d-%02d' % (year, month+1)
    return template('{{!json}}', json=CashBookAccess().find_by_user_id_and_date_range(user_id, start_date, end_date))

@route('/api/v1/burdenrate/item_string', method='POST')
def set_burden_rate_item_string():
    user_id = request.forms.get('user_id')
    item_string = request.forms.get('item_string').decode('utf-8')
    rate = request.forms.get('rate')
    session.add(BurdenRateString(item_string=item_string, rate=rate, user_id=user_id))
    session.commit()
    return template('{"result":"ok"}')

@route('/api/v1/burdenrate/item_id', method='POST')
def set_burnden_rate_item_id():
    user_id = request.forms.get('user_id')
    item_id = request.forms.get('item_id')
    rate = request.forms.get('rate')
    session.add(BurdenRateItemId(item_id=item_id, rate=rate, user_id=user_id))
    session.commit()
    return template('{"result":"ok"}')
    
@route('/api/v1/burdenrate/user/<user_id:int>')
def get_burden_rate(user_id):
    result_string = session.query(BurdenRateString).filter(BurdenRateString.user_id == user_id).all()
    result_item_id = session.query(BurdenRateItemId).filter(BurdenRateItemId.user_id == user_id).all()
    session.commit()
    result = [{'id':x.id,'item_string':x.item_string,'rate':x.rate} for x in result_string] + [{'id':x.id,'item_id':x.item_id,'rate':x.rate} for x in result_item_id]
    return template('{{!json}}', json=json.dumps(result))

@route('/static/<filepath:path>')
def static(filepath):
    return static_file(filepath, root="./static")


Base = declarative_base()

class CashBook(Base):
    __tablename__ = 'cashbook'
    id = Column(Integer, primary_key=True)
    payment_type = Column(String)
    payment_id = Column(Integer)
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
