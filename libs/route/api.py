from application import app
from bottle import route,template
from cashbook import CashBookAccess
import csv
import datetime

@app.route('/api/v1/cashbook', method='POST')
def post_cashbook():
    session = app.config['session']
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

@app.route('/api/v1/cashbook')
def get_cashbook():
    session = app.config['session']
    return template('{{!json}}', json=CashBookAccess().get_all())

@app.route('/api/v1/cashbook/<year:int>')
def cashbook_find_by_year(year):
    session = app.config['session']
    start_date = '%d-01' % (year)
    end_date = '%d-01' % (year + 1)
    return template('{{!json}}', json=CashBookAccess().find_by_date_range(start_date, end_date))

@app.route('/api/v1/cashbook/<year:int>/<month:int>')
def cashbook_find_by_month(year, month):
    session = app.config['session']
    start_date = '%d-%02d' % (year, month)
    end_date = '%d-%02d' % (year, month + 1)
    return template('{{!json}}', json=CashBookAccess().find_by_date_range(start_date, end_date))

@app.route('/api/v1/user/<user_id:int>')
def cashbook_find_by_user(user_id):
    session = app.config['session']
    return template('{{!json}}', json=CashBookAccess().find_by_user_id(user_id))

@app.route('/api/v1/user/<user_id:int>/<year:int>')
def cashbook_find_by_user_year(user_id, year):
    session = app.config['session']
    start_date = '%d-01' % (year)
    end_date = '%d-01' % (year + 1)
    return template('{{!json}}', json=CashBookAccess().find_by_user_id_and_date_range(user_id, start_date, end_date))

@app.route('/api/v1/user/<user_id:int>/<year:int>/<month:int>')
def cashbook_find_by_user_year_month(user_id, year, month):
    session = app.config['session']
    start_date = '%d-%02d' % (year, month)
    end_date = '%d-%02d' % (year, month+1)
    return template('{{!json}}', json=CashBookAccess().find_by_user_id_and_date_range(user_id, start_date, end_date))

@app.route('/api/v1/burdenrate/item_string', method='POST')
def set_burden_rate_item_string():
    session = app.config['session']
    user_id = request.forms.get('user_id')
    item_string = request.forms.get('item_string').decode('utf-8')
    rate = request.forms.get('rate')
    session.add(BurdenRateString(item_string=item_string, rate=rate, user_id=user_id))
    session.commit()
    return template('{"result":"ok"}')

@app.route('/api/v1/burdenrate/item_id', method='POST')
def set_burnden_rate_item_id():
    session = app.config['session']
    user_id = request.forms.get('user_id')
    item_id = request.forms.get('item_id')
    rate = request.forms.get('rate')
    session.add(BurdenRateItemId(item_id=item_id, rate=rate, user_id=user_id))
    session.commit()
    return template('{"result":"ok"}')
    
@app.route('/api/v1/burdenrate/user/<user_id:int>')
def get_burden_rate(user_id):
    session = app.config['session']
    result_string = session.query(BurdenRateString).filter(BurdenRateString.user_id == user_id).all()
    result_item_id = session.query(BurdenRateItemId).filter(BurdenRateItemId.user_id == user_id).all()
    session.commit()
    result = [{'id':x.id,'item_string':x.item_string,'rate':x.rate} for x in result_string] + [{'id':x.id,'item_id':x.item_id,'rate':x.rate} for x in result_item_id]
    return template('{{!json}}', json=json.dumps(result))

