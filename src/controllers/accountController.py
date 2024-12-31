import asyncio
from flask.json import jsonify
from src.models.accountModel import Account
from datetime import datetime, timedelta
import random
import uuid
import bcrypt
import jwt

import src.globalvars as globalvars

from src.services.database import MongoDB

from src.services.__init__ import database

def generateRandomActivationCode() -> str:
  try:
    randomNumbers = random.sample(range(0, 9), 5)
    activationCode = ''.join(map(str, randomNumbers))
    
    return activationCode

  except:
    raise ValueError('Failed to create activation code')

def generateRandomAccountId() -> str :
  accountID = str(uuid.uuid4().hex)

  return accountID

def generateHashPassword(password) -> str:
  salt = bcrypt.gensalt()
  hashedPassword = bcrypt.hashpw(password.encode("utf-8"), salt )

  return hashedPassword


async def createAccount(accountInformation) -> str:
    """
      Create an account

    :object = Dict that contains the desired account to be created

        firstName: Owner full name
        lastName: Owner social name
        mobilePhone: Owner contact mobile number
        email: Owner email address
        password: Owner password

    """
    accountToCreate = None
    try:
      accountToCreate = Account()

      accountToCreate.accountId = generateRandomAccountId()
      accountToCreate.firstName = accountInformation['firstName']
      accountToCreate.lastName = accountInformation['lastName']
      accountToCreate.email = accountInformation['email'].lower()
      accountToCreate.mobilePhone = accountInformation['mobilePhone']
      accountToCreate.password = generateHashPassword(accountInformation['password'])
      accountToCreate.createdAt = datetime.now()
      accountToCreate.activatedAt = None
      # accountToCreate.activationCode = generateRandomActivationCode()
      accountToCreate.activationCode = '123456'

      dataBaseConnection = database.dataBase()[globalvars.CONST_ACCOUNT_COLLECTION]

      if dataBaseConnection.find_one({'email': accountToCreate.email}):
        return 'Duplicate Account'
      
      createdAccount = dataBaseConnection.insert_one(accountToCreate.__dict__)
      return createdAccount

    except Exception as e:
      raise ValueError('Error creating account:' f'{e}')    

async def activateAccount(accountInformation) -> str:
  try:
    email = accountInformation['email'].lower()
    activationCode = accountInformation['activationCode']

    dataBaseConnection = database.dataBase()[globalvars.CONST_ACCOUNT_COLLECTION]   

    account = dataBaseConnection.find_one({'email': email})

    if not account:
      return 'Invalid email'

    if account['activatedAt'] != None:
      return 'Already activated'      
    
    if account['activationCode'] != activationCode:
      return 'Invalid activation code'

    today = datetime.now()
    filter = {"email": email }    

    activated = dataBaseConnection.update_one(filter,{'$set': {'activatedAt': today}}, upsert=False)

    if not activated:
      return 'Error'
    
    return 'Success'

  except Exception as e:
    raise ValueError('Error activating account') 


async def loginAccount(accountInformation) -> str:
  try:
    email = accountInformation['email'].lower()
    password = accountInformation['password'].encode("utf-8")

    dataBaseConnection = database.dataBase()[globalvars.CONST_ACCOUNT_COLLECTION]   

    account = dataBaseConnection.find_one({'email': email})

    if not account:
      return 'Invalid email'    

    if not bcrypt.checkpw(password, account['password']):
      return 'Invalid password'
    
    if account['activatedAt'] is None:
      return 'Not activated'
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")    

    expiration = datetime.utcnow() + timedelta(seconds=globalvars.JWT_EXPIRATION)

    jwtData = { 'email': account['email'], 'firstName': account['firstName'] , 'lastName': account['lastName'] , 'mobilePhone': account['mobilePhone'], 'accountId': account['accountId'], 'generationDate': current_time, 'exp': expiration }

    jwtToReturn = jwt.encode(payload= jwtData ,key= globalvars.TOKEN_SECRET)

    return jsonify({'token': jwtToReturn, 'expiration': globalvars.JWT_EXPIRATION})

  except Exception as e:
    raise ValueError('Error generating JWT') 

