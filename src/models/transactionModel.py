from datetime import datetime
from enum import Enum

class transactionType(Enum):
    DEPOSIT = 1
    TRANSFER = 2
    WITHDRAW = 3
    LOAN = 4

class Transaction(object):

    def __init__(self) -> None:
        self.type: transactionType = ''
        self.amount: float = ''
        self.dateTime: datetime = ''
        self.fromAccount : dict = {}
        self.toAccount: dict = {}
        self.transactionId: str = ''
        self.message: str = ''
        self.createdAt: datetime = datetime.now()
