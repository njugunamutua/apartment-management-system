#import libraries
from flask import Flask, redirect, render_template, flash, request, url_for, session
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb.cursors
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import uuid
from werkzeug.utils import secure_filename
import os
import shutil

import random
import string

def make_mpesa_code():
    letters = string.ascii_uppercase
    alnum = string.ascii_uppercase + string.digits
    return random.choice(letters) + random.choice(letters) + ''.join(random.choice(alnum) for _ in range(8))

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
# app.secret_key = 'your secret key'
app.secret_key = "apartment_rental"

#code for connection
@app.template_filter('securename')
def securename(value):
    return secure_filename(value or '')
app.config['MYSQL_HOST'] = 'localhost' #hostname
app.config['MYSQL_USER'] = 'apartweb' #username
app.config['MYSQL_PASSWORD'] = 'mynewpass123' #password
#in my case password is null so i am keeping empty
app.config['MYSQL_DB'] = 'apartmentRental_v2' #database name
# Intialize MySQL
class SimpleMySQL:
    def __init__(self, app):
        self.app = app
        self._connection = None
    @property
    def connection(self):
        if self._connection is None or not self._connection.open:
            self._connection = pymysql.connect(
                host=self.app.config['MYSQL_HOST'],
                user=self.app.config['MYSQL_USER'],
                password=self.app.config['MYSQL_PASSWORD'],
                database=self.app.config['MYSQL_DB']
            )
        return self._connection
mysql = SimpleMySQL(app)

mysql = SimpleMySQL(app)
@app.route('/')
def home() :
    return render_template('welcome.html')
    
    
@app.route('/AdminLogin', methods=['GET', 'POST'])
def AdminLogin() :
    error = None
    if request.method == 'POST' and 'adminUsername' in request.form and 'adminPass' in request.form and 'securityPass' in request.form:
        if request.form['adminUsername'] != 'admin' or \
                request.form['adminPass'] != 'secret@123' or \
                request.form['securityPass'] != 'apartment':
            error = 'Invalid credentials'
        else:
            flash('You have logged in successfully!!')
            return redirect(url_for('AdminDashboard'))
    return render_template('AdminLogin.html', error=error)


@app.route('/AdminLogout')
def AdminLogout() :
    log2 = ''
    log2 = 'You have logged out successfully!!'
    return render_template('AdminLogin.html', log2=log2)


@app.route('/TenantLogin', methods=['GET', 'POST'])
def TenantLogin() :
    error = None
    if request.method == 'POST' and 'username' in request.form and 'pswd1' in request.form :
        username = request.form['username']
        password = request.form['pswd1']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM TENANT WHERE EMAIL = % s AND PSWD = % s', (username, password, ))
        account = cursor.fetchone()
        # If account exists in TENANT table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['T_ID']
            session['username'] = account['EMAIL']
            # Redirect to home page
            flash('You have logged in successfully!!')
            return redirect(url_for('TenantDashboard'))
        else:
            # Account doesnt exist or username/password incorrect
            error = ' Invalid Username or Password !!'
    return render_template('TenantLogin.html', error=error)


@app.route('/Logout')
def Logout() :
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    log = ''
    log = 'You have logged out successfully!!'
    return render_template('TenantLogin.html', log=log)


@app.route('/Register', methods=['GET','POST'])
def Register():
    msg1 = ''
    log = ''
    #applying empty validation
    if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'phNo' in request.form and 'dob' in request.form and 'occupation' in request.form and 'gender' in request.form and 'email' in request.form and 'pswd' in request.form:
        #passing HTML form data into python variable
        fname = request.form['firstname']
        lname = request.form['lastname']
        ph = request.form['phNo']
        dob = request.form['dob']
        gender = request.form['gender']
        occupation = request.form['occupation']
        email = request.form['email']
        pswd = request.form['pswd']
        if len(ph) != 10 :
            msg1 = 'Phone No. must be of 10 digits!!'
            return render_template('TenantRegister.html', msg1=msg1)
        #creating variable for connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #query to check given data is present in database or no
        cursor.execute('SELECT * FROM TENANT WHERE EMAIL = % s', (email,))
        #fetching data from MySQL
        result = cursor.fetchone()
        if result:
            msg1 = 'Email already exists !'
        else:
            #executing query to insert new data into MySQL
            cursor.execute('INSERT INTO TENANT VALUES (% s, % s, NULL , % s, % s, % s , % s , % s , NULL, % s)', (fname, lname, ph, email, gender ,dob, occupation,pswd))
            mysql.connection.commit()
            #displaying message
            log = 'You have successfully registered !'
            return render_template('TenantLogin.html', log=log)          
    elif request.method == 'POST':
        msg1 = 'Please fill out the form !'
    return render_template('TenantRegister.html', msg1=msg1)


@app.route('/TenantRegister')
def tregister() :
    return render_template('TenantRegister.html')


#----------- ADMIN DASHBOARD----------------


