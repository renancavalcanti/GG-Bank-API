from datetime import datetime, timedelta
import uuid
import asyncio
import src.globalvars as globalvars

from src.models.transactionModel import Transaction

from src.controllers.accountController import addFundsToAccount, addLoanDebt, getBalance, removeFundsFromAccount

from src.services.database import MongoDB
from src.services.__init__ import database

def generateRandomTransactionId() -> str :
  accountID = str(uuid.uuid4().hex)

  return accountID

async def makeTransfer(accountOwner, destinationAccount, amount: float, message: str) -> bool:
    transferToMake = None
    try:
        transferToMake = Transaction()

        transferToMake.type = 'TRANSFER'
        transferToMake.amount = amount
        transferToMake.dateTime = datetime.now()
        transferToMake.fromAccount = {
            'accountId': accountOwner['accountId'],
            'firstName': accountOwner['firstName'],
            'lastName': accountOwner['lastName'],
            'mobilePhone': accountOwner['mobilePhone'],
            'email': accountOwner['email'].lower()
        }
        transferToMake.toAccount = {
            'accountId': destinationAccount['accountId'],
            'firstName': destinationAccount['firstName'],
            'lastName': destinationAccount['lastName'],
            'mobilePhone': destinationAccount['mobilePhone'],
            'email': destinationAccount['email'].lower()
        }
        transferToMake.transactionId = generateRandomTransactionId()
        transferToMake.message = message

        dataBaseConnection = database.dataBase()[globalvars.CONST_TRANSACTION_COLLECTION]   

        transferMade = dataBaseConnection.insert_one(transferToMake.__dict__)

        return transferMade

    except Exception as e:
        raise ValueError('Error in the transaction, please try again')    

async def makeDeposit(destinationAccount, amount, message) -> bool:
    depositToMake = None
    try:
        depositToMake = Transaction()

        depositToMake.type = 'DEPOSIT'
        depositToMake.amount = amount
        depositToMake.dateTime = datetime.now()
        # fromAccount = toAccount 
        depositToMake.fromAccount = {
            'accountId': destinationAccount['accountId'],
            'firstName': destinationAccount['firstName'],
            'lastName': destinationAccount['lastName'],
            'mobilePhone': destinationAccount['mobilePhone'],
            'email': destinationAccount['email'].lower()
        }
        depositToMake.toAccount = {
            'accountId': destinationAccount['accountId'],
            'firstName': destinationAccount['firstName'],
            'lastName': destinationAccount['lastName'],
            'mobilePhone': destinationAccount['mobilePhone'],
            'email': destinationAccount['email'].lower()
        }
        depositToMake.transactionId = generateRandomTransactionId()
        depositToMake.message = message

        dataBaseConnection = database.dataBase()[globalvars.CONST_TRANSACTION_COLLECTION]   

        depositMade = dataBaseConnection.insert_one(depositToMake.__dict__)

        return depositMade

    except Exception as e:
        raise ValueError('Error depositing')    

async def makeWithdraw(destinationAccount, amount) -> bool:
    withdrawToMake = None
    try:
        withdrawToMake = Transaction()

        withdrawToMake.type = 'WITHDRAW'
        withdrawToMake.amount = amount
        withdrawToMake.dateTime = datetime.now()
        # fromAccount = toAccount 
        withdrawToMake.fromAccount = {
            'accountId': destinationAccount['accountId'],
            'firstName': destinationAccount['firstName'],
            'lastName': destinationAccount['lastName'],
            'mobilePhone': destinationAccount['mobilePhone'],
            'email': destinationAccount['email'].lower()
        }
        withdrawToMake.toAccount = {
            'accountId': destinationAccount['accountId'],
            'firstName': destinationAccount['firstName'],
            'lastName': destinationAccount['lastName'],
            'mobilePhone': destinationAccount['mobilePhone'],
            'email': destinationAccount['email'].lower()
        }
        withdrawToMake.transactionId = generateRandomTransactionId()
        withdrawToMake.message = ''

        dataBaseConnection = database.dataBase()[globalvars.CONST_TRANSACTION_COLLECTION]   

        withdrawMade = dataBaseConnection.insert_one(withdrawToMake.__dict__)

        return withdrawMade

    except:
        raise ValueError('Error depositing')    

async def makeLoan(destinationAccount, amount) -> bool:
    depositToMake = None
    try:
        depositToMake = Transaction()

        depositToMake.type = 'LOAN'
        depositToMake.amount = amount
        depositToMake.dateTime = datetime.now()
        # fromAccount = toAccount
        depositToMake.fromAccount = {
            'accountId': destinationAccount['accountId'],
            'firstName': destinationAccount['firstName'],
            'lastName': destinationAccount['lastName'],
            'mobilePhone': destinationAccount['mobilePhone'],
            'email': destinationAccount['email'].lower()
        }
        depositToMake.toAccount = {
            'accountId': destinationAccount['accountId'],
            'firstName': destinationAccount['firstName'],
            'lastName': destinationAccount['lastName'],
            'mobilePhone': destinationAccount['mobilePhone'],
            'email': destinationAccount['email'].lower()
        }
        depositToMake.transactionId = generateRandomTransactionId()
        depositToMake.message = ''

        dataBaseConnection = database.dataBase()[globalvars.CONST_TRANSACTION_COLLECTION]   

        depositMade = dataBaseConnection.insert_one(depositToMake.__dict__)

        return depositMade

    except Exception as e:
        raise ValueError('Error depositing')    

async def getStatement(account, days) -> list:
    try:
        statementList = []

        dataBaseConnection = database.dataBase()[globalvars.CONST_TRANSACTION_COLLECTION]   

        today = datetime.now()
        toDate = datetime(today.year, today.month, today.day) + timedelta(days= 1)
        fromDate = toDate - timedelta(days= int(days))
        
        filter = {"dateTime": {'$lt': toDate, '$gte': fromDate }, "$or": [{"fromAccount.accountId": account},{ "toAccount.accountId": account}]}
        for statement in dataBaseConnection.find(filter):
            statementObject = {}

            statementObject.update({ "type": statement['type'] })
            statementObject.update({ "amount": statement['amount'] })
            
            date = statement['dateTime']
            statementObject.update({ "dateTime": date.isoformat() })
            statementObject.update({ "fromAccount": statement['fromAccount'] })
            statementObject.update({ "toAccount": statement['toAccount'] })
            statementObject.update({ "transactionId": statement['transactionId'] })
            statementObject.update({ "message": statement['message'] })
            
            statementList.append(
                statementObject
            )

        return statementList

    except ValueError as err:
        return err