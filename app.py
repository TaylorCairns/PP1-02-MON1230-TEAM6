from flask import Flask, render_template, request, url_for, session, redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib
from datetime import datetime, timedelta
import geocoder


app = Flask(__name__)
app.secret_key = 'yoursecretkey'
app.config['MYSQL_HOST'] = '34.116.121.90'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'genrental'
app.config['MYSQL_DB'] = 'genrentaldb'

mysql = MySQL(app)

#Login function requests data from user to create session information, if successful login, returns rent page, else returns log in page.

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
        cursor.execute(
            'SELECT * FROM users WHERE username = %s and password = %s', (username, encryptPass))
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

#Register Function requests data from user, inserts new entries into appropriate tables. Returns Register page

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

        # Check if account exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        acc = cursor.fetchone()

        if acc:
            msg = 'Account already exists'
        elif not username or not password or not email:
            msg = 'Please fill out the form'
        else:
            cursor.execute('INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s, %s)',
                           (username, encryptPass, email, firstName, lastName, licenseNo, userType))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('login'))

    elif request.method == 'POST':
        msg = 'Please fill out form'

    return render_template('register.html', msg=msg)

#Rent Function loads data based on session information, returns rent page

@app.route('/rent')
def rent():
    if 'logged' in session:
        if request.method == 'GET':
            user = session['user']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM bookings WHERE completed = %s AND username = %s', ('No', session['user'],))
            history = cursor.fetchall()
            mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM bookings WHERE completed = %s AND username = %s', ('Yes', session['user'],))
            past = cursor.fetchall()
            mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute('SELECT * FROM cars')
            cars = cursor.fetchall()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM cars WHERE NOT longlat IS NULL')
            carsLoc = cursor.fetchall()

            session
            
            #Gets current location from ip address
            g = geocoder.ip('me')
            

            cur = str(g.lat) + ',' + str(g.lng)
            

            my_string = '&markers=color:green%7Clabel:%7C' + cur + '|'
            for row in carsLoc:
                labelName = str(row['carId'])
                my_string = my_string + '&markers=color:' + row['color'] + '%7Clabel:' + labelName + '%7C' + row['longlat'] + '|'

            return render_template('rent.html', userType=session['type'], userHistory=history, username=user, cars=cars, past=past, my_string=my_string)

        return render_template('rent.html', userType=session['type'], username=session['username'])

    return redirect(url_for('login'))


#Booking Function requests data from user, inserts new data into appropriate tables


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'logged' in session:
        if request.method == 'POST':
            user = session['user']

            carLicense = request.form['carLicense']
            date = request.form['date']
            time = request.form['time']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM cars WHERE license = %s', (carLicense, ))

            cars = cursor.fetchone()
            mysql.connection.commit()

            if cars:

                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('INSERT INTO bookings (username, license, date, completed, time) VALUES (%s, %s, %s, %s, %s)', (
                    user, carLicense, date, 'No', time))
                mysql.connection.commit()


        return redirect(url_for('rent'))
    else:
        return redirect(url_for('login'))


#Cancel Booking Function requests data from user and deletes appropriate data from database table


@app.route('/cancelBooking', methods=['GET', 'POST'])
def cancelBooking():
    if 'logged' in session:
        if request.method == 'POST' and 'cancelId' in request.form:
            user = session['user']
            cancelId = request.form['cancelId']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM bookings WHERE id = %s AND username = %s', (cancelId, user))
            cancelBooking = cursor.fetchone()
            mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM bookings WHERE username = %s', (user, ))

            history = cursor.fetchall()
            mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM cars')
            cars = cursor.fetchall()
            mysql.connection.commit()

            if cancelBooking:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    'UPDATE bookings SET completed = %s WHERE id = %s', ('Yes', cancelId))
                mysql.connection.commit()

                return redirect(url_for('rent'))
            return redirect(url_for('rent'))
        return redirect(url_for('rent'))

    else:
        return redirect(url_for('login'))



#Logout Function logs user out of session

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'logged' in session:

        session.pop('logged', None)
        session.pop('username', None)
        session.pop('userType', None)
        session.pop('firstname', None)

        return redirect(url_for('login'))

#Profile Function loads user data on Profile page.

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'logged' in session:

        if request.method == 'GET':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM users WHERE username = %s', (session['user'],))
            user = cursor.fetchone()
            return render_template('profile.html', typeOfUser=session['type'], user=user)

        msg = ''
        if request.method == 'POST' and 'newValue' in request.form and 'changeSection' in request.form:
            
            changeSection = request.form['changeSection']
            newValue = request.form['newValue']


            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if changeSection == 'firstname':
                cursor.execute(
                    'UPDATE users SET firstname = %s WHERE username = %s', (newValue, session['user']))
                mysql.connection.commit()
            if changeSection == 'lastname':
                cursor.execute(
                    'UPDATE users SET lastname = %s WHERE username = %s', (newValue, session['user']))
                mysql.connection.commit()
            if changeSection == 'email':
                cursor.execute(
                    'UPDATE users SET email = %s WHERE username = %s', (newValue, session['user']))
                mysql.connection.commit()
            if changeSection == 'licenseNo':
                cursor.execute(
                    'UPDATE users SET licenseNo = %s WHERE username = %s', (newValue, session['user']))
                mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM users WHERE username = %s', (session['user'],))
            user = cursor.fetchone()
            return render_template('profile.html', typeOfUser=session['type'], user=user)

        return render_template('profile.html', typeOfUser=session['type'], user=session['user'])

    return redirect(url_for('login'))



