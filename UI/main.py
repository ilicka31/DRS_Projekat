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
    _currency = 'RSD'

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
    return render_template('profile.html', user = session['user'])

def updateUserInSession(email):
    # Get updated user and put it in session['user']
    headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'email': email})
    req = requests.get("http://127.0.0.1:5001/api/getUserFromDB", data = body, headers = headers)
    session['user'] = (req.json())



app.run(port=5000)