@app.route('/AdminDashboard')
def AdminDashboard() :
    occ_apts=''
    unocc_apts=''
    t_tenants=''
    t_users=''
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  
    cursor.execute('SELECT COUNT(T_ID) AS T_USERS FROM TENANT')
    mysql.connection.commit()
    result1=cursor.fetchone()
    t_users = result1['T_USERS'] 
    cursor.execute('SELECT COUNT(T_ID) AS T_TENANTS FROM TENANT WHERE ROOM_NO IS NOT NULL')
    mysql.connection.commit()
    result2=cursor.fetchone()
    t_tenants = result2['T_TENANTS'] 
    cursor.execute('SELECT COUNT(ROOM_NO) AS T_APTS FROM APARTMENT WHERE APT_STATUS = "Occupied"')
    mysql.connection.commit()
    result3=cursor.fetchone()
    occ_apts = result3['T_APTS'] 
    cursor.execute('SELECT COUNT(ROOM_NO) AS T_APTS FROM APARTMENT WHERE APT_STATUS = "Unoccupied"')
    mysql.connection.commit()
    result4=cursor.fetchone()
    unocc_apts = result4['T_APTS']  
    tot_apt = unocc_apts + occ_apts  
    cursor.execute('SELECT COUNT(BLOCK_NO) AS T_BLOCK FROM APARTMENT_BLOCK')
    mysql.connection.commit()
    result5=cursor.fetchone()
    tot_blck = result5['T_BLOCK']
    cursor.execute('SELECT SUM(R.RENT_FEE) AS T_RENT FROM RENT AS R, RENT_STATUS AS S WHERE R.RENT_ID = S.RENT_ID AND S.R_STATUS = "Paid"')
    mysql.connection.commit()
    result6=cursor.fetchone()
    tot_rent = result6['T_RENT'] 
    if tot_rent == None :
        tot_rent = 0
    return render_template('AdminDashboard.html', occ_apts=occ_apts, unocc_apts=unocc_apts, t_tenants=t_tenants, t_users=t_users, tot_apt=tot_apt, tot_blck=tot_blck, tot_rent=tot_rent)

@app.route('/BlockBreakdown')
def BlockBreakdown() :
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #per-block breakdown: how many units each block actually has, and their status
    cursor.execute('''SELECT B.BLOCK_NO, B.BLOCK_NAME,
                              COUNT(A.ROOM_NO) AS TOTAL_UNITS,
                              SUM(CASE WHEN A.APT_STATUS = "Occupied" THEN 1 ELSE 0 END) AS OCCUPIED,
                              SUM(CASE WHEN A.APT_STATUS = "Unoccupied" THEN 1 ELSE 0 END) AS VACANT
                       FROM APARTMENT_BLOCK AS B
                       LEFT JOIN APARTMENT AS A ON A.BLOCK_NO = B.BLOCK_NO
                       GROUP BY B.BLOCK_NO, B.BLOCK_NAME
                       ORDER BY B.BLOCK_NO''')
    mysql.connection.commit()
    block_breakdown = cursor.fetchall()
    #per-block, per-bedroom-type breakdown, e.g. Block 1 -> 1 Bedroom: 10 units, 8 occupied, 2 vacant
    cursor.execute('''SELECT BLOCK_NO, BEDROOM_TYPE,
                              COUNT(*) AS TOTAL_UNITS,
                              SUM(CASE WHEN APT_STATUS = "Occupied" THEN 1 ELSE 0 END) AS OCCUPIED,
                              SUM(CASE WHEN APT_STATUS = "Unoccupied" THEN 1 ELSE 0 END) AS VACANT
                       FROM APARTMENT
                       WHERE BEDROOM_TYPE IS NOT NULL
                       GROUP BY BLOCK_NO, BEDROOM_TYPE
                       ORDER BY BLOCK_NO, BEDROOM_TYPE''')
    mysql.connection.commit()
    bedroom_type_breakdown = cursor.fetchall()
    return render_template('BlockBreakdown.html', block_breakdown=block_breakdown, bedroom_type_breakdown=bedroom_type_breakdown) 
   
@app.route('/TotalUsers')
def TotalUsers() :
    msg5=''   
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT FNAME, LNAME, GENDER, PH_NO, EMAIL, ROOM_NO FROM TENANT')
    mysql.connection.commit()
    msg5=cursor.fetchall()
    return render_template('TotalUsers.html', msg5=msg5)


@app.route('/tenantReport', methods=['GET','POST'])
def tenantReport() :
    tenantReport=''
    msg6=''
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'tid' in request.form :
        #passing HTML form data into python variable
        T_ID = request.form['tid']
        #query to check given data is present in database or no
        cursor.execute('SELECT * FROM TENANT WHERE T_ID = % s', (T_ID,))
        #fetching data from MySQL
        result = cursor.fetchone()
        if result:
            #executing query to insert new data into MySQL
            cursor.execute('DELETE FROM TENANT WHERE T_ID = % s',(T_ID,))
            mysql.connection.commit()
        else:
            msg6 = 'Tenant doesn\'t exists !'
    elif request.method == 'POST':
        msg6 = 'Please fill out the details !'
    cursor.execute('SELECT T_ID, FNAME, LNAME, GENDER, PH_NO, EMAIL, ROOM_NO FROM TENANT WHERE ROOM_NO IS NOT NULL')
    mysql.connection.commit()
    tenantReport=cursor.fetchall()
    return render_template('tenantReport.html', msg6=msg6,tenantReport=tenantReport)


