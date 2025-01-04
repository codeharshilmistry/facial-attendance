from flask import Flask, render_template, request, url_for, session, redirect, flash, jsonify, send_file
import pymysql
from flask_session import Session
import base64
import cv2
import face_recognition
import uuid
from io import BytesIO
import numpy as np
import datetime
import ast
import pandas as pd

conn = pymysql.connect(host='localhost', user = 'root', password="", db='attendance')

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def landing_page():
    return render_template('/home.html')

@app.route('/login')
def login():
    return render_template('/login.html')

@app.route('/check_home', methods=['POST'])
def home_page():
    username = request.form['username']
    password = request.form['password']
    if username!='admin1' or password!='password':
        flash("Incorrect Username or Password")
        return redirect(url_for('login'))
    session["name"]= username
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('/home_login.html')

@app.route('/logout')
def logout():
    session["name"] = None
    flash("Logged out !!")
    return redirect('/')

@app.route('/newstudent')
def newstudent():
    return render_template('/newstudent.html')

@app.route('/adddata', methods=['POST'])
def adddata():
    cursor=conn.cursor()
    name = request.form['student_name']
    enrollment = request.form['student_enrollment']
    cursor.execute("SELECT enrollment FROM studentsdata")
    enrollments = cursor.fetchall()
    print("Enrollments :", enrollments)
    flag = False
    for erno in enrollments:
        if enrollment == str(erno[0]):
            flag = True

    if flag:
        flash("Student with enrollment " + enrollment + " exists already")
        return redirect(url_for('newstudent'))

    contact = request.form['student_contact']
    code = str(uuid.uuid4())
    email = request.form['student_email']
    classroom = request.form['student_classroom']
    print(classroom, contact, code)
    temp_image = request.files['student_image']
    image = temp_image.read()
    query = "INSERT INTO studentsdata (name, enrollment, contact, code, email, classroom, image) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (name, enrollment, contact, code, email, classroom, image)
    cursor.execute(query, values)
    conn.commit()
    flash("Student added successfully.")
    return redirect(url_for('newstudent'))

@app.route('/viewstudent', methods=['GET'])
def viewstudent():
    cursor=conn.cursor()
    query="SELECT * FROM studentsdata"
    cursor.execute(query)
    tempdatalist=cursor.fetchall()
    finaldatalist=[]
    for sets in tempdatalist:
        list=[sets[0],sets[1], sets[2], sets[3], sets[5], sets[6]]
        binary_temp = base64.b64encode(sets[7])
        image_data = binary_temp.decode("UTF-8")
        list.append(image_data)
        finaldatalist.append(list)
    return render_template('/viewstudent.html', data=finaldatalist)

@app.route('/editdata', methods=['GET'])
def editdata():
    id = request.args.get('id')
    cursor=conn.cursor()
    query="SELECT * FROM studentsdata WHERE id=%s"
    cursor.execute(query,id)
    data=cursor.fetchone()
    return render_template('/edit.html', data=data)

@app.route('/updatedata', methods=['POST'])
def updatedata():
    cursor=conn.cursor()
    id=request.form['id']
    name = request.form['student_name']
    enrollment = request.form['student_enrollment']
    contact = request.form['student_contact']
    email = request.form['student_email']
    classroom = request.form['student_classroom']
    temp_image = request.files['student_image']
    query="UPDATE studentsdata SET name=%s, enrollment=%s, contact=%s, email=%s, classroom=%s WHERE id=%s"
    values=(name, enrollment, contact, email, classroom, id)
    cursor.execute(query, values)
    conn.commit()
    if temp_image:
        image = temp_image.read()
        query="UPDATE studentsdata SET image=%s WHERE id=%s"
        values=(image, id)
        cursor.execute(query,values)
        conn.commit()
    flash("Student details updated Successfully !!")
    return redirect(url_for('viewstudent'))

@app.route('/getid', methods = ['POST'])
def getid():
    global delid
    id = request.get_json()
    delid = str(id)
    return jsonify(id=id)

def getdelid():
    return delid

@app.route('/deletedata')
def deletedata():
    id = getdelid()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM studentsdata WHERE id=%s", (id))
    conn.commit()
    flash("Student details deleted successfully")
    return redirect(url_for('viewstudent'))
    
@app.route('/attendance')
def attendance():
    return render_template('/attendance.html')

