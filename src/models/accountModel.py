from datetime import datetime

class Account(object):
    def __init__(self) -> None:
        self.firstName: str = ''
        self.lastName: str = ''
        self.email: str = ''
        self.password: str = ''
        self.mobilePhone: str = ''
        self.accountId: str = ''
        self.createdAt: datetime = ''
        self.activatedAt: datetime = ''
        self.activationCode: str = ''
        # self.balance: float = 0.00   deprecated
        # self.loanDebt: float = 0.00   deprecated

    