@app.route('/ApartmentRooms', methods=['POST','GET'])
def ApartmentRooms() :
    msg2=''
    msg3=''
    aptTitle = ''
    description = ''
    area = ''
    Rent=0
    Room = 0
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'room' in request.form and 'block' in request.form and 'status' in request.form and 'rentPerMonth' in request.form and 'floor' in request.form and 'bedroomType' in request.form:
        #passing HTML form data into python variable
        Room = request.form['room']
        Block = request.form['block']
        Floor = request.form['floor']
        BedroomType = request.form['bedroomType']
        Status = request.form['status']
        Rent = request.form['rentPerMonth']
        aptTitle = request.form['apartmentTitle'] 
        description = request.form.get('desc')
        area = request.form['area']
        file1 = request.files['hall']
        file2 = request.files['kitchen']
        file3 = request.files['bedroom']
        file4 = request.files['extra']
        path = 'static/images/apartment'+Room
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
        file1.save(os.path.join('static/images/apartment'+Room, secure_filename(file1.filename)))
        file2.save(os.path.join('static/images/apartment'+Room, secure_filename(file2.filename)))
        file3.save(os.path.join('static/images/apartment'+Room, secure_filename(file3.filename)))
        file4.save(os.path.join('static/images/apartment'+Room, secure_filename(file4.filename)))
        #query to check given data is present in database or no
        cursor.execute('SELECT * FROM APARTMENT WHERE ROOM_NO = % s', (Room,))
        #fetching data from MySQL
        result = cursor.fetchone()
        if result:
            msg2 = 'Apartment already exists !'
        else:
            #executing query to insert new data into MySQL
            cursor.execute('INSERT INTO APARTMENT VALUES (% s, % s, % s, % s, % s, % s)', (Room, Block, Floor, BedroomType, Rent, Status))
            mysql.connection.commit()
            cursor.execute('INSERT INTO APARTMENT_DETAILS VALUES (% s, % s, % s, % s)', (Room, aptTitle, area, description))
            mysql.connection.commit()
            Image_url = 'images/apartment'+Room
            cursor.execute('INSERT INTO APARTMENT_PHOTOS VALUES (% s, % s, %s, %s, %s, %s)', (Room, Image_url, secure_filename(file1.filename), secure_filename(file2.filename), secure_filename(file3.filename), secure_filename(file4.filename)))
            mysql.connection.commit()
            #displaying message
            msg2 = 'You have successfully added an Apartment !'
    elif request.method == 'POST':
        msg2 = 'Please fill out the form !'
    cursor.execute('SELECT APT_TITLE, A.ROOM_NO, A.BLOCK_NO, A.FLOOR_NO, A.BEDROOM_TYPE, AREA, RENT_PER_MONTH, APARTMENT_DESC FROM APARTMENT AS A, APARTMENT_DETAILS AS AD WHERE A.ROOM_NO = AD.ROOM_NO AND A.APT_STATUS = "Unoccupied"')
    mysql.connection.commit()
    msg3=cursor.fetchall()
    cursor.execute('SELECT * FROM APARTMENT_PHOTOS')
    mysql.connection.commit()
    img_url = cursor.fetchall()
    return render_template('ApartmentRooms.html',msg2=msg2,msg3=msg3,img_url=img_url)


@app.route('/UpdateApartment', methods=['GET','POST'])
def UpdateApartment():
    msg2=''
    msg3=''
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'room1' in request.form and 'status1' in request.form and 'rentPerMonth1' in request.form :
        #passing HTML form data into python variable
        Room1 = request.form['room1']
        Status1 = request.form['status1']
        Rent1 = request.form['rentPerMonth1']
        area1 = request.form['up_area']
        title1 = request.form['up_title']
        Floor1 = request.form.get('up_floor') or None
        BedroomType1 = request.form.get('up_bedroomType') or None
        #query to check given data is present in database or no
        cursor.execute('SELECT * FROM APARTMENT WHERE ROOM_NO = % s', (Room1,))
        #fetching data from MySQL
        result = cursor.fetchone()
        if result:
            #executing query to insert new data into MySQL
            cursor.execute('UPDATE APARTMENT SET RENT_PER_MONTH = % s, APT_STATUS = % s WHERE ROOM_NO = % s',(Rent1,Status1,Room1))
            mysql.connection.commit()
            if Floor1 is not None:
                cursor.execute('UPDATE APARTMENT SET FLOOR_NO = % s WHERE ROOM_NO = % s',(Floor1,Room1))
                mysql.connection.commit()
            if BedroomType1 is not None:
                cursor.execute('UPDATE APARTMENT SET BEDROOM_TYPE = % s WHERE ROOM_NO = % s',(BedroomType1,Room1))
                mysql.connection.commit()
            cursor.execute('UPDATE APARTMENT_DETAILS SET AREA = % s, APT_TITLE = % s WHERE ROOM_NO = % s',(area1,title1,Room1))
            mysql.connection.commit()
        else:
            msg2 = 'Apartment doesn\'t exists !'
    elif request.method == 'POST':
        msg2 = 'Please fill out the form !'
    cursor.execute('SELECT APT_TITLE, A.ROOM_NO, A.BLOCK_NO, A.FLOOR_NO, A.BEDROOM_TYPE, AREA, RENT_PER_MONTH, APARTMENT_DESC FROM APARTMENT AS A, APARTMENT_DETAILS AS AD WHERE A.ROOM_NO = AD.ROOM_NO AND A.APT_STATUS = "Unoccupied"')
    mysql.connection.commit()
    msg3=cursor.fetchall() 
    cursor.execute('SELECT * FROM APARTMENT_PHOTOS')
    mysql.connection.commit()
    img_url = cursor.fetchall()
    return render_template('ApartmentRooms.html', msg2=msg2,msg3=msg3,img_url=img_url)


