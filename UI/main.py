from flask import Flask, render_template, request, json, session, flash, redirect,url_for
import json
import requests
import random
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = "12345abv"

@app.route('/')
def main():
    return render_template('registration.html')

@app.route('/register', methods = ['POST'])
def register():
    _firstName = request.form['firstName']
    _lastName = request.form['lastName']
    _email = request.form['email']
    _password = request.form['password']
    _address = request.form['address']
    _city = request.form['city']
    _country = request.form['country']
    _phone = request.form['phone']
    _balance = "0"
    _currency = "USD"

    headers = {'Content-type' : 'application/json', 'Accept' : 'text/plain'}
    body = json.dumps({'firstName': _firstName, 'lastName':_lastName, 'email':_email, 'password':_password, 'address':_address, 
                        'city':_city, 'country':_country, 'phone':_phone, 'balance':_balance, 'currency': _currency})
    req = requests.post("http://127.0.0.1:5001/api/register", data = body, headers=headers)
    

    response = (req.json())
    _message = response['message'] 
    _code = req.status_code
    
    if _code == 200:
        return redirect(url_for('main'))

    if _code == 400:
        return redirect(url_for('main'))

    return render_template('registration.html')

@app.route('/logout')
def logout():
    session['user']= None
    return render_template('registration.html')

@app.route('/createTr')
def createTr():
    return render_template("createTransaction.html", user=session['user'], transaction_history = getTransactionHistory(),currency_dictionary=currency_dictionary, users_currencies=getUsersCurrencies(session['user']['email']), message = request.args.get('message'))

@app.route('/filter', methods = ['POST'])
def filter():
    _sender = request.form['sender']
    _receiver = request.form['receiver']
    _amountMin = request.form['amountMin']
    _amountMax = request.form['amountMax']
    _currency = request.form['currency']
    _time = request.form['time']
    _status = request.form['status']
    user = session['user']
    _email = session['user']['email']
    
    headers = {'Content-type' : 'application/json', 'Accept' : 'text/plain'}
    body = json.dumps({'sender' : _sender, 'receiver' : _receiver, 'amountMin' : _amountMin, 
                       'amountMax': _amountMax, 'currency' : _currency, 'time' : _time, 'status' : _status, 'email' : _email})
    req = requests.post("http://127.0.0.1:5001/api/filterTransactions", data = body, headers=headers)
    response = req.json()
    
    return render_template("profile.html", user=session['user'], transaction_history = response, currency_dictionary=currency_dictionary, users_currencies=getUsersCurrencies(session['user']['email']))

@app.route('/createTransaction', methods = ['POST'])
def createTransaction():
    _sender = session['user']['email']
    _balance = session['user']['balance']
    _receiver = request.form['receiver']
    _amount = request.form['amount']
    _currency = request.form['currency']
    if(_sender == _receiver):
        return redirect(url_for('createTr', message = "Can't initiate a transaction to yourself!"))
    headers = {'Content-type' : 'application/json', 'Accept' : 'text/plain'}
    body = json.dumps({'sender': _sender, 'balance' : _balance, 'receiver':_receiver, 'amount':_amount, 'currency':_currency})
    req = requests.post("http://127.0.0.1:5001/api/createTransaction", data = body, headers=headers)
    
    response = (req.json())
    _message = response['message'] 
    _code = req.status_code
    if(_code == 200):
        updateUserInSession(_sender)
        return redirect(url_for("profile", sender = _sender))
    else:
        return redirect(url_for('createTr', message = _message))

@app.route('/verify')
def verify():
    return render_template("verify.html", user=session['user'], transaction_history = getTransactionHistory(),currency_dictionary=currency_dictionary, users_currencies=getUsersCurrencies(session['user']['email']))

@app.route('/verifying', methods =['POST'])
def verifying():
    user = session['user']
    _email =user['email']
    _cardNumber = request.form['card']
    _month = request.form['month']
    _year = request.form['year']
    _cvv = request.form['cvv']
    

    headers = {'Content-type' : 'application/json', 'Accept' : 'text/plain'}
    body = json.dumps({'cardNumber': _cardNumber, 'month':_month, 'year':_year, 'cvv':_cvv, 'email': _email })
    req = requests.post("http://127.0.0.1:5001/api/verifying", data = body, headers=headers)

    response = (req.json())
    _message = response['message'] 
    _code = req.status_code
    #session['user']['isVerified']=1
    updateUserInSession(_email)
    if _code == 200:
        return redirect(url_for('profile'))

    if _code == 400:
        return redirect(url_for('profile'))

@app.route('/exchange')
def exchange():
    return render_template("exchange.html", user=session['user'], transaction_history = getTransactionHistory(),currency_dictionary=currency_dictionary, users_currencies=getUsersCurrencies(session['user']['email']))

@app.route('/exchanging', methods=['POST'])
def exchanging():
    email=request.form['email']
    ammountToExchange=request.form['ammountToExchange']
    currencyToExchange=request.form['currencyToExchange']
    usersCurrency=request.form['usersCurrencies']
    headers = {'Content-type' : 'application/json', 'Accept' : 'text/plain'}
    body = json.dumps({'ammountToExchange': ammountToExchange, 'currencyToExchange':currencyToExchange, 'email':session['user']['email'], 'usersCurrency':usersCurrency })
    req = requests.post("http://127.0.0.1:5001/api/exchanging", data = body, headers=headers)
    
    mess=''
    if req.status_code==400:
        mess='Not enough money'
        return render_template("exchange.html", user=session['user'], message=mess, currency_dictionary=currency_dictionary, transaction_history = getTransactionHistory(), users_currencies=getUsersCurrencies(session['user']['email']))

    updateUserInSession(email)

    return redirect(url_for('profile'))
    
