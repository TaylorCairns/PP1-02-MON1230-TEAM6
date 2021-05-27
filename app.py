from flask import Flask, render_template, request, url_for, session, redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib
from datetime import datetime, timedelta
import math

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

        # Chec if account exists
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


@app.route('/rent')
def rent():
    
        if request.method == 'GET':
            user = 'red'
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM bookings WHERE completed = %s AND username = %s', ('No', 'red',))
            history = cursor.fetchall()
            mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM bookings WHERE completed = %s AND username = %s', ('Yes', 'red',))
            past = cursor.fetchall()
            mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            cursor.execute('SELECT * FROM cars')
            cars = cursor.fetchall()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            cursor.execute('SELECT * FROM cars WHERE NOT longlat IS NULL')
            carsLoc = cursor.fetchall()
            
            session
            
            my_string = ""
            for row in carsLoc:
                labelName = str(row['carId'])
                my_string = my_string + '&markers=color:' + row['color'] + '%7Clabel:' + labelName + '%7C' + row['longlat'] + '|'

            #print(my_string)
            




 
            return render_template('rent.html', userType='admin', userHistory=history, username=user, cars=cars, past=past, my_string=my_string)

        return render_template('rent.html', userType='admin', username='red')
        

            
    



@app.route('/booking', methods=['GET', 'POST'])
def booking():
    
        if request.method == 'POST':
                user = 'red'
                


                carLicense = request.form['carLicense']
                date = request.form['date']
                time = request.form['time']


                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM cars WHERE license = %s', (carLicense, ))


                cars = cursor.fetchone()
                mysql.connection.commit()

                
            

                if cars:
                    
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('INSERT INTO bookings (username, license, date, completed, time) VALUES (%s, %s, %s, %s, %s)', (user, carLicense, date, 'No', time))
                    mysql.connection.commit()

        return redirect(url_for('rent'))
    

@app.route('/cancelBooking', methods=['GET', 'POST'])
def cancelBooking():
    
        if request.method == 'POST' and 'cancelId' in request.form:
            user = 'red'
            cancelId = request.form['cancelId']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM bookings WHERE id = %s AND username = %s', (cancelId, user))
            cancelBooking = cursor.fetchone()
            mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM bookings WHERE username = %s', (user, ))

            history = cursor.fetchall()
            mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM cars')
            cars = cursor.fetchall()
            mysql.connection.commit()

            if cancelBooking:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('UPDATE bookings SET completed = %s WHERE id = %s', ('Yes', cancelId))
                mysql.connection.commit()
                

                return redirect(url_for('rent'))
            return redirect(url_for('rent'))
        return redirect(url_for('rent'))



    



@app.route('/logout', methods=['GET', 'POST'])
def logout():
    

    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    

        if request.method == 'GET':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM users WHERE username = %s', ('red',))
            user = cursor.fetchone()
            return render_template('profile.html', typeOfUser='admin', user=user)

        msg = ''
        if request.method == 'POST' and 'newValue' in request.form and 'changeSection' in request.form:
            #selectUser = request.form['selectUser']
            changeSection = request.form['changeSection']
            newValue = request.form['newValue']

            print(changeSection)

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if changeSection == 'firstname':
                cursor.execute(
                    'UPDATE users SET firstname = %s WHERE username = %s', (newValue, 'red'))
                mysql.connection.commit()
            if changeSection == 'lastname':
                cursor.execute(
                    'UPDATE users SET lastname = %s WHERE username = %s', (newValue, 'red'))
                mysql.connection.commit()
            if changeSection == 'email':
                cursor.execute(
                    'UPDATE users SET email = %s WHERE username = %s', (newValue, 'red'))
                mysql.connection.commit()
            if changeSection == 'licenseNo':
                cursor.execute(
                    'UPDATE users SET licenseNo = %s WHERE username = %s', (newValue, 'red'))
                mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM users WHERE username = %s', ('red',))
            user = cursor.fetchone()
            return render_template('profile.html', typeOfUser='admin', user=user)

        return render_template('profile.html', typeOfUser='admin', user='red')


    



@app.route('/nearestcar', methods=['GET', 'POST'])

#def distance(origin, destination):
#
#   lat1, lon1 = origin
#    lat2, lon2 = destination
#    radius = 6371  # km
# 
#    dlat = math.radians(lat2-lat1)
#    dlon = math.radians(lon2-lon1)
#    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
#        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
#    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
#    d = radius * c
# 
#    return d
 

#origin = (-37.78451649, 145.125984)              # Bridgeport CT USA
#destination = (41.0772, 73.4687)         # Darien CT  USA
#current = (-37.78, 145.12)

#def distance(point1, point2):
#    return mpu.haversine_distance(point1, point2)

#def closest(data, this_point):
#    return min(data, key=lambda x: distance(this_point, x))
 
#print("Distance in KM : {} ".format(distance(origin, destination)))

def nearestcar():
    if 'logged' in session:
        if request.method == 'POST':
            user = 'admin'
            date = datetime.now()
            
        
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM cars WHERE NOT inuse = %s', ('Yes'))
            cars = cursor.fetchall()
            mysql.connection.commit()

            minDistance = 900000000
            minLongLat = 0
            minLicense = 1
            current = (-37.78, 145.12)
            #print("distance : {}" .format(distance(origin, destination)))
            
            for row in cars:
                destination = row['longlat']
                dist = mpu.haversine_distance(current, destination)
                if dist < minDistance:
                    minDistance = dist
                    minLongLat = row['longlat']
                    minLicense = row['license']
                
                #else: 
                    #print("min Lat Long: {}" .format(minLongLat))
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM cars WHERE longLat = %s', (minLongLat))
            minlongLatCar = cursor.fetchone()
            mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO bookings (username, license, date, completed) VALUES (%s, %s, %s, %s)', (user, minLicense, date, 'No'))
            mysql.connection.commit()


            return redirect(url_for('rent'))


@app.route('/edituser', methods=['GET', 'POST'])
def edituser():
    

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

            print(changeSection)

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

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users')
            user = cursor.fetchall()
            return render_template('editUser.html', user=user)


        return render_template('editUser.html')
    
    



@app.route('/policy')
def policy():
    return render_template('policy.html')


@app.route('/carmanage', methods=['GET', 'POST', 'DELETE'])
def carmanage():
    

        if request.method == 'GET':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM cars')
            car = cursor.fetchall()
            print(car)
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
            # if changeSection == 'lastname':
            #     cursor.execute(
            #         'UPDATE users SET lastname = %s WHERE username = %s', (newValue, selectUser))
            #     mysql.connection.commit()
            # if changeSection == 'userType':
            #     cursor.execute(
            #         'UPDATE users SET userType = %s WHERE username = %s', (newValue, selectUser))
            #     mysql.connection.commit()
            # if changeSection == 'licenseNo':
            #     cursor.execute(
            #         'UPDATE users SET licenseNo = %s WHERE username = %s', (newValue, selectUser))
            #     mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM cars')
            car = cursor.fetchall()
            return render_template('carmanage.html', car=car)

        if request.method == 'POST' and 'license' in request.form and 'newValue' in request.form and 'changeSection' in request.form:
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
            return render_template('carmanage.html', car=car)

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
            return render_template('carmanage.html', car=car)

        return render_template('carmanage.html')

    