@app.route('/DeleteApartment', methods=['GET','POST'])
def DeleteApartment() :
    msg2=''
    msg3=''
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'room2' in request.form :
        #passing HTML form data into python variable
        Room2 = request.form['room2']
        #query to check given data is present in database or no
        cursor.execute('SELECT * FROM APARTMENT WHERE ROOM_NO = % s', (Room2,))
        #fetching data from MySQL
        result = cursor.fetchone()
        if result:
            #executing query to insert new data into MySQL
            cursor.execute('SELECT PATHNAME FROM APARTMENT_PHOTOS WHERE ROOM_NO = % s',(Room2,))
            mysql.connection.commit()
            path = cursor.fetchone()
            pathname = 'static/'+path['PATHNAME']
            shutil.rmtree(pathname, ignore_errors=False, onerror=None)
            cursor.execute('DELETE FROM APARTMENT WHERE ROOM_NO = % s',(Room2,))
            mysql.connection.commit()
        else:
            msg2 = 'Apartment doesn\'t exists !'
    elif request.method == 'POST':
        msg2 = 'Please fill out the form !'
    cursor.execute('SELECT APT_TITLE, A.ROOM_NO, A.BLOCK_NO, A.FLOOR_NO, A.BEDROOM_TYPE, AREA, RENT_PER_MONTH, APARTMENT_DESC FROM APARTMENT AS A, APARTMENT_DETAILS AS AD WHERE A.ROOM_NO = AD.ROOM_NO AND A.APT_STATUS = "Unoccupied"')
    mysql.connection.commit()
    msg3=cursor.fetchall() 
    cursor.execute('SELECT * FROM APARTMENT_PHOTOS')
    mysql.connection.commit()
    img_url = cursor.fetchall()
    return render_template('ApartmentRooms.html', msg2=msg2,msg3=msg3,img_url=img_url)

@app.route('/RentStatus')
def RentStatus() :
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT FNAME, LNAME, T.ROOM_NO, RENT_PER_MONTH, DUE_DATE, R_STATUS, LATE_FEE FROM RENT AS R, APARTMENT AS A, RENT_STATUS AS RS, TENANT AS T WHERE R.RENT_ID = RS.RENT_ID AND T.T_ID = R.T_ID AND A.ROOM_NO = T.ROOM_NO')
    mysql.connection.commit()
    rent_status=cursor.fetchall()
    unpaid_list = [row for row in rent_status if row['R_STATUS'] == 'Unpaid']
    paid_list = [row for row in rent_status if row['R_STATUS'] == 'Paid']
    cursor.execute('''SELECT
            COALESCE(SUM(CASE WHEN RS.R_STATUS = "Paid" AND MONTH(R.DUE_DATE)=MONTH(CURDATE()) AND YEAR(R.DUE_DATE)=YEAR(CURDATE()) THEN R.RENT_FEE ELSE 0 END),0) AS paid_total,
            COALESCE(SUM(CASE WHEN RS.R_STATUS = "Unpaid" AND MONTH(R.DUE_DATE)=MONTH(CURDATE()) AND YEAR(R.DUE_DATE)=YEAR(CURDATE()) THEN R.RENT_FEE ELSE 0 END),0) AS unpaid_total,
            SUM(CASE WHEN RS.R_STATUS = "Paid" AND MONTH(R.DUE_DATE)=MONTH(CURDATE()) AND YEAR(R.DUE_DATE)=YEAR(CURDATE()) THEN 1 ELSE 0 END) AS paid_count,
            SUM(CASE WHEN RS.R_STATUS = "Unpaid" AND MONTH(R.DUE_DATE)=MONTH(CURDATE()) AND YEAR(R.DUE_DATE)=YEAR(CURDATE()) THEN 1 ELSE 0 END) AS unpaid_count
        FROM RENT AS R JOIN RENT_STATUS AS RS ON R.RENT_ID = RS.RENT_ID''')
    mysql.connection.commit()
    totals = cursor.fetchone()
    return render_template('RentStatus.html',rent_status=rent_status, unpaid_list=unpaid_list, paid_list=paid_list, totals=totals)