@app.route('/edituser', methods=['GET', 'POST'])
def edituser():
    if 'admin' in session['type'] and 'logged' in session:

        if request.method == 'GET':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users')
            user = cursor.fetchall()
            return render_template('editUser.html', user=user)

        msg = ''
        if request.method == 'POST' and 'selectUser' in request.form and 'changeSection' in request.form and 'newValue' in request.form:

            selectUser = request.form['selectUser']
            changeSection = request.form['changeSection']
            newValue = request.form['newValue']

            

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if changeSection == 'firstname':
                cursor.execute(
                    'UPDATE users SET firstname = %s WHERE username = %s', (newValue, selectUser))
                mysql.connection.commit()
            if changeSection == 'lastname':
                cursor.execute(
                    'UPDATE users SET lastname = %s WHERE username = %s', (newValue, selectUser))
                mysql.connection.commit()
            if changeSection == 'userType':
                cursor.execute(
                    'UPDATE users SET userType = %s WHERE username = %s', (newValue, selectUser))
                mysql.connection.commit()
            if changeSection == 'licenseNo':
                cursor.execute(
                    'UPDATE users SET licenseNo = %s WHERE username = %s', (newValue, selectUser))
                mysql.connection.commit()


        return redirect(url_for('edituser'))
    return redirect(url_for('login'))
    


#Policy Function returns Policy page


@app.route('/policy')
def policy():
    return render_template('policy.html')

#Car Manage Function allows manager to add, edit, delete cars from database, returns car manage page if manager, else login page.

@app.route('/carmanage', methods=['GET', 'POST', 'DELETE'])
def carmanage():
    if 'manager' in session['type'] and 'logged' in session:

        if request.method == 'GET':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM cars')
            car = cursor.fetchall()
            
            return render_template('carmanage.html', car=car)

        msg = ''
        if request.method == 'POST' and 'license' in request.form and 'color' in request.form and 'model' in request.form and 'make' in request.form and 'location' in request.form and 'rating' in request.form and 'changeSection' not in request.form:
            

            license = request.form['license']
            color = request.form['color']
            model = request.form['model']
            make = request.form['make']
            location = request.form['location']
            rating = request.form['rating']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            sql = "INSERT INTO cars (license, color, model, make, location, rating) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (license, color, model, make, location, rating)
            cursor.execute(sql, val)
            mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM cars')
            car = cursor.fetchall()
            return redirect(url_for('carmanage', car=car))
        
        if request.method == 'POST' and 'license' in request.form and 'newValue' in request.form and 'changeSection' in request.form and 'updatecar' in request.form:
            print("what the fuck")
            license = request.form['license']
            changeSection = request.form['changeSection']
            newValue = request.form['newValue']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if changeSection == 'license':
                cursor.execute(
                    'UPDATE cars SET license = %s WHERE license = %s', (newValue, license))
                mysql.connection.commit()
            if changeSection == 'color':
                cursor.execute(
                    'UPDATE cars SET color = %s WHERE license = %s', (newValue, license))
                mysql.connection.commit()
            if changeSection == 'model':
                cursor.execute(
                    'UPDATE cars SET model = %s WHERE license = %s', (newValue, license))
                mysql.connection.commit()
            if changeSection == 'make':
                cursor.execute(
                    'UPDATE cars SET make = %s WHERE license = %s', (newValue, license))
                mysql.connection.commit()
            if changeSection == 'longlat':
                cursor.execute(
                    'UPDATE cars SET longlat = %s WHERE license = %s', (newValue, license))
                mysql.connection.commit()
            if changeSection == 'location':
                cursor.execute(
                    'UPDATE cars SET location = %s WHERE license = %s', (newValue, license))
                mysql.connection.commit()
            if changeSection == 'rating':
                cursor.execute(
                    'UPDATE cars SET rating = %s WHERE license = %s', (newValue, license))
                mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM cars')
            car = cursor.fetchall()
            return redirect(url_for('carmanage', car=car))

        if request.method == 'POST' and 'license' in request.form and 'delete' in request.form:
            license = request.form['license']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            sql = "DELETE FROM cars WHERE license = %s"
            val = ([license])
            cursor.execute(sql, val)
            mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM cars')
            car = cursor.fetchall()
            return redirect(url_for('carmanage', car=car))

        return render_template('carmanage.html')
        


    return redirect(url_for('login'))
        


        




