from flask import Blueprint, jsonify
import flask, requests, sha3, random, struct, threading
import json

transactions_blueprint = Blueprint('transactions_blueprint', __name__)

from main import mysql
from datetime import datetime

from time import sleep
from models.transaction import Transaction
import multiprocessing
from multiprocessing import Queue
import MySQLdb
queue = Queue()

@transactions_blueprint.route('/exchanging', methods=['POST'])
def exchanging():
    content=flask.request.json
    email=content['email']
    ammountToExchange=content['ammountToExchange']
    currencyToExchange=content['currencyToExchange']
    usersCurrency=content['usersCurrency']
    return tryToExchange(email, ammountToExchange, currencyToExchange, usersCurrency)

def tryToExchange(email, ammount, currencyToExchange, usersCurrency):
    _status = 'SUCCESS'
    '''UMANJIVANJE'''
    if(usersCurrency == "USD"):
        cursor=mysql.connection.cursor()
        result = cursor.execute("SELECT balance FROM user WHERE email=%s", [email])
        balance = cursor.fetchone()
        if(balance['balance']<float(ammount)):
            _status = 'FAIL'
            print('err')
            return {'message':'not enough money'}, 400
        newBalance = balance['balance']-float(ammount)
        newBalance = round(newBalance,2)
        cursor.execute("UPDATE user SET balance=%s WHERE email=%s", [newBalance, email])
    else:
        cursor=mysql.connection.cursor()
        result= cursor.execute("SELECT balance FROM  userbalance WHERE email=%s AND currency=%s", [email, usersCurrency])
        balance=cursor.fetchone()

        if balance['balance']<float(ammount):
            _status = 'FAIL'
            print('err')
            return {'message':'not enough money'}, 400   
        newBalance = balance['balance']-float(ammount)
        newBalance = round(newBalance,2)
        cursor.execute("UPDATE userbalance SET balance=%s WHERE email=%s AND currency=%s", [newBalance, email, usersCurrency])

    '''NOVA VALUTA/UVECAVANJE POSTOJECE'''
    req = requests.get("https://api.freecurrencyapi.com/v1/latest?apikey=MmuhzxpAOc1bDgPlzY1t4wrbjW9Q7NW6af3HRDv6&base_currency=" + usersCurrency)
    # req = requests.get("https://freecurrencyapi.net/api/v2/latest?apikey=57fbaed0-7177-11ec-a390-0d2dac4cb175&base_currency=" + usersCurrency)

    currency_dict = (req.json())['data']
    result= cursor.execute("SELECT * FROM  userbalance WHERE email=%s", [email])
    currencies=cursor.fetchall()

    # Converts every other currency in base currency value
    for key, value in currency_dict.items():
        if key==currencyToExchange:
            exchanged = float(ammount)*value
            exchanged = round(exchanged,2)
    for item in currencies:
        if item['currency']==currencyToExchange:
            newBalance = item['balance'] + exchanged
            newBalance= round(newBalance,2)
            cursor.execute("UPDATE userbalance SET balance=%s WHERE email=%s AND currency=%s", [newBalance, email, currencyToExchange])
            mysql.connection.commit()
            cursor.close()
            return {'message':'You successfully exchanged '}, 200  
    
    cursor.execute("INSERT INTO userbalance (email, currency, balance) VALUES (%s, %s, %s)",[email, currencyToExchange, exchanged])

    _time = datetime.now()
    _time = _time.strftime('%Y-%m-%d %H:%M:%S')
    random_int = random.getrandbits(32)
    _hashID = generateHash(email, email, float(ammount), random_int)
    exchange = usersCurrency + "->" + currencyToExchange
    
    cursor.execute("INSERT INTO transactions VALUES (%s, %s, %s, %s, %s, %s, %s);", [_hashID, email, email, _time, ammount, exchange, _status])

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

    _sender = content['sender']
    _receiver = content['receiver']
    _amount = content['amount']
    _currency = content['currency']
    _balance = content['balance']

    _status = 'PROCESSING'
    random_int = random.getrandbits(32)
    _amountF = float(_amount)
    _time = datetime.now()
    _time = _time.strftime('%Y-%m-%d %H:%M:%S')
    
    _hashID = generateHash(_sender, _receiver, _amountF, random_int)
    
    if(isReceiverValid(_receiver)):
        cursor=mysql.connection.cursor()
        cursor.execute("INSERT INTO transactions VALUES (%s, %s, %s, %s, %s, %s, %s);", [_hashID, _sender, _receiver, _time, _amount, _currency, _status])
        mysql.connection.commit()
        cursor.close()
        thread =threading.Thread(target=transactionThread, args=(_hashID, _sender, _receiver, _time, _amount, _currency, _status, _balance))
        thread.start()
        return  {'message':'Successfully created transaction'}, 200

    return {'message' : 'Receiver user doesn\'t exist!'}, 400

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

def transactionThread(_hashID, _sender, _receiver, _time, _amount, _currency, _status, _balance):
    sleep(5) #proveriti koliko treba cekati
    #napravi se nova transakcija i smesti u queue
    tr = Transaction(_hashID,_sender,_receiver,_amount,_time,_currency,_status)
    queue.put(tr)