@app.route('/UpdatedRentStatus')
def UpdatedRentStatus() :
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''SELECT T.T_ID, T.ROOM_NO, A.RENT_PER_MONTH FROM TENANT AS T
                       JOIN APARTMENT AS A ON T.ROOM_NO = A.ROOM_NO
                       WHERE T.ROOM_NO IS NOT NULL''')
    mysql.connection.commit()
    occupied = cursor.fetchall()
    created = 0
    for t in occupied:
        cursor.execute('''SELECT RENT_ID FROM RENT WHERE T_ID = % s
                           AND MONTH(DUE_DATE) = MONTH(CURDATE()) AND YEAR(DUE_DATE) = YEAR(CURDATE())''', (t['T_ID'],))
        existing = cursor.fetchone()
        if not existing:
            cursor.execute('INSERT INTO RENT (RENT_FEE, T_ID, DUE_DATE, LATE_FEE, PAYMENT_ID) VALUES (% s, % s, % s, % s, % s)',
                            (t['RENT_PER_MONTH'], t['T_ID'], date.today(), 0, None))
            mysql.connection.commit()
            new_rent_id = cursor.lastrowid
            cursor.execute('INSERT INTO RENT_STATUS VALUES (% s, % s)', (new_rent_id, 'Unpaid'))
            mysql.connection.commit()
            created += 1
    flash(str(created) + " new rent record(s) generated for this month.")
    return redirect(url_for('RentStatus'))
@app.route('/Backup')
def Backup() :
    backup_status=''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT T_ID, FNAME, LNAME, GENDER, PH_NO, EMAIL, ROOM_NO FROM TENANT_BACKUP ')
    mysql.connection.commit()
    backup_status=cursor.fetchall()
    # cursor.execute('CALL RENTUPDATE()')
    # mysql.connection.commit()
    return render_template('backup.html',backup_status=backup_status)


#---------------------------------------------- TENANT DASHBOARD---------------------------------------------


@app.route('/TenantDashboard')
def TenantDashboard() :
    if 'loggedin' in session:
        return render_template('TenantDashboard.html')
    return render_template('TenantLogin.html')

@app.route('/ReportIssue', methods=['GET','POST'])
def ReportIssue():
    if 'loggedin' not in session:
        return render_template('TenantLogin.html')
    msg = None
    err = None
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST' and 'title' in request.form and 'description' in request.form:
        title = request.form['title']
        description = request.form['description']
        T_id = session['id']
        cursor.execute('SELECT ROOM_NO FROM TENANT WHERE T_ID = % s', (T_id,))
        tenant_row = cursor.fetchone()
        room_no = tenant_row['ROOM_NO'] if tenant_row else None
        cursor.execute('INSERT INTO MAINTENANCE_REQUEST (T_ID, ROOM_NO, ISSUE_TITLE, DESCRIPTION, STATUS, DATE_REPORTED) VALUES (% s, % s, % s, % s, % s, % s)',
                        (T_id, room_no, title, description, 'Open', date.today()))
        mysql.connection.commit()
        msg = 'Your issue has been reported. We will get back to you soon.'
    elif request.method == 'POST':
        err = 'Please fill out both fields.'
    return render_template('ReportIssue.html', msg=msg, err=err)


@app.route('/MyRequests')
def MyRequests():
    if 'loggedin' not in session:
        return render_template('TenantLogin.html')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM MAINTENANCE_REQUEST WHERE T_ID = % s ORDER BY DATE_REPORTED DESC', (session['id'],))
    requests = cursor.fetchall()
    return render_template('MyRequests.html', requests=requests)


@app.route('/MaintenanceRequests')
def MaintenanceRequests():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''SELECT M.*, T.FNAME, T.LNAME FROM MAINTENANCE_REQUEST AS M
                       LEFT JOIN TENANT AS T ON M.T_ID = T.T_ID
                       ORDER BY FIELD(M.STATUS, "Open","In Progress","Resolved"), M.DATE_REPORTED DESC''')
    requests = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) AS c FROM MAINTENANCE_REQUEST WHERE STATUS = "Open"')
    open_count = cursor.fetchone()['c']
    cursor.execute('SELECT COUNT(*) AS c FROM MAINTENANCE_REQUEST WHERE STATUS = "In Progress"')
    progress_count = cursor.fetchone()['c']
    cursor.execute('SELECT COUNT(*) AS c FROM MAINTENANCE_REQUEST WHERE STATUS = "Resolved"')
    resolved_count = cursor.fetchone()['c']
    return render_template('MaintenanceRequests.html', requests=requests, open_count=open_count, progress_count=progress_count, resolved_count=resolved_count)


@app.route('/UpdateMaintenanceStatus', methods=['POST'])
def UpdateMaintenanceStatus():
    if request.method == 'POST' and 'request_id' in request.form and 'new_status' in request.form:
        req_id = request.form['request_id']
        new_status = request.form['new_status']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if new_status == 'Resolved':
            cursor.execute('UPDATE MAINTENANCE_REQUEST SET STATUS = % s, DATE_RESOLVED = % s WHERE REQUEST_ID = % s', (new_status, date.today(), req_id))
        else:
            cursor.execute('UPDATE MAINTENANCE_REQUEST SET STATUS = % s, DATE_RESOLVED = NULL WHERE REQUEST_ID = % s', (new_status, req_id))
        mysql.connection.commit()
    return redirect(url_for('MaintenanceRequests'))

