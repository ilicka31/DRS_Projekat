from flask import Blueprint
import flask
from datetime import datetime

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


@user_blueprint.route('/verifying', methods=['POST'])
def verifying():
    content = flask.request.json
    _cardNumber  = content['cardNumber']
    _month =  content['month']
    _year = content['year']
    _cvv = content['cvv']
    _email= content['email']

    _monthNum = datetime.strptime(_month, '%B').month
    _expDate ="0"+str(_monthNum)+"/"+str(_year)[-2:]    

    #  
    # _card = card(_email)
    if( "4242424242424242" == str(_cardNumber).replace(" ", "") and "123" == str(_cvv).replace(" ","") and "02/23" ==str(_expDate)):
        #ovde kao treba skinuti taj dolar???
        updateUserVerified(_email)
        retval = {'message' : 'Succesfull verification! '}, 200
    else:
        retval = {'message' : 'Unsuccesfull verification!'}, 400
   
    return retval

def updateUserVerified(email):
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE user SET isVerified=true WHERE email = %s ",[email])
    mysql.connection.commit()
    cursor.close()

"""
@user_blueprint.route('/verify', methods=['POST'])
def verify():
    content = flask.request.json
    email = content['email']
    verifyUser(email)
    user = getUser(email)
    if user == None:
        retval = {'message' : 'Unsuccesfull verification! '}, 400
    else:
        retval = {'message' : 'Account verified! '}, 200
        
    return retval
""" 

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

@user_blueprint.route('/updateprofile', methods=['POST'])
def updateprofile():
    content = flask.request.json
    _firstName = content['firstName']
    _lastName = content['lastName']
    _email = content['email']
    _password = content['password']
    _address = content['address']
    _city = content['city']
    _country = content['country']
    _phone = content['phone']

    updateUser(_firstName, _lastName, _email, _password, _address, _city, _country, _phone)
    retVal = {'message' : 'User info successfully updated'}, 200
    return retVal

def updateUser(name, lastname, email, password, address, city, country, phone):
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE user SET firstName = %s, lastName = %s, password = %s, address = %s, city = %s, country = %s, phone = %s WHERE email = %s ",(name, lastname, password, address, city, country, phone, email))
    mysql.connection.commit()
    cursor.close()

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