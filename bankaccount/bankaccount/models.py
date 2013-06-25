import sqlahelper
import sqlalchemy as sa

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

class NotEnoughFunds(Exception):
    pass

class BankAccount(Base):
    __tablename__ = 'bankaccounts'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(255), unique=True)
    balance = sa.Column(sa.Integer, default=0)

    def __init__(self, name):
        super(BankAccount, self).__init__(name=name, balance=0)

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self,amount):
        if self.balance - amount < 0:
            raise NotEnoughFunds
        self.balance -= amount