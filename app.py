from flask import Flask,jsonify
from src.views.account import account
from src.views.transaction import transaction
from waitress import serve

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

app.register_blueprint(account)  # /v1/accounts
app.register_blueprint(transaction)  # /v1/transactions

@app.errorhandler(404)
def errorHandle(self):
    return jsonify({"error": '404, Something wrong is not right'}), 404   

@app.route("/")
def index():
    return ''    

if __name__ == "__main__":
   app.run()