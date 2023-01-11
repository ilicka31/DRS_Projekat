from flask import Blueprint, jsonify
import flask
import requests

transactions_blueprint = Blueprint('transactions_blueprint', __name__)

from main import mysql
from datetime import datetime


@transactions_blueprint.route('/exchanging', methods=['POST'])
def exchanging():
    content=flask.request.json
    email=content['email']
    ammountToExchange=content['ammountToExchange']
    currencyToExchange=content['currencyToExchange']
    usersCurrency=content['usersCurrency']
    return tryToExchange(email, ammountToExchange, currencyToExchange, usersCurrency)

def tryToExchange(email, ammount, currencyToExchange, usersCurrency):
    cursor=mysql.connection.cursor()
    result= cursor.execute("SELECT * FROM  userbalance WHERE email=%s AND currency=%s", [email, usersCurrency])
    currencies=cursor.fetchall()
    for item in currencies:
        if item['balance']<float(ammount):
            print('err')
            return {'message':'not enough money'}, 400   
    cursor.execute("UPDATE user SET balance=balance-%s WHERE email=%s AND currency=%s", [ammount, email, usersCurrency])
    

    cursor.execute("UPDATE userbalance SET balance=balance-%s WHERE email=%s AND currency=%s", [ammount, email, usersCurrency])
    
    print(usersCurrency)
    req = requests.get("https://api.freecurrencyapi.com/v1/latest?apikey=MmuhzxpAOc1bDgPlzY1t4wrbjW9Q7NW6af3HRDv6&base_currency=" + usersCurrency)
    currency_dict = (req.json())['data']
    result= cursor.execute("SELECT * FROM  userbalance WHERE email=%s", [email])
    currencies=cursor.fetchall()

    # Converts every other currency in base currecy value
    for key, value in currency_dict.items():
        if key==currencyToExchange:
            exchanged =  float(ammount)*value
    print(exchanged)
    for item in currencies:
        print(item['currency'])
        if item['currency']==currencyToExchange:
            print(currencyToExchange)
            print(item['currency'])

            cursor.execute("UPDATE userbalance SET balance=balance+%s WHERE email=%s AND currency=%s", [exchanged, email, currencyToExchange])
            print(exchanged)
            mysql.connection.commit()
            cursor.close()
            return {'message':'You successefully exchanged '}, 200  
    cursor.execute("INSERT INTO userbalance (email, currency, balance) VALUES (%s, %s, %s)",[email, currencyToExchange, exchanged])
    mysql.connection.commit()

    cursor.close()

    return {'message':'You successefully exchanged '}, 200  

@transactions_blueprint.route('/getUsersCurrencies', methods=['GET'])
def getUsersCurrencies():
    content=flask.request.json
    email=content['email']
    return getUsersCurrenciesFromDB(email)

@transactions_blueprint.route('/createTransaction', methods = ['POST'])
def createTransaction():
    content = flask.request.json
    
    _hashID = content['hashID']
    _sender = content['sender']
    _receiver = content['receiver']
    _time = datetime.now();
    _amount = content['amount']
    _amountF = float(_amount)
    _currency = content['currency']
    _status = content['status']
    _balance = content['balance']
    
    
    if(float(_amount) > _balance):
        return {'message':'You do not have enough balance on your acc for this transaction '}, 400
    
    if(isReceiverValid(_receiver)):
        tr = creatingTr(_hashID, _sender, _receiver, _time, _amount, _currency, _status)
        
    if(transactionExists(_hashID)):
        retval = {'message' : 'Successfull creating transaction'}, 200
    else:
        retval = {'message' : 'Error with creating transaction'}, 400
    
    return retval

def transactionExists(hashID: str) -> bool :
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM transactions WHERE hashID = %s", [hashID])
    transaction = cursor.fetchone()
    cursor.close()
    if (transaction != None):
        return True
    else:
        return False


def isReceiverValid(email: str) -> bool:
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT * FROM user WHERE email = %s and isVerified = 1;", [email])
    receiver = cursor.fetchone()
    cursor.close()
    if (receiver != None):
        return True 
    else:
        return False
        
def getSendersBalance(email: str) -> float:
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT balance FROM user WHERE email = '%s';", [email])
    balance = cursor.fetchall()
    cursor.close()
    return balance
    
def creatingTr(_hashID, _sender, _receiver, _time, _amount, _currency, _status):
    cursor=mysql.connection.cursor()
    
    #cursor.execute("UPDATE user SET balance = balance + %f WHERE email = \'%s\';", _amountF, _receiver);
    #cursor.execute("UPDATE user SET balance = balance - %f WHERE email = \'%s\';", _amountF, _sender);
    cursor.execute("INSERT INTO transactions VALUES (%s, %s, %s, %s, %s, %s, %s);", [_hashID, _sender, _receiver, _time, _amount, _currency, _status])
    mysql.connection.commit()
    transaction = cursor.fetchone()
    cursor.close()
    
    return transaction
    


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
    ammount=(content['ammount'])
    print(email)
    print(type(ammount))
    print(ammount)
    return addMoneyToDB(email, ammount)

def addMoneyToDB(email, ammount):
    cursor=mysql.connection.cursor()

    result=cursor.execute("UPDATE userbalance SET balance = balance + %s WHERE email = %s", [ammount, email])
    result=cursor.execute("UPDATE user SET balance =balance+ %s WHERE email = %s", [ammount, email])
    mysql.connection.commit()
    
    cursor.close()
    return jsonify(result)


def userExists(email: str) -> bool :
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM userbalance WHERE email = %s", [email])
    account = cursor.fetchone()
    cursor.close()
    if account:
        return True
    else:
        return False