@app.route('/RentApartment')
def rentApartment() :
    #optional filters coming from the search form: ?block=1&bedroomType=2 Bedroom
    block_filter = request.args.get('block', '').strip()
    bedroom_filter = request.args.get('bedroomType', '').strip()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = ('SELECT APT_TITLE, A.ROOM_NO, A.BLOCK_NO, A.FLOOR_NO, A.BEDROOM_TYPE, AREA, RENT_PER_MONTH, APARTMENT_DESC '
             'FROM APARTMENT AS A, APARTMENT_DETAILS AS AD '
             'WHERE A.ROOM_NO = AD.ROOM_NO AND A.APT_STATUS = "Unoccupied"')
    params = []
    if block_filter:
        query += ' AND A.BLOCK_NO = % s'
        params.append(block_filter)
    if bedroom_filter:
        query += ' AND A.BEDROOM_TYPE = % s'
        params.append(bedroom_filter)
    query += ' ORDER BY A.BLOCK_NO, A.FLOOR_NO, A.ROOM_NO'
    cursor.execute(query, tuple(params))
    mysql.connection.commit()
    apartment=cursor.fetchall()
    cursor.execute('SELECT * FROM APARTMENT_PHOTOS')
    mysql.connection.commit()
    img_url = cursor.fetchall()
    #for the filter dropdowns: every block, and every bedroom type currently in use
    cursor.execute('SELECT BLOCK_NO, BLOCK_NAME FROM APARTMENT_BLOCK ORDER BY BLOCK_NO')
    mysql.connection.commit()
    blocks = cursor.fetchall()
    cursor.execute('SELECT DISTINCT BEDROOM_TYPE FROM APARTMENT WHERE BEDROOM_TYPE IS NOT NULL ORDER BY BEDROOM_TYPE')
    mysql.connection.commit()
    bedroom_types = cursor.fetchall()
    return render_template('RentApartment.html',apartment=apartment, img_url=img_url, blocks=blocks, bedroom_types=bedroom_types, block_filter=block_filter, bedroom_filter=bedroom_filter)

@app.route('/Details', methods=['GET','POST'])
def Details() :
    Error=''
    Uname=''
    Tname=''
    PAddress=''
    aptNo=''
    TFatherName=''
    Date = date.today()
    rentAmt= 0
    Deposit= 0
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'Username' in request.form and 'aptNo' in request.form and 'TFatherName' in request.form and 'PerAddr' in request.form :
        Uname = request.form['Username']
        aptNo = request.form['aptNo']
        TFatherName = request.form['TFatherName']
        PAddress = request.form['PerAddr']
        cursor.execute('SELECT T_ID FROM TENANT WHERE EMAIL= % s',(Uname,))
        mysql.connection.commit()
        tid_list1 = cursor.fetchone()
        t_id = tid_list1['T_ID']
        cursor.execute('SELECT RENT_PER_MONTH FROM APARTMENT WHERE ROOM_NO = %s AND APT_STATUS = "Unoccupied"',(aptNo,))
        mysql.connection.commit()
        res1 = cursor.fetchone()
        if t_id != None and res1 != None :
            cursor.execute('SELECT FNAME,LNAME FROM TENANT WHERE T_ID = %s',(t_id,))
            mysql.connection.commit()
            res = cursor.fetchone()
            Tname = res['FNAME']+' '+res['LNAME']
            rentAmt=res1['RENT_PER_MONTH']
            Deposit = rentAmt * 2
            return redirect(url_for('Contract', aptNo=aptNo ,Tname=Tname, TFatherName=TFatherName, Uname=Uname,PAddress=PAddress, Date=Date, rentAmt=rentAmt, Deposit=Deposit))
        else :
            Error = 'Invalid Username or Apartment No.!!'
    elif request.method == 'POST' :
        Error= 'Please fill out the form!'
    return render_template('Details.html', Error=Error)



@app.route('/alreadyTenant', methods=['GET','POST'])
def alreadyTenant() :
    Error=''
    Uname=''
    Tname=''
    aptNo=''
    rentAmt= 0
    PhNo=''
    late_fee=0
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'Username' in request.form and 'aptNo' in request.form :
        Uname = request.form['Username']
        aptNo = request.form['aptNo']
        cursor.execute('SELECT T_ID, PH_NO FROM TENANT WHERE EMAIL = % s',(Uname,))
        mysql.connection.commit()
        tid_list1 = cursor.fetchone()
        t_id = tid_list1['T_ID']
        PhNo = tid_list1['PH_NO']
        cursor.execute('''SELECT R.LATE_FEE FROM RENT AS R JOIN RENT_STATUS AS RS ON R.RENT_ID = RS.RENT_ID
                           WHERE R.T_ID = % s AND RS.R_STATUS = "Unpaid" ORDER BY R.DUE_DATE DESC LIMIT 1''', (t_id,))
        mysql.connection.commit()
        latefee_list = cursor.fetchone()
        if latefee_list is None:
            return render_template('alreadyTenant.html', Error="No rent is currently due for this tenant.")
        late_fee = latefee_list['LATE_FEE'] or 0
        totAmt = int(rentAmt) + int(late_fee)
        # PhNo='9876543212'
        cursor.execute('SELECT RENT_PER_MONTH FROM APARTMENT WHERE ROOM_NO = %s AND APT_STATUS = "Occupied"',(aptNo,))
        mysql.connection.commit()
        res1 = cursor.fetchone()
        if t_id != None and res1 != None :
            cursor.execute('SELECT FNAME,LNAME FROM TENANT WHERE T_ID = %s',(t_id,))
            mysql.connection.commit()
            res = cursor.fetchone()
            Tname = res['FNAME']+' '+res['LNAME']
            rentAmt=res1['RENT_PER_MONTH']
            late_fee = late_fee
            totAmt = int(rentAmt) + int(late_fee)
            return redirect(url_for('Payment1', aptNo=aptNo ,Tname=Tname, Uname=Uname,PhNo=PhNo , rentAmt=rentAmt, late_fee=late_fee, totAmt=totAmt))
        else :
            Error = 'Invalid Username or Apartment No.!!'
    elif request.method == 'POST' :
        Error= 'Please fill out the form!'
    return render_template('alreadyTenant.html', Error=Error)


