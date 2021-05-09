from flask import Flask, render_template, request, url_for, session, redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib

app = Flask(__name__)
app.secret_key = 'yoursecretkey'
app.config['MYSQL_HOST'] = '34.116.121.90'
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

        # generates a Salt and Hashes the Password with sha256
        salt = "lcyysk2NAQOJCHxkM1fA"
        saltPass = password+salt
        hashPass = hashlib.sha256(saltPass.encode())
        encryptPass = hashPass.hexdigest()
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s and password = %s', (username, encryptPass))
        acc = cursor.fetchone()
        if acc:
            session['logged'] = True
            session['user'] = acc['username']
            session['type'] = acc['userType']
            session['name'] = acc['firstname']

            return redirect(url_for('rent'))
        else:
            msg = 'Incorrect Username or Password'
        
        

    return render_template('index.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' and 'firstName' in request.form and 'lastName' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        userType = 'customer'
        licenseNo = 'none'
        # generates a Salt and Hashes the Password with sha256
        salt = "lcyysk2NAQOJCHxkM1fA"
        saltPass = password+salt
        hashPass = hashlib.sha256(saltPass.encode())
        encryptPass = hashPass.hexdigest()

        #Chec if account exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        acc = cursor.fetchone()
        
        
        if acc:
            msg = 'Account already exists'
        elif not username or not password or not email:
            msg = 'Please fill out the form'
        else:
            cursor.execute('INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s, %s)', (username, encryptPass, email, firstName, lastName, licenseNo, userType))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('login'))
            
    elif request.method == 'POST':
        msg = 'Please fill out form'



    return render_template('register.html', msg=msg)



@app.route('/rent')
def rent():
    return render_template('rent.html')


@app.route('/logout')
def logout():
    session.pop('logged', none)
    session.pop('username', none)
    session.pop('userType', none)
    session.pop('firstname', none)

    return redirect(url_for('login'))



@app.route('/profile')
def profile():
    if 'logged' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (session['user'],))
        user = cursor.fetchone()
        return render_template('profile.html', typeOfUser=session['type'], user=user)

    return redirect(url_for('login'))


@app.route('/edituser', methods=['GET', 'POST'])
def edituser():
    
    
    msg = ''
    if request.method == 'POST' and 'selectUser' in request.form and 'changeSection' in request.form and 'newValue' in request.form:
        
        
        selectUser = request.form['selectUser']
        changeSection = request.form['changeSection']
        newValue = request.form['newValue']

        print(changeSection)
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if changeSection == 'firstname':
            cursor.execute('UPDATE users SET firstname = %s WHERE username = %s',(newValue, selectUser))
            mysql.connection.commit()
        if changeSection == 'lastname':
            cursor.execute('UPDATE users SET lastname = %s WHERE username = %s',(newValue, selectUser))
            mysql.connection.commit()
        if changeSection == 'userType':
            cursor.execute('UPDATE users SET userType = %s WHERE username = %s',(newValue, selectUser))
            mysql.connection.commit()
        if changeSection == 'licenseNo':
            cursor.execute('UPDATE users SET licenseNo = %s WHERE username = %s',(newValue, selectUser))
            mysql.connection.commit()
        
        

        
    return render_template('editUser.html')   
