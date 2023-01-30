from flask import Flask, render_template 
from flask_mysqldb import MySQL 


app= Flask(__name__)  

app.config['MYSQL_HOST'] = 'database' 
app.config['MYSQL_USER'] = 'root' 
app.config['MYSQL_PASSWORD'] = '123' 
app.config['MYSQL_DB'] = 'drs_baza'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' 
mysql = MySQL(app) 

from blueprints.transactions import transactions_blueprint
from blueprints.users import user_blueprint  

def start_process():
    from blueprints.transactions import transactionProcess, queue, multiprocessing
    process = multiprocessing.Process(target=transactionProcess, args=[queue])
    process.start()

if __name__ == "__main__":    
    app.register_blueprint(user_blueprint, url_prefix = '/api') 
    app.register_blueprint(transactions_blueprint, url_prefix = '/api')    
    start_process()
    app.run(host='0.0.0.0', debug=True,port=5001)
   