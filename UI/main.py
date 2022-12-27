from flask import Flask, render_template, request, json, session, flash, redirect,url_for
import json
import requests

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
    _currency = 'USD'

    headers = {'Content-type' : 'application/json', 'Accept' : 'text/plain'}
    body = json.dumps({'firstName': _firstName, 'lastName':_lastName, 'email':_email, 'password':_password, 'address':_address, 
                        'city':_city, 'country':_country, 'phone':_phone, 'balance':_balance, 'currency': _currency})
    req = requests.post("http://127.0.0.1:5001/api/register", data = body, headers=headers)
    

    response = (req.json())
    _message = response['message'] 
    _code = req.status_code
    
    if _code == 200:
        flash(_message)
        return redirect(url_for('main'))

    if _code == 400:
        flash(_message)
        return redirect(url_for('main'))

    return render_template('registration.html')
"""
@app.route('/verify', methods = ['POST'])
def verify():
    user = session['user']
    headers = {'Content-type' : 'application/json', 'Accept' : 'text/plain'}
    
    email = user['email']
    body = json.dumps({'email' : email})
    
    req = requests.post("http://127.0.0.1:5001/api/verify", data = body, headers = headers)
    response = (req.json())
    _message = response['message'] 
    _code = req.status_code

    if _code == 200:
        updateUserInSession(user['email'])
        return render_template('profile.html', user = session['user'])
    if _code == 400:
        flash(_message)
        return redirect(url_for('main'))
"""

@app.route('/logout')
def logout():
    session['user']= None
    return render_template('registration.html')

@app.route('/verify')
def verify():
    return render_template("verify.html", user=session['user'])

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
    
    if _code == 200:
        flash(_message)
        return redirect(url_for('profile'))

    if _code == 400:
        flash(_message)
        return render_template("profile.html", user=session['user'])



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
        flash(_message)
        return redirect(url_for('main'))

@app.route('/profile')
def profile():
    transaction_history = getTransactionHistory()
    return render_template('profile.html', user = session['user'],currency_dictionary = currency_dictionary, transaction_history = transaction_history)

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
    return render_template('profile.html')


@app.route('/changeCurrency', methods=['POST'])
def change():
    newCurrency=request.form['currencyChosenByTheUser']
    return render_template('profile.html', user = session['user'],currency_dictionary = refreshCurrencyList(newCurrency))

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
    req = requests.get("https://freecurrencyapi.net/api/v2/latest?apikey=57fbaed0-7177-11ec-a390-0d2dac4cb175&base_currency=" + base_currency)
    currency_dict = (req.json())['data']

    # Converts every other currency in base currecy value
    for key, value in currency_dict.items():
        currency_dict[key] = 1 / value

    return dict(sorted(currency_dict.items(), key=lambda x:x[1], reverse=True))



    
    

def getTransactionHistory():
    headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'email': session['user']['email']})
    req = requests.get("http://127.0.0.1:5001/api/getTransactionHistory", data = body, headers = headers)
    return req.json()


app.run(port=5000)