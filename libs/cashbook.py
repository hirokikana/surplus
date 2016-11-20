import json
from tables import CashBook, User, BurdenRateString, BurdenRateItemId
from application import app
from sqlalchemy.orm import sessionmaker

class CashBookAccess():
    def __init__(self):
        self.session = sessionmaker(bind=app.config['db_engine'])()

    def get_all(self):
        result = self.__to_array(self.session.query(CashBook).
                                 all())
        return json.dumps(result)

    def find_by_user_id(self, user_id):
        result = []
        for burden_rate_row in self.session.query(BurdenRateString).filter(BurdenRateString.user_id == user_id).all():
            rate = burden_rate_row.rate / 100.0
            for row in self.__to_array(self.session.query(CashBook).
                                       filter(CashBook.item.like('%%%s%%' % burden_rate_row.item_string)).
                                       all()
            ):
                row['expense'] *= rate
                result.append(row)
        return json.dumps(result)

    def find_by_user_id_and_date_range(self, user_id, start_date, end_date):
        result = []
        for burden_rate_row in self.session.query(BurdenRateString).filter(BurdenRateString.user_id == user_id).all():
            rate = burden_rate_row.rate / 100.0
            for row in self.__to_array(self.session.query(CashBook).
                                       filter(CashBook.item.like('%%%s%%' % burden_rate_row.item_string)).
                                       filter(CashBook.use_date >= start_date).
                                       filter(CashBook.use_date < end_date).
                                       all()
            ):
                row['expense'] *= rate
                result.append(row)
        return json.dumps(result)

    def find_by_date_range(self, start_date, end_date):
        result = self.__to_array(self.session.query(CashBook).
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
