from flask import Blueprint, session, Flask
import flask
from flask_mysqldb import MySQL 

user_blueprint = Blueprint('user_blueprint', __name__)

from main import mysql

@user_blueprint.route('/register', methods=['POST'])
def register():
    content = flask.request.json
    _firstName = content['firstName']
    _lastName = content['lastName']
    _email = content['email']
    _password = content['password']
    _address = content['address']
    _city = content['city']
    _country = content['country']
    _phone = content['phone']
    _balance = content['balance']
    _currency = content['currency']
    _verified = False
    
    
    # check if user with same email exists
    if userExists(_email):
       retVal = {'message' : 'User already registered'}, 400
       return retVal
    
    registerUser(_firstName, _lastName, _email, _password, _address, _city, _country, _phone, _balance, _currency,_verified)
    retVal = {'message' : 'User successfully registered'}, 200


    return retVal

@user_blueprint.route('/getUserFromDB', methods=['GET'])
def getUserFromDB():
    content = flask.request.json
    _email = content['email']
    return getUser(_email)

@user_blueprint.route('/login', methods=['POST'])
def login():
    content = flask.request.json
    _email = content['email']
    _password = content['password']

    user = getUser(_email)

    if user == None:
        retval = {'message' : 'User doesn\'t exist!'}, 400
    elif user['password'] == _password:
        retval = {'message' : 'Login successful!'}, 200
    else:
        retval = {'message' : 'Password is incorrect!'}, 400

    return retval

def userExists(email: str) -> bool :
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM user WHERE email = %s", [email])
    account = cursor.fetchone()
    cursor.close()
    if account:
        return True
    else:
        return False

def registerUser(name, lastname, email, password, address, city, country, phoneNum, balance, currency,verified):
    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO user VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',[ name, lastname, email, password, address, city, country, phoneNum, balance, currency,verified ])
    mysql.connection.commit()
    cursor.close()

def getUser(email : str) -> dict:
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM user WHERE email = %s", [email])
    user = cursor.fetchone()
    cursor.close()
    return user