@app.route('/markattendance', methods=['POST'])
def markattendance():
    
    # Storing HTML Face encodings -> html_image_codes
    try:
        classroom = request.form['class']    
    except:
        flash("Please Select the classroom")
        return redirect(url_for('attendance'))
    subject = request.form['subject']
    
    
    html_image = request.files['grpimage']
    image_stream = BytesIO(html_image.read())
    image = cv2.imdecode(np.frombuffer(image_stream.getvalue(), np.uint8), cv2.IMREAD_COLOR)
    rgbimg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print(type(rgbimg))
    face_locations = face_recognition.face_locations(rgbimg)
    print(len(face_locations))
    
    #----------------------------------------------------------------------------------------------
    # Original code 
    # html_image = request.files['grpimage']
    # image = html_image.read()
    # rgbimg = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # numpyimg = np.asarray(rgbimg)
    # face_locations = face_recognition.face_locations(numpyimg)
    #---------------------------------------------------------------------
    
    html_face_codes= face_recognition.face_encodings(image, face_locations)
    print(len(html_face_codes))

    if len(html_face_codes) == 0:
        flash("No Student Faces Detected")
        return redirect(url_for('attendance'))
    
    # Storing Database Face encodings -> db_image_codes

    cursor = conn.cursor()
    query="SELECT code, image FROM studentsdata WHERE classroom=%s"
    val=(classroom)
    cursor.execute(query, val)
    db_data = cursor.fetchall()
    db_image_codes = []
    db_codes = []
    
    for data in db_data:

        db_image = data[1]       

        image_array = np.frombuffer(db_image, dtype=np.uint8)   
        db_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR) 
        rgb_db_image = cv2.cvtColor(db_image, cv2.COLOR_BGR2RGB)
        db_image_encoding = face_recognition.face_encodings(rgb_db_image)
        for temp_encoding in db_image_encoding:
            db_image_codes.append(temp_encoding)
        db_codes.append(data[0])
    
    print("Number of HTML Faces :", len(html_face_codes))
    print("Number of DB Faces", len(db_image_codes))

    # final_codes contains the attendance codes
    final_codes = []
    
    for html_face_code in html_face_codes:
        distance = face_recognition.face_distance(db_image_codes, html_face_code)
        min_distance = min(distance)
        if min_distance < 0.6:
            index = distance.tolist().index(min_distance)
            if db_codes[index] not in final_codes:
                final_codes.append(db_codes[index])

    if len(final_codes) == 0:
        flash("No matching Student Faces found from class "+classroom)
        return redirect(url_for('attendance'))
    
    print("Matching faces number :", len(final_codes))

    present_data = []
    not_present_data = []

    cursor.execute("SELECT name, enrollment, code FROM studentsdata WHERE classroom=%s", val)

    alldata = cursor.fetchall()

    for data in alldata:
        if data[2] in final_codes:
            present_data.append(data)
        else:
            not_present_data.append(data)

    return render_template('/markattendance.html', present_data=present_data, not_present_data=not_present_data,classroom=classroom, subject=subject)

@app.route('/confirmattendance', methods=['POST'])
def confirmattendance():
    cursor = conn.cursor()
    present_data = request.form['present_data']
    present_data = ast.literal_eval(present_data)
    classroom = request.form['classroom']
    subject = request.form['subject']
    manualdata = request.form.getlist('manualattendance')
    for data in present_data:
        query = "INSERT INTO attendancedata (name, enrollment, classroom, subject, date, time, code) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        date = datetime.date.today()
        time = datetime.datetime.now().strftime("%H:%M:%S")
        val = (data[0], data[1], classroom, subject, date, time, data[2])
        cursor.execute(query, val)
        conn.commit()

    for code in manualdata:
        cursor.execute("SELECT name, enrollment FROM studentsdata WHERE code=%s",(code))
        data = cursor.fetchone()
        query = "INSERT INTO attendancedata (name, enrollment, classroom, subject, date, time, code) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        date = datetime.date.today()
        time = datetime.datetime.now().strftime("%H:%M:%S")
        val = (data[0], data[1], classroom, subject, date, time, code)
        cursor.execute(query, val)
        conn.commit()

    flash("Attendance Marked !!")
    return redirect(url_for('attendance'))

@app.route('/history')
def history():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendancedata")
    alldata = cursor.fetchall()
    return render_template('/history.html', alldata = alldata)

@app.route('/download')
def download_records():
    cursor = conn.cursor()
    cursor.execute("SELECT name, enrollment, classroom, subject, date, time FROM attendancedata")
    dataset = cursor.fetchall()

    names=[]
    enrollments=[]
    classrooms=[]
    subjects=[]
    dates=[]
    times=[]

    for data in dataset:
        names.append(data[0])
        enrollments.append(data[1])
        classrooms.append(data[2])
        subjects.append(data[3])
        temp = data[4].strftime("%d-%m-%Y")
        dates.append(temp)
        times.append(str(data[5]))

    finaldataset = {
        'Name' : names,
        'Enrollment' : enrollments,
        'Class' : classrooms,
        'Subject' : subjects,
        'Date' : dates,
        'Time' : times
    }

    dataframe = pd.DataFrame(finaldataset)
    dataframe.to_excel(r'static\attendance.xlsx', sheet_name='Attendance Records', index=False, engine='xlsxwriter')
    path = r'static/attendance.xlsx'
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)