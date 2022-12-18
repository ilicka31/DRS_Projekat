from flask import Blueprint, jsonify
import flask

transactions_blueprint = Blueprint('transactions_blueprint', __name__)

from main import mysql

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