@app.route('/Contract/<aptNo>/<Tname>/<TFatherName>/<Uname>/<PAddress>/<Date>/<rentAmt>/<Deposit>', methods=['GET','POST'])
def Contract(aptNo,Tname, TFatherName, Uname, PAddress, Date, rentAmt, Deposit) :
    msg7=''
    late_fee=0
    totAmt=0
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'UserName' in request.form and 'aptno' in request.form and 'rent-amt' in request.form and 'deposit' in request.form and 'start_date' in request.form and 'end_date' in request.form and 'pay_date' in request.form and 'terms' in request.form:
        #passing HTML form data into python variable
        end_date = request.form['end_date']
        # pay_date = request.form['pay_date']
        terms = request.form['terms']
        Username = request.form['UserName']
        Apt_no = request.form['aptno']
        start_date = request.form['start_date']
        Deposit = request.form['deposit']
        rentAmt = request.form['rent-amt']
        #creating variable for connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #query to check given data is present in database or no
        cursor.execute('SELECT T_ID FROM TENANT WHERE EMAIL= % s',(Username,))
        mysql.connection.commit()
        tid_list2 = cursor.fetchone()
        T_id = tid_list2['T_ID']
        resDate = datetime.strptime(start_date, '%Y-%m-%d')
        due_date = resDate + relativedelta(months=+2)
        totAmt = int(rentAmt) + int(late_fee)
        #executing query to insert new data into MySQL
        cursor.execute('INSERT INTO CONTRACT VALUES ( NULL , % s, % s, % s , % s , % s , % s)', (T_id, Apt_no, start_date, end_date, Deposit ,terms))
        cursor.execute('INSERT INTO RENT VALUES ( NULL , % s, % s, % s , % s , NULL)', (rentAmt, T_id,due_date, late_fee))
        mysql.connection.commit()
        cursor.execute('''SELECT R.RENT_ID FROM RENT AS R JOIN RENT_STATUS AS RS ON R.RENT_ID = RS.RENT_ID
                           WHERE R.T_ID = % s AND RS.R_STATUS = "Unpaid" ORDER BY R.DUE_DATE DESC LIMIT 1''', (t_id,))
        mysql.connection.commit()
        rentid_list = cursor.fetchone()
        rent_id = rentid_list['RENT_ID'] if rentid_list else None
        cursor.execute('INSERT INTO RENT_STATUS VALUES ( % s, % s)', (rent_id,'Unpaid'))
        cursor.execute('UPDATE TENANT SET ROOM_NO = % s WHERE T_ID = % s',(Apt_no,T_id))
        cursor.execute('UPDATE APARTMENT SET APT_STATUS = "Occupied" WHERE ROOM_NO = % s',(Apt_no,))
        mysql.connection.commit()
        cursor.execute('SELECT PH_NO FROM TENANT WHERE T_ID = % s',(T_id,))
        mysql.connection.commit()
        phone_no = cursor.fetchone()
        PhNo = phone_no['PH_NO']
        #displaying message
        flash('Hope you love Rooftop Apartments... ')
        return redirect(url_for('Payment', aptNo=aptNo ,Tname=Tname, PhNo=PhNo, Uname=Uname, rentAmt=rentAmt, late_fee=late_fee, totAmt=totAmt))
    elif request.method == 'POST' :
        msg7 = 'Please fill out the form !'
    return render_template('contract.html', msg7=msg7, aptNo=aptNo , Date=Date, Tname=Tname, TFatherName=TFatherName, Uname=Uname, PAddress=PAddress, Date1=Date, rentAmt=rentAmt, Deposit=Deposit)


