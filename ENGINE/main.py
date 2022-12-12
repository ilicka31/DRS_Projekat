from flask import Flask, render_template 
from flask_mysqldb import MySQL 
from blueprints.users import user_blueprint  

app= Flask(__name__, root_path='../UI/')  

app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root' 
app.config['MYSQL_PASSWORD'] = '' 
app.config['MYSQL_DB'] = 'drs_baza'
mysql = MySQL(app) 

 
#app.config['MYSQL_CURSORCLASS'] = 'DictCursor' 

 
if __name__ == "__main__":    
    app.register_blueprint(user_blueprint, url_prefix = '/api')     
    app.run(port=5001)