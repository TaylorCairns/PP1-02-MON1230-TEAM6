from flask import Flask, render_template, request, url_for, session, redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib

app = Flask(__name__)
app.secret_key = 'yoursecretkey'
app.config['MYSQL_HOST'] = '34.87.208.208'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'genrental'
app.config['MYSQL_DB'] = 'genrentaldb'

mysql = MySQL(app)




@app.route('/', methods=['GET', 'POST'])
def login():

    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s and password = %s', (username, password))
        acc = cursor.fetchone()
        if acc:
            return redirect(url_for('rent'))
        else:
            msg = 'Incorrect Username or Password'
        
        

    return render_template('index.html', msg=msg)

@app.route('/register')
def register():
    return render_template('register.html')



@app.route('/rent')
def rent():
    return render_template('rent.html')



