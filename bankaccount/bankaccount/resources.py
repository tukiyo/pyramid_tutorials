from sqlalchemy.orm.exc import NoResultFound
from . import models

class Root(object):
    def __init__(self,request):
        self.request = request

    def get_bankaccount(self):
        try:
            return models.DBSession.query(models.BankAccount).filter_by(name=u'default').one()
        except NoResultFound:
            return None