async def getBalance(email):
  try:
    balance = 0
    finalBalance = 0
    dataBaseConnection = database.dataBase()[globalvars.CONST_TRANSACTION_COLLECTION]   

    today = datetime.now()
    toDate = datetime(today.year, today.month, today.day, today.hour, today.minute) + timedelta(minutes = 1)
    
    filter = {"$or": [{"fromAccount.email": email},{ "toAccount.email": email}]}
    for statement in dataBaseConnection.find(filter):
      
      if statement['type'] == 'TRANSFER':

        if statement['fromAccount']['email'] == email:
          if statement['dateTime'] < toDate:
            balance -= statement['amount']
          
          finalBalance -= statement['amount']
        else:
          if statement['dateTime'] < toDate:
            balance += statement['amount']
          
          finalBalance += statement['amount']

      if statement['type'] == 'DEPOSIT':
        if statement['dateTime'] < toDate:
          balance += statement['amount']
        
        finalBalance += statement['amount']

      if statement['type'] == 'WITHDRAW':
        if statement['dateTime'] < toDate:        
          balance -= statement['amount']

        finalBalance -= statement['amount']

      if statement['type'] == 'LOAN':
        if statement['dateTime'] < toDate:        
          balance += statement['amount']
        
        finalBalance += statement['amount']
    
    return ({ 'balance': balance, 'finalBalance': finalBalance })

  except:
    raise ValueError('Error getting account balance')

async def getAccounts() -> list:
  try:
    accounts = []

    dataBaseConnection = database.dataBase()[globalvars.CONST_ACCOUNT_COLLECTION]   

    for account in dataBaseConnection.find():
      accountInfo = {}

      accountInfo.update({'accountId': account['accountId']})
      accountInfo.update({'firstName': account['firstName']})
      accountInfo.update({'lastName': account['lastName']})
      accountInfo.update({'email': account['email']})
      accountInfo.update({'mobilePhone': account['mobilePhone']})
       
      accounts.append(
        accountInfo
      )

    return accounts

  except:
    raise ValueError('Error getting accounts information')

async def getAccountInfo(email: str, sendAccountId: bool = False, sendAccountBalance: bool = False) -> dict:
  try:
    accountInfo = {}

    dataBaseConnection = database.dataBase()[globalvars.CONST_ACCOUNT_COLLECTION]   

    account = dataBaseConnection.find_one({'email': email})

    if not account:
      return 'Not found'

    if sendAccountId:
      accountInfo.update({'accountId': account['accountId']})
    
    if sendAccountBalance:
      accountInfo.update({'balance': account.get('balance', 0)})

    accountInfo.update({'firstName': account['firstName']})
    accountInfo.update({'lastName': account['lastName']})
    accountInfo.update({'email': account['email']})
    accountInfo.update({'mobilePhone': account['mobilePhone']})

    return accountInfo

  except Exception as ex:
    raise ValueError('Error getting account information', ex)

def addFundsToAccount(account: str, amount: float) -> bool:
    try:

      dataBaseConnection = database.dataBase()[globalvars.CONST_ACCOUNT_COLLECTION]   
    
      filter = {'email': account['email']}
    
      update = account['balance'] + amount
      
      account = dataBaseConnection.update_one(filter,{'$set': {'balance': update}}, upsert=False)

      return True

    except:
      raise ValueError('Erro adding funds to account')

def removeFundsFromAccount(account: str, amount: float) -> bool:
    try:
      
      dataBaseConnection = database.dataBase()[globalvars.CONST_ACCOUNT_COLLECTION]   
    
      filter = {'email': account}
    
      update = int(account['balance']) - amount
      
      account = dataBaseConnection.update_one(filter,{'$set': {'balance': update}}, upsert=False)

      return True
    
    except Exception as e:
      raise ValueError('Erro removing funds to account')

def addLoanDebt(account: str, amount: float) -> bool:
  try:

    dataBaseConnection = database.dataBase()[globalvars.CONST_ACCOUNT_COLLECTION]   
  
    filter = {'email': account['email']}
  
    update = account['loanDebt'] + amount
    
    account = dataBaseConnection.update_one(filter,{'$set': {'loanDebt': update}}, upsert=False)

    return True

  except:
    raise ValueError('Erro adding funds to account')