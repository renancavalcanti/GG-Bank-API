from flask import Blueprint, request, jsonify
import json
import asyncio
import re

from flask.helpers import stream_with_context

from src.views.middleware.tokenValidation import validateJWT

from src.controllers.accountController import activateAccount, createAccount , loginAccount, getBalance, getAccounts, getAccountInfo

account = Blueprint('account', __name__)

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def checkEmail(email):
    if(re.fullmatch(regex, email)):
        return True
 
    else:
        return False
 

def validateRequest(request: None):
    try:
        if not request['firstName']:
            return False
        
        if not request['lastName']:
            return False
        
        if not request['email']:
            return False

        if not request['mobilePhone']:
            return False
        
        if not request['password']:
            return False

        return True

    except Exception as e:
        return (f'Raised exception: {e}')


@account.route('/v1/accounts/auth', methods=['POST'])
def Login():
    try:
        if not request.data:
            raise 'Request error'

        dataReceived = json.loads(request.data)

        if not dataReceived['email']:
            return jsonify({"error": 'Email not found in the request'}), 400  

        if not dataReceived['password']:
            return jsonify({"error": 'Password not found in the request'}), 400     

        authorizationReturn = asyncio.run(loginAccount(dataReceived))

        if authorizationReturn == 'Invalid password':
            return jsonify({"error": 'Invalid credentials'}), 401  

        if authorizationReturn == 'Invalid email':
            return jsonify({"error": 'There is no account with the email provided'}), 401  

        if authorizationReturn == 'Not activated':
            return jsonify({"error": 'The account is not activated yet'}), 420              

        return jsonify({'token': authorizationReturn.json['token'] , 'expiration': authorizationReturn.json['expiration']}), 200

    except ValueError as err:
        return jsonify({"error": 'Error creating login session, please try again'}), 400

@account.route('/v1/accounts/activate', methods=['POST'])       
def Activate():
    try:
        if not request.data:
            return jsonify({"error": 'There is no data in the request' }), 400

        dataReceived = json.loads(request.data)

        result = asyncio.run(activateAccount(dataReceived))        

        if result == 'Invalid email':
            return jsonify({"error": 'There is no account with the email provided'}), 401  

        if result == 'Invalid activation code':
            return jsonify({"error": 'Invalid activation code'}), 401  

        if result == 'Already activated':
            return jsonify({"error": 'Account already activated'}), 401  
        
        if result == 'Error':
            raise ValueError('Error activating account')
        
        return jsonify({"result": 'Account successful activated'}), 200
        
    except ValueError as err:
        return jsonify({"error": 'Error activating account, please try again'}), 400

@account.route('/v1/accounts/create', methods=['POST'])
def Account():
    try:
        if not request.data:
            return jsonify({"error": 'There is no data in the request' }), 400

        dataReceived = json.loads(request.data)

        if not validateRequest(dataReceived):
            return jsonify({"error": 'Error validating form, invalid data' }), 400
            
        if not checkEmail(dataReceived['email']):
            return jsonify({"error": 'Invalid email in the request'}), 400  
        
        createdAccount = asyncio.run(createAccount(dataReceived))
        
        if createdAccount == 'Duplicate Account':
            return jsonify({"error": 'There is already an account with the data informed'}), 400
        
        if not createdAccount.inserted_id:
            return jsonify({"error": 'Error creating account, please try again' }), 500

        return jsonify({'accountId': f'{str(createdAccount.inserted_id)}'}), 200

    except ValueError as err:
        return jsonify({"error": 'Error creating account, please try again'}), 400

@account.route('/v1/accounts/info', methods=['GET'])    
def returnAccounts():
    try:
        token = validateJWT()

        if token == 400:
            return jsonify({"error": 'Token is missing in the request, please try again'}), 401

        if token == 401:
            return jsonify({"error": 'Invalid authentication token, please login again'}), 403

        accounts = []
        accounts = asyncio.run(getAccounts())

        return jsonify({'accounts': accounts})
    
    except ValueError as err:
        return jsonify({"error": 'Error returning accounts information, please try again'}), 400

@account.route('/v1/accounts/info/<email>', methods=['GET'])    
def returnAccount(email):

    try:
        token = validateJWT()

        if token == 400:
            return jsonify({"error": 'Token is missing in the request, please try again'}), 401

        if token == 401:
            return jsonify({"error": 'Invalid authentication token, please login again'}), 403

        if not email:
             return jsonify({"error": 'Email not find in the request, please try again'}), 400

        emailToFind = email.lower()
        account = asyncio.run(getAccountInfo(emailToFind, True))
        if account == 'Not found': 
            return jsonify({'error': 'Account not found' }), 404        

        return jsonify({'account': account})

    except ValueError as err:
        return jsonify({"error": 'Error returning account information, please try again'}), 400

@account.route('/v1/accounts/balance', methods=['GET'])    
def returnBalance():
    
    try:
        token = validateJWT()

        if token == 400:
            return jsonify({"error": 'Token is missing in the request, please try again'}), 401

        if token == 401:
            return jsonify({"error": 'Invalid authentication token, please login again'}), 403
        
        accountToFind = token['email'].lower()
        accountBalance = asyncio.run(getBalance(accountToFind))

        return jsonify({'balance': accountBalance['balance'], 'finalBalance': accountBalance['finalBalance']}), 200

    except ValueError as err:
        return jsonify({"error": 'Error returning account information, please try again'}), 400