@app.route('/Payment/<aptNo>/<Tname>/<PhNo>/<Uname>/<rentAmt>/<late_fee>/<totAmt>', methods=['GET','POST'])
def Payment(aptNo,Tname,PhNo, Uname, rentAmt, late_fee, totAmt) :
    err=''
    Date = date.today()
    id = uuid.uuid1()
    fields = id.fields
    pay_id = fields[0]
    pay_date = date.today()
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST' and 'email' in request.form and 'roomNo' in request.form :
        Uname = request.form['email']
        aptNo = request.form['roomNo']
        payMethod = request.form.get('payMethod', 'card')
        mpesa_code = ''
        if payMethod == 'mpesa':
            mpesaPhone = request.form.get('mpesaPhone', '')
            if len(mpesaPhone) < 9:
                err = 'Enter a valid M-Pesa phone number!!'
                return render_template('Payment.html',err=err, aptNo=aptNo ,Tname=Tname, PhNo=PhNo, Uname=Uname, rentAmt=rentAmt, late_fee=late_fee, totAmt=totAmt)
            mpesa_code = make_mpesa_code()
            Acc_No = mpesa_code
        elif 'acc-no' in request.form and 'cardNo' in request.form and 'cvv' in request.form :
            Acc_No = request.form['acc-no']
            card_No = request.form['cardNo']
            cvv = request.form['cvv']
            if len(card_No) != 11 and len(cvv) != 3:
                err = 'Invalid Card No or cvv!!'
                return render_template('Payment.html',err=err, aptNo=aptNo ,Tname=Tname, PhNo=PhNo, Uname=Uname, rentAmt=rentAmt, late_fee=late_fee, totAmt=totAmt)
        else:
            err = 'Please fill out the form!'
            return render_template('Payment.html',err=err, aptNo=aptNo ,Tname=Tname, PhNo=PhNo, Uname=Uname, rentAmt=rentAmt, late_fee=late_fee, totAmt=totAmt)
        cursor.execute('SELECT T_ID FROM TENANT WHERE EMAIL= % s',(Uname,))
        mysql.connection.commit()
        tid_list1 = cursor.fetchone()
        t_id = tid_list1['T_ID']
        cursor.execute('''SELECT R.RENT_ID FROM RENT AS R JOIN RENT_STATUS AS RS ON R.RENT_ID = RS.RENT_ID
                           WHERE R.T_ID = % s AND RS.R_STATUS = "Unpaid" ORDER BY R.DUE_DATE DESC LIMIT 1''', (t_id,))
        mysql.connection.commit()
        rentid_list = cursor.fetchone()
        rent_id = rentid_list['RENT_ID'] if rentid_list else None
        if t_id != None and aptNo != None :
            cursor.execute('INSERT INTO PAYMENT VALUES(% s, % s, % s, % s, % s)',(pay_id,Acc_No,t_id,Date,rentAmt))
            cursor.execute('UPDATE RENT SET PAYMENT_ID = % s WHERE RENT_ID = % s',(pay_id, rent_id))
            cursor.execute('UPDATE RENT_STATUS SET R_STATUS = "Paid" WHERE RENT_ID = % s',(rent_id,))
            cursor.execute('UPDATE TENANT SET ROOM_NO = % s WHERE T_ID = % s',(aptNo,t_id))
            cursor.execute('UPDATE APARTMENT SET APT_STATUS = "Occupied" WHERE ROOM_NO = % s',(aptNo,))
            mysql.connection.commit()
            pay_amt = rentAmt
            return redirect(url_for('Receipt',Tname=Tname, pay_id=pay_id, pay_date=pay_date ,pay_amt=pay_amt, payMethod=payMethod, mpesaCode=(mpesa_code or '-')))
    elif request.method == 'POST' :
        err= 'Please fill out the form!'
    return render_template('Payment.html',err=err, aptNo=aptNo ,Tname=Tname, PhNo=PhNo, Uname=Uname, rentAmt=rentAmt, late_fee=late_fee, totAmt=totAmt)  


@app.route('/Payment1/<aptNo>/<Tname>/<PhNo>/<Uname>/<rentAmt>/<late_fee>/<totAmt>', methods=['GET','POST'])
def Payment1(aptNo,Tname,PhNo, Uname, rentAmt, late_fee, totAmt) :
    err='Payment Unsuccessfull'
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST' and 'email' in request.form and 'roomNo' in request.form and 'acc-no' in request.form :
        Uname = request.form['email']
        aptNo = request.form['roomNo']
        pay_date = request.form['pay_date']
        Acc_No = request.form['acc-no']
        id = uuid.uuid1()
        fields = id.fields
        pay_id = fields[0]
        Date = date.today()
        cursor.execute('SELECT T_ID FROM TENANT WHERE EMAIL= % s',(Uname,))
        mysql.connection.commit()
        tid_list1 = cursor.fetchone()
        t_id = tid_list1['T_ID']
        cursor.execute('''SELECT R.RENT_ID FROM RENT AS R JOIN RENT_STATUS AS RS ON R.RENT_ID = RS.RENT_ID
                           WHERE R.T_ID = % s AND RS.R_STATUS = "Unpaid" ORDER BY R.DUE_DATE DESC LIMIT 1''', (t_id,))
        mysql.connection.commit()
        rentid_list = cursor.fetchone()
        rent_id = rentid_list['RENT_ID'] if rentid_list else None
        if t_id != None and aptNo != None :
            cursor.execute('INSERT INTO PAYMENT VALUES(% s, % s, % s, % s, % s)',(pay_id,Acc_No,t_id,Date,rentAmt))
            cursor.execute('UPDATE RENT SET PAYMENT_ID = % s WHERE RENT_ID = % s',(pay_id, rent_id))
            cursor.execute('UPDATE RENT_STATUS SET R_STATUS = "Paid" WHERE RENT_ID = % s',(rent_id,))
            mysql.connection.commit()
            pay_amt = rentAmt
            return redirect(url_for('Receipt',Tname=Tname, pay_id=pay_id, pay_date=pay_date ,pay_amt=pay_amt))
    return render_template('Payment.html', err=err,aptNo=aptNo ,Tname=Tname, PhNo=PhNo, Uname=Uname, rentAmt=rentAmt, late_fee=late_fee, totAmt=totAmt)

 
 
@app.route('/Receipt/<Tname>/<pay_id>/<pay_date>/<pay_amt>', methods=['GET','POST'])
def Receipt(Tname,pay_id,pay_date,pay_amt) :
    payMethod = request.args.get('payMethod', 'card')
    mpesaCode = request.args.get('mpesaCode', '-')
    return render_template('Reciept.html', Tname=Tname, pay_id=pay_id, pay_date=pay_date ,pay_amt=pay_amt, payMethod=payMethod, mpesaCode=mpesaCode)




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000)
    app.run(host="0.0.0.0", port=port, debug=False)
