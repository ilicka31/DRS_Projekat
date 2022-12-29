from flask import Blueprint, jsonify
import flask

transactions_blueprint = Blueprint('transactions_blueprint', __name__)

from main import mysql


@transactions_blueprint.route('/getUsersCurrencies', methods=['GET'])
def getUsersCurrencies():
    content=flask.request.json
    email=content['email']
    return getUsersCurrenciesFromDB(email)


def getUsersCurrenciesFromDB(email):
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT * FROM  userbalance WHERE email=%s", [email])
    currencies=cursor.fetchall()
    cursor.close()
    return jsonify(currencies)

@transactions_blueprint.route('/getTransactionHistory', methods=['GET'])
def getTransactionHistory():
    content = flask.request.json
    _email = content['email']
    return getTransactionHistoryFromDB(_email)

def getTransactionHistoryFromDB(email):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM transactions WHERE sender = %s or receiver = %s",[email,email])
    history = cursor.fetchall()
    cursor.close()
    return jsonify(history)

@transactions_blueprint.route('/addingMoney', methods=['POST'])
def addingMoney():
    content=flask.request.json
    email=content['email']
    ammount=content['ammount']
    return addMoneyToDB(email, ammount)

def addMoneyToDB(email, ammount):
    cursor=mysql.connection.cursor()
    cursor.execute("UPDATE user SET balance=%s WHERE email=%s", [ammount, email])
    
    respone=cursor.fetchall()
    cursor.close()
    return jsonify(respone)


def userExists(email: str) -> bool :
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM userbalance WHERE email = %s", [email])
    account = cursor.fetchone()
    cursor.close()
    if account:
        return True
    else:
        return False