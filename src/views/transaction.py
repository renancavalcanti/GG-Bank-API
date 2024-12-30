from flask import Blueprint, request, jsonify
import json
import asyncio

from src.views.middleware.tokenValidation import validateJWT
from src.controllers.transactionController import getStatement, makeDeposit, makeLoan, makeTransfer, makeWithdraw

from src.controllers.accountController import getAccountInfo, getBalance

transaction = Blueprint('transfer', __name__)

def validateRequest(request: None):
    try:
        if not request['amount']:
            raise 'Amount not found in the request'
 
        if not request['message']:
            raise 'Message not found in the request'

        return True

    except Exception as e:
        return (f'Raised exception: {e}')


@transaction.route('/v1/transactions/transfer/', methods=['POST'])
def transfer():
    try:
        token = validateJWT()

        if token == 400:
            return jsonify({"error": 'Token is missing in the request, please try again'}), 401

        if token == 401:
            return jsonify({"error": 'Invalid authentication token, please login again'}), 403
        
        if not request.data:
            raise 'Request error'

        dataReceived = json.loads(request.data)

        if not validateRequest(dataReceived):
            raise ValueError('Error validating form')

        if token['email'] == dataReceived['account'].lower():
            return jsonify({"error": 'Destination account cannot be the same as the origin account'}), 401

        email = dataReceived['account'].lower()
        amount = dataReceived['amount']
        balance = asyncio.run(getBalance(token['email'].lower()))

        if int(balance['balance']) < amount:
            raise ValueError('Not enough funds')

        message = dataReceived['message']     

        destinationAccount = asyncio.run(getAccountInfo(email, True))     

        if destinationAccount == 'Not found': 
            return jsonify({'error': 'Destination account not found' }), 404

        transfer = asyncio.run(makeTransfer(token, destinationAccount, amount, message))
        if not transfer.inserted_id:
            raise ValueError ('Error transfering')

        return jsonify({'transactionId': str(transfer.inserted_id) })

    except ValueError as err:
        return jsonify({"error": str(err)}), 400

@transaction.route('/v1/transactions/deposit', methods=['POST'])    
def deposit():
    try:
        token = validateJWT()

        if token == 400:
            return jsonify({"error": 'Token is missing in the request, please try again'}), 401

        if token == 401:
            return jsonify({"error": 'Invalid authentication token, please login again'}), 403

        if not request.data:
            raise 'Request error'

        dataReceived = json.loads(request.data)

        if not dataReceived['amount']:
            raise ValueError('Amount not informed')
        
        if not dataReceived['email']:
            raise ValueError('Email not informed')

        if not dataReceived['message']:
            raise 'Message not found in the request'            

        amount = dataReceived['amount']
        email = dataReceived['email'].lower()
        message = dataReceived['message']

        destinationAccount = asyncio.run(getAccountInfo(email, True, True))    
        if destinationAccount == 'Not found': 
            return jsonify({'error': 'Destination account not found' }), 404

        depositToMake = asyncio.run(makeDeposit(destinationAccount, amount, message))
        if not depositToMake.inserted_id:
            raise ValueError ('Error transfering')

        return jsonify({'transactionId': str(depositToMake.inserted_id) })

    except ValueError as err:
        return jsonify({"error": str(err)}), 400

@transaction.route('/v1/transactions/withdraw', methods=['POST'])
def withdraw():
    try:
        token = validateJWT()

        if token == 400:
            return jsonify({"error": 'Token is missing in the request, please try again'}), 401

        if token == 401:
            return jsonify({"error": 'Invalid authentication token, please login again'}), 403

        if not request.data:
            raise 'Request error'            

        dataReceived = json.loads(request.data)

        if not dataReceived['amount']:
            raise ValueError('Amount not informed')
     
        amount = dataReceived['amount']

        balance = asyncio.run(getBalance(token['email'].lower()))

        if int(balance['balance']) < amount:
            raise ValueError('Not enough funds')        

        withdrawToMake = asyncio.run(makeWithdraw(token, amount))
        if not withdrawToMake.inserted_id:
            raise ValueError ('Error withdrawing')

        return jsonify({"transactionId": str(withdrawToMake.inserted_id) })

    except ValueError as err:
        return jsonify({"error": str(err)}), 400

@transaction.route('/v1/transactions/loan', methods=['POST'])    
def loan():
    try:
        token = validateJWT()

        if token == 400:
            return jsonify({"error": 'Token is missing in the request, please try again'}), 401

        if token == 401:
            return jsonify({"error": 'Invalid authentication token, please login again'}), 403

        if not request.data:
            raise 'Request error'

        dataReceived = json.loads(request.data)

        if not dataReceived['amount']:
            raise ValueError('Amount not informed')

        amount = dataReceived['amount']

        loanToMake = asyncio.run(makeLoan(token, amount))
        if not loanToMake.inserted_id:
            raise ValueError ('Error transfering')

        return jsonify({"transactionId": str(loanToMake.inserted_id)})

    except ValueError as err:
        return jsonify({"error": str(err)}), 400

@transaction.route('/v1/transactions/<days>/statement', methods=['GET'])    
def returnStatement(days):
    try:
        token = validateJWT()

        if token == 400:
            return jsonify({"error": 'Token is missing in the request, please try again'}), 401

        if token == 401:
            return jsonify({"error": 'Invalid authentication token, please login again'}), 403

        if not days:
            raise ValueError('Not informed days of statement')

        # if days > 365:
        #     raise ValueError('Maximum number of days for a statement is 365')

        statement = asyncio.run(getStatement(token['accountId'], days))

        return jsonify({'statement': statement })
    except ValueError as err:
        return jsonify({"error": str(err)}), 400