def transactionProcess(queue : Queue):
    while(1):
        transaction = queue.get()
     
        # otvaranje nove konekcije u threadu
        cnx = MySQLdb.connect(host="localhost",
                            user="root",
                            passwd="",
                            db="drs_baza")

        cursor = cnx.cursor()

        if(transaction.currency == "USD"):
            cursor.execute(''' SELECT balance FROM user WHERE email = %s ''', [transaction.sender])
            response = cursor.fetchone()
            senderBalance = float(response[0])
        else:
            cursor.execute(''' SELECT balance FROM userbalance WHERE email=%s AND currency=%s''', [transaction.sender, transaction.currency])
            response = cursor.fetchone()
            senderBalance = float(response[0])
        if(float(transaction.amount) > senderBalance): #stanje odbijena
            cursor.execute(''' UPDATE transactions SET status = %s WHERE hashID = %s''', ['FAIL', transaction.id])
        else: #stanje obradjena
            creatingTr(transaction.id, transaction.sender, transaction.receiver,transaction.date, transaction.amount, transaction.currency, transaction.state,cursor)
        cnx.commit()
        cursor.close()
        cnx.close()


def creatingTr(_hashID, _sender, _receiver, _time, _amount, _currency, _status, cursor):
    #cursor=mysql.connection.cursor()
    if(_currency == "USD"):
        cursor.execute("SELECT balance FROM user WHERE email = %s", [_sender])
        oldBalance = cursor.fetchone()
        newBalance = oldBalance[0] - float(_amount)
        newBalance = round(newBalance,2)
        cursor.execute("UPDATE user SET balance=%s WHERE email=%s", [newBalance, _sender])
    else:
       # cursor=mysql.connection.cursor()
        result= cursor.execute("SELECT balance FROM  userbalance WHERE email=%s AND currency=%s", [_sender, _currency])
        balance=cursor.fetchone() 
        newBalance = balance[0] - float(_amount)
        newBalance = round(newBalance,2)
        cursor.execute("UPDATE userbalance SET balance=%s WHERE email=%s AND currency=%s", [newBalance, _sender, _currency])
    
    if(_currency == "USD"):
        cursor.execute("SELECT balance FROM user WHERE email = %s", [_receiver])
        oldBalance = cursor.fetchone()
        newBalance = oldBalance[0] + float(_amount)
        newBalance = round(newBalance,2)
        cursor.execute("UPDATE user SET balance=%s WHERE email=%s", [newBalance, _receiver])
    else:
        #cursor=mysql.connection.cursor()
        result=cursor.execute("SELECT balance FROM  userbalance WHERE email=%s AND currency=%s", [_receiver, _currency])
        balance=cursor.fetchone() 

        if(balance == None):
            amount = round(float(_amount),2)
            cursor.execute("INSERT INTO userbalance (email, currency, balance) VALUES (%s, %s, %s)",[_receiver, _currency, amount])
        else:
            newBalance = balance[0] + float(_amount)
            newBalance = round(newBalance,2)
            cursor.execute("UPDATE userbalance SET balance=%s WHERE email=%s AND currency=%s", [newBalance, _receiver, _currency])

    cursor.execute(''' UPDATE transactions SET status = %s WHERE hashID = %s''', ('SUCCESS', _hashID))
    #mysql.connection.commit()
    #_message = cursor.fetchone()
    #cursor.close()

    
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

@transactions_blueprint.route('/filterTransactions', methods = ['POST'])
def filterTransactions():
    content = flask.request.json
    _email = content['email']
    transactions = getTransactionHistoryFromDB(_email)
    
    _sender = content['sender']
    _receiver = content['receiver']
    _amountMin = content['amountMin']
    _amountMax = content['amountMax']
    _currency = content['currency']
    _status = content['status']
    transactions = transactions.json
    transactionsNew = []
    
    
    if((_sender == '') and (_receiver == '') and (_amountMin == '') and (_amountMax == '') and (_currency == '') and (_time == '') and (_status == '')):
        return jsonify(transactions)
    
    if(_amountMin != ''):
        _amountMin = float(_amountMin)
    else:
        _amountMin = 0
    
    if(_amountMax != ''):
        _amountMax = float(_amountMax)
    else:
        _amountMax = 0
        
        
    for obj in transactions:
        if(_amountMax == 0):
            if((_sender.upper() in obj['sender'].upper()) and (_receiver.upper() in obj['receiver'].upper()) and (_amountMin < obj['amount']) and
                (_status.upper() in obj['status'].upper()) and (_currency.upper() in obj['currency'].upper())):
                transactionsNew.append(obj)
        else:
            if((_sender.upper() in obj['sender'].upper()) and (_receiver.upper() in obj['receiver'].upper()) and (_amountMin < obj['amount']) and (_amountMax > obj['amount']) and
                (_status.upper() in obj['status'].upper()) and (_currency.upper() in obj['currency'].upper())):
                transactionsNew.append(obj)
                
    
    return jsonify(transactionsNew)

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
    return addMoneyToDB(email, ammount)

def addMoneyToDB(email, ammount):
    cursor=mysql.connection.cursor()
    result=cursor.execute("UPDATE user SET balance=balance+%s WHERE email = %s", [ammount, email])

    _time = datetime.now()
    _time = _time.strftime('%Y-%m-%d %H:%M:%S')
    random_int = random.getrandbits(32)
    _hashID = generateHash(email, email, float(ammount), random_int)
    
    cursor.execute("INSERT INTO transactions VALUES (%s, %s, %s, %s, %s, %s, %s);", [_hashID, email, email, _time, ammount, 'USD', 'SUCCESS'])


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



def generateHash(_sender, _receiver, _amount, rand_int):
    input_data = _sender.encode() + _receiver.encode() + struct.pack("!d", _amount) + struct.pack("I", rand_int)
    
    keccak256 = sha3.keccak_256()
    keccak256.update(input_data)
    
    keccak_hash = keccak256.hexdigest()
    return keccak_hash