@app.route('/addMoney')
def addMoney():
    return render_template("addMoney.html", user=session['user'], transaction_history = getTransactionHistory(),currency_dictionary=currency_dictionary, users_currencies=getUsersCurrencies(session['user']['email']), message = request.args.get('_message'))

@app.route('/addingMoney', methods=['POST'])
def addingMoney():
    user=session['user']
    email=user['email']
    ammountToAdd=request.form['ammountToAdd']
    _cardNumber = request.form['card']
    _month = request.form['month']
    _year = request.form['year']
    _cvv = request.form['cvv']

    _monthNum = datetime.strptime(_month, '%B').month
    _expDate ="0"+str(_monthNum)+"/"+str(_year)[-2:]    

    _message = ""
    if("4242424242424242" != str(_cardNumber).replace(" ", "") or "123" != str(_cvv).replace(" ","") or "02/23" != str(_expDate)):
        _message = "Invalid card information inserted!"
        return redirect(url_for('addMoney', _message = _message))

    headers = {'Content-type' : 'application/json', 'Accept' : 'text/plain'}
    body = json.dumps({'email' : email, 'ammount' : ammountToAdd})
    req = requests.post("http://127.0.0.1:5001/api/addingMoney", data = body, headers = headers)
    updateUserInSession(email)

    return redirect(url_for('profile'))

@app.route('/login', methods =['POST'])
def login():
    _email = request.form['email']
    _password = request.form['password']

    headers = {'Content-type' : 'application/json', 'Accept' : 'text/plain'}
    body = json.dumps({'email' : _email, 'password' : _password})
    req = requests.post("http://127.0.0.1:5001/api/login", data = body, headers = headers)

    response = (req.json())
    _message = response['message'] 
    _code = req.status_code

    if _code == 200:
        updateUserInSession(_email)
        return redirect(url_for('profile'))
    if _code == 400:
        return redirect(url_for('main'))


@app.route('/profile')
def profile():
    sender = request.args.get('sender')
    if sender != None:
        updateUserInSession(sender)
    return render_template('profile.html', user = session['user'], currency_dictionary = currency_dictionary, transaction_history = getTransactionHistory() , users_currencies=getUsersCurrencies(session['user']['email']))

@app.route('/update')
def update():
    return render_template('updateprofile.html', user=session['user'])

@app.route('/updateuser', methods=['POST'])
def updateuser():
    user = session['user']
    _firstName = request.form['firstName']
    _lastName = request.form['lastName']
    _email = user['email']
    _password = request.form['password']
    _address = request.form['address']
    _city = request.form['city']
    _country = request.form['country']
    _phone = request.form['phone']
    
    headers = {'Content-type' : 'application/json', 'Accept' : 'text/plain'}
    body = json.dumps({'firstName': _firstName, 'lastName':_lastName,'email' : _email, 'password':_password, 'address':_address, 
                        'city':_city, 'country':_country, 'phone':_phone})
    print(_email)
    req = requests.post("http://127.0.0.1:5001/api/updateprofile", data = body, headers = headers)

    response = (req.json())
    _message = response['message'] 
    _code = req.status_code
    updateUserInSession(session['user']['email'])

    if _code == 200:
        return redirect(url_for('profile'))
    return redirect(url_for('profile'))

countries_dictionary={}
def updateUserInSession(email):
    # Get updated user and put it in session['user']
    headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'email': email})
    req = requests.get("http://127.0.0.1:5001/api/getUserFromDB", data = body, headers = headers)
    session['user'] = (req.json())


currency_dictionary ={}
@app.before_first_request
def getCurrencyList():
    global currency_dictionary
    currency_dictionary = refreshCurrencyList('USD')
    
def refreshCurrencyList(base_currency : str):
    # base currency is RSD in our case
    req = requests.get("https://api.freecurrencyapi.com/v1/latest?apikey=MmuhzxpAOc1bDgPlzY1t4wrbjW9Q7NW6af3HRDv6&base_currency=" + base_currency)
    # req = requests.get("https://freecurrencyapi.net/api/v2/latest?apikey=57fbaed0-7177-11ec-a390-0d2dac4cb175&base_currency=" + base_currency)
    currency_dict = (req.json())['data']

    # Converts every other currency in base currecy value
    for key, value in currency_dict.items():
        currency_dict[key] = 1 / value

    return dict(sorted(currency_dict.items(), key=lambda x:x[1], reverse=True))



def getUsersCurrencies(email):
    
    headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'email': email})
    req = requests.get("http://127.0.0.1:5001/api/getUsersCurrencies", data = body, headers = headers)
    
    return req.json()   
    

def getTransactionHistory():
    headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'email': session['user']['email']})
    req = requests.get("http://127.0.0.1:5001/api/getTransactionHistory", data = body, headers = headers)
    return req.json()


app.run(